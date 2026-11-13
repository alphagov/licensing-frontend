import uuid


class DataIntegrityError(Exception):
    pass


class DocumentDBError(Exception):
    pass


class LicenceLookupError(Exception):
    pass


class PDFGenerationGeneralError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.id = uuid.uuid4()


class PDFProviderUnavailableError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.id = uuid.uuid4()


class FormNotFoundException(Exception):
    pass


class FormNotPublishedException(Exception):
    pass
