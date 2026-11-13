import logging
import uuid

from django.core.files.uploadedfile import SimpleUploadedFile

from citizen_frontend.services.document_storage import S3Service

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ApplicationUploadService:
    def __init__(self):
        self.document_store = S3Service()

    def handle_form_submission(self, request_files):
        self.upload_document(request_files["application_upload"])

        supporting_documents = [file for key, file in request_files.items() if key.startswith("supporting_document_")]
        self.handle_supporting_documents(supporting_documents)

    def handle_supporting_documents(self, documents):
        logger.info("Uploading supporting documents")
        for document in documents:
            self.upload_document(document=document)

    def upload_document(self, document: SimpleUploadedFile):
        path = f"{str(uuid.uuid4())}/{document.name}"

        self.document_store.store_file(path=path, file=document, content_type=document.content_type)
