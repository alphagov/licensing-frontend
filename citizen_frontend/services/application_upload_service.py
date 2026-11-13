import uuid

from django.core.files.uploadedfile import SimpleUploadedFile

from citizen_frontend.services.document_storage import S3Service


class ApplicationUploadService:
    def __init__(self):
        self.document_store = S3Service()

    def upload_application(self, application: SimpleUploadedFile):
        path = f"{str(uuid.uuid4())}/{application.name}"

        self.document_store.store_file(path=path, file=application, content_type=application.content_type)
