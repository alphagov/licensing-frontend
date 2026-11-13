import uuid

from django.core.files.uploadedfile import SimpleUploadedFile

from citizen_frontend.services.document_storage import S3Service


class ApplicationUploadService:
    def __init__(self):
        self.document_store = S3Service()

    def handle_supporting_documents(self, documents):
        for document in documents:
            self.upload_document(document=document)

    def upload_document(self, document: SimpleUploadedFile):
        path = f"{str(uuid.uuid4())}/{document.name}"

        self.document_store.store_file(path=path, file=document, content_type=document.content_type)
