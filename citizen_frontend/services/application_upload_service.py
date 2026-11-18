import logging
import uuid

from common.models.interaction_customisation import Customisation
from common.models.licence_application import SupportingDocument
from common.models.shared_models import SupportingDocumentDefinition
from django.core.files.uploadedfile import SimpleUploadedFile

from citizen_frontend.repository.licence_application_repository import LicenceApplicationRepository
from citizen_frontend.services.document_storage import S3Service

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ApplicationUploadService:
    def __init__(self):
        self.document_store = S3Service()
        self.licence_application_repository = LicenceApplicationRepository()

    def handle_form_submission(self, files, customisation: Customisation, supporting_documents_online: bool):
        upload_id = str(uuid.uuid4())

        application_document = self.handle_application_form(
            application_file=files["application_upload"], upload_id=upload_id
        )

        if supporting_documents_online:
            # change this to dict so can get the upload number out
            supporting_documents = {key: file for key, file in files.items() if key.startswith("supporting_document_")}
            self.handle_supporting_documents(
                supporting_documents, upload_id, customisation, supporting_documents_online
            )

        application_reference = self.licence_application_repository.create_new_licence_application(application_document)
        return application_reference

    def handle_application_form(self, application_file, upload_id: str) -> SupportingDocument:
        application_document = self.create_application_document(application_file, upload_id)
        logger.info("Uploading application form")

        self.upload_document(document=application_file, path=application_document._id)

        return application_document

    def handle_supporting_documents(
        self, documents, upload_id: str, customisation: Customisation, supporting_document_online: bool
    ):
        logger.info("Uploading supporting documents")
        supporting_document_object_entries = self.create_supporting_document_entry_objects(
            files=documents,
            customisation=customisation,
            upload_id=upload_id,
            supporting_documents_online=supporting_document_online,
        )
        for _key, value in documents.items():
            self.upload_document(document=value, path=f"{upload_id}/{value.name}")

        return supporting_document_object_entries

    def upload_document(self, document: SimpleUploadedFile, path: str):
        self.document_store.store_file(path=path, file=document, content_type=document.content_type)

    def create_supporting_document_entry_objects(
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

    def create_application_document(self, application_file: SimpleUploadedFile, upload_id: str) -> SupportingDocument:
        return SupportingDocument(
            _id=f"{upload_id}/{application_file.name}",
            file_name=application_file.name,
            definition=SupportingDocumentDefinition(
                name="Completed form",
                description="Downloaded and filled PDF form",
                is_mandatory=True,
            ),
        )


# TODO we need to build out the correct number of supporting documents
#  with correct definitions as part of application object.
#  These need uploading first, take the path as the SupportingDocument.id
#  Create the service object, believe this can get most info from an interaction
