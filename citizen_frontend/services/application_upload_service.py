from citizen_frontend.services.document_storage import S3Service


class ApplicationUploadService:
    def __init__(self):
        self.document_store = S3Service()

    def upload_application(self, application):
        self.document_store.store_file("path", application)
