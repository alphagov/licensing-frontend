import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from citizen_frontend.services.application_upload_service import ApplicationUploadService


@pytest.fixture
def mock_application_upload_service(mocker, mock_s3_service):
    service = ApplicationUploadService()
    # TODO don't even need to use mock_s3_service here, only useful if we want to do verify the actual upload
    mocker.patch.object(service, "document_store", return_value=mock_s3_service)
    yield service


def test_application_upload_service_uploads_submitted_forms_to_s3(mock_application_upload_service):
    mock_application = SimpleUploadedFile(
        name="application.pdf", content_type="application/pdf", content=b"%PDF-1.4 fake pdf content"
    )

    mock_application_upload_service.upload_application(mock_application)

    mock_application_upload_service.document_store.store_file.assert_called_with(
        path="", file=io.BytesIO(mock_application.read()), content_type=mock_application.content_type
    )


def test_application_upload_service_verifies_postal_supported_documents():
    pass


def test_application_upload_service_virus_scans_files_before_uploading():
    pass


def test_application_upload_service_handles_s3_failures():
    pass
