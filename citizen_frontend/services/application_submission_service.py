import logging
import uuid
from dataclasses import dataclass

from common.models.authority import Authority
from common.models.interaction_customisation import Customisation
from common.models.licence import Licence, LicenceInteraction
from common.models.licence_application import SupportingDocument
from common.models.shared_models import SupportingDocumentDefinition
from django.core.files.uploadedfile import SimpleUploadedFile

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


@dataclass
class ApplicationSubmission:
    files: dict[str, SimpleUploadedFile]
    email: str
    authority: Authority
    licence: Licence
    customisation: Customisation
    interaction: LicenceInteraction
    is_supporting_documents_online: bool


class ApplicationSubmissionService:
    def __init__(self, application):
        self.application = application
        self.document_store = S3Service()
        self.licence_application_repository = LicenceApplicationRepository()

    def submit_form(self):
        try:
            logger.info("Handling application submission")
            upload_id = str(uuid.uuid4())
            # TODO Would it be better to use a bson.ObjectId here to tie everything together
            #   if the document upload happens, but the database insert fails, we'd still be able to find
            #   the objects related to this application. or is it a case of one failure and done.
            #   is audit here to help handle this scenario.

            application_document = self._handle_application_form(
                application_file=self.application.files["application_upload"], upload_id=upload_id
            )

            supporting_documents_files = {
                key: file for key, file in self.application.files.items() if key.startswith("supporting_document_")
            }
            supporting_documents = self._handle_supporting_documents(
                supporting_documents_files,
                upload_id,
                self.application.customisation,
                self.application.is_supporting_documents_online,
            )

            application_reference = self.licence_application_repository.create_new_licence_application(
                application_submission=self.application,
                application_document=application_document,
                supporting_documents=supporting_documents,
            )
            return application_reference
        except (DataIntegrityError, DocumentDBError, DocumentStorageError) as e:
            # TODO What gets logged here, how do we link submission/application to user, email...?
            raise LicenceSubmissionError(f"Failed to submit application: {e.args}") from e

    def _handle_application_form(self, application_file, upload_id: str) -> SupportingDocument:
        application_document = self._create_application_document(application_file, upload_id)
        logger.info("Uploading application form")

        self._upload_document(document=application_file, path=application_document._id)

        return application_document

    def _handle_supporting_documents(
        self, documents, upload_id: str, customisation: Customisation, supporting_document_online: bool
    ):
        logger.info("Uploading supporting documents")
        supporting_document_object_entries = self._create_supporting_document_entry_objects(
            files=documents,
            customisation=customisation,
            upload_id=upload_id,
            supporting_documents_online=supporting_document_online,
        )
        for _key, value in documents.items():
            self._upload_document(document=value, path=f"{upload_id}/{value.name}")

        return supporting_document_object_entries

    def _upload_document(self, document: SimpleUploadedFile, path: str):
        self.document_store.store_file(path=path, file=document.file, content_type=document.content_type)

    def _create_supporting_document_entry_objects(
        self, files: dict[str, SimpleUploadedFile], customisation, upload_id: str, supporting_documents_online: bool
    ):

        if not supporting_documents_online:
            return [
                SupportingDocument(definition=supporting_document_definition)
                for supporting_document_definition in customisation.supporting_document_definitions
            ]

        supporting_document_entries = []

        for index, supporting_document_definition in enumerate(customisation.supporting_document_definitions):
            file = files.get("supporting_document_" + str(index))
            if file:
                entry = SupportingDocument(
                    _id=f"{upload_id}/{file.name}",
                    file_name=file.name,
                    definition=supporting_document_definition,
                )
            else:
                entry = SupportingDocument(definition=supporting_document_definition)
            supporting_document_entries.append(entry)

        return supporting_document_entries

    def _create_application_document(self, application_file: SimpleUploadedFile, upload_id: str) -> SupportingDocument:
        return SupportingDocument(
            _id=f"{upload_id}/{application_file.name}",
            file_name=application_file.name,
            definition=SupportingDocumentDefinition(
                name="Completed form",
                description="Downloaded and filled PDF form",
                is_mandatory=True,
            ),
        )
