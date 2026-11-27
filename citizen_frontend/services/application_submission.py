import datetime
import logging
import uuid
from dataclasses import dataclass

from common.enums.countries import Countries
from common.models.authority import Authority
from common.models.interaction_customisation import Customisation
from common.models.licence import Licence, LicenceInteraction
from common.models.licence_application import SupportingDocument
from common.models.shared_models import SupportingDocumentDefinition
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from govuk_bank_holidays.bank_holidays import BankHolidays

from citizen_frontend.exceptions import (
    DataIntegrityError,
    DocumentDBError,
    DocumentStorageError,
    LicenceSubmissionError,
)
from citizen_frontend.repository.licence_application_repository import LicenceApplicationRepository
from citizen_frontend.services.document_storage import S3Service

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# TODO do we squash these two objects together...?
#  No this is the input object
@dataclass
class Application:
    files: dict[str, SimpleUploadedFile]
    email: str
    authority: Authority
    licence: Licence
    customisation: Customisation
    interaction: LicenceInteraction
    are_supporting_documents_online: bool


class ApplicationSubmission:
    def __init__(self, application):
        self.application = application
        self.upload_id = str(uuid.uuid4())
        self.supporting_document_files = {
            key: file for key, file in self.application.files.items() if key.startswith("supporting_document_")
        }
        self.divisions = {
            Countries.ENGLAND.value: "england-and-wales",
            Countries.NORTHERN_IRELAND.value: "northern-ireland",
            Countries.WALES.value: "england-and-wales",
            Countries.SCOTLAND.value: "scotland",
        }
        self.country = (
            self.application.authority.countries[0] if self.application.authority.countries else Countries.ENGLAND.value
        )
        self.bank_holidays = BankHolidays()
        self.holidays = self._set_holidays()
        self.expected_processing_date = self._calculate_expected_processing_date()
        self.document_store = S3Service()
        self.licence_application_repository = LicenceApplicationRepository()

    def submit(self) -> str:
        try:
            logger.info("Handling application submission")

            application_document = self._upload_application_form(
                application_file=self.application.files["application_upload"]
            )

            supporting_documents = self._upload_supporting_documents()

            application_reference = self.licence_application_repository.create_new_licence_application(
                application_submission=self.application,
                application_document=application_document,
                supporting_documents=supporting_documents,
                expected_processing_date=self.expected_processing_date,
            )
            return application_reference
        except (DataIntegrityError, DocumentDBError, DocumentStorageError) as e:
            # TODO What gets logged here, how do we link submission/application to user, email...?
            raise LicenceSubmissionError(f"Failed to submit application: {e.args}") from e

    def _upload_application_form(self, application_file) -> SupportingDocument:
        application_document = self._create_application_document(application_file)
        logger.info("Uploading application form")

        self._upload_document(document=application_file, path=application_document._id)

        return application_document

    def _upload_supporting_documents(
        self,
    ) -> list[SupportingDocument]:

        logger.info("Uploading supporting documents")
        supporting_document_object_entries = self._create_supporting_document_entry_objects()

        for _key, value in self.supporting_document_files.items():
            self._upload_document(document=value, path=f"{self.upload_id}/{value.name}")

        return supporting_document_object_entries

    def _upload_document(self, document: SimpleUploadedFile, path: str):
        self.document_store.store_file(path=path, file=document.file, content_type=document.content_type)

    def _create_supporting_document_entry_objects(self) -> list[SupportingDocument]:

        if not self.application.are_supporting_documents_online:
            return [
                SupportingDocument(definition=supporting_document_definition)
                for supporting_document_definition in self.application.customisation.supporting_document_definitions
            ]

        supporting_document_entries = []

        for index, supporting_document_definition in enumerate(
            self.application.customisation.supporting_document_definitions
        ):
            file = self.supporting_document_files.get("supporting_document_" + str(index))
            if file:
                entry = SupportingDocument(
                    _id=f"{self.upload_id}/{file.name}",
                    file_name=file.name,
                    definition=supporting_document_definition,
                )
            else:
                entry = SupportingDocument(definition=supporting_document_definition)
            supporting_document_entries.append(entry)

        return supporting_document_entries

    def _create_application_document(self, application_file: SimpleUploadedFile) -> SupportingDocument:
        return SupportingDocument(
            _id=f"{self.upload_id}/{application_file.name}",
            file_name=application_file.name,
            definition=SupportingDocumentDefinition(
                name="Completed form",
                description="Downloaded and filled PDF form",
                is_mandatory=True,
            ),
        )

    # TODO these should probably live on the interaction customisation model
    def _calculate_expected_processing_date(
        self,
    ) -> datetime.date:

        processing_days = (
            self.application.customisation.number_of_days_to_process
            if self.application.customisation.number_of_days_to_process
            else 30
        )
        expected_date = timezone.now().date()

        if not self.application.customisation.is_processing_days_working_days:
            return expected_date + datetime.timedelta(days=processing_days)

        start_day = datetime.date.weekday(expected_date)
        is_weekend_start = start_day >= 5

        if is_weekend_start:
            processing_days += 2 if start_day == 5 else 1

        days_added = 0

        while days_added < processing_days:
            expected_date += datetime.timedelta(days=1)

            is_weekend = datetime.date.weekday(expected_date) >= 5
            is_holiday = expected_date in self.holidays

            if not is_weekend and not is_holiday:
                days_added += 1

        return expected_date

    def _set_holidays(self):
        return {holiday["date"] for holiday in self.bank_holidays.get_holidays(self.divisions.get(self.country))}
