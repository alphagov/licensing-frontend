import pytest
from conftest import TEST_UUID
from django.core.files.uploadedfile import SimpleUploadedFile

from citizen_frontend.services.application_upload_service import ApplicationUploadService


@pytest.fixture
def mock_application_upload_service(mock_s3_service):
    service = ApplicationUploadService()
    yield service


def test_application_upload_service_uploads_submitted_forms_to_s3(
    mock_s3, mock_application_upload_service, mock_uuid, mock_s3_client
):
    expected_content = b"%PDF-1.4 fake pdf content"
    mock_application = SimpleUploadedFile(
        name="application.pdf", content_type="application/pdf", content=expected_content
    )

    mock_application_upload_service.upload_application(mock_application)

    file = mock_s3_client.get_object(
        Bucket="test-bucket",
        Key=f"{TEST_UUID}/{mock_application.name}",
    )
    assert file["Body"].read() == expected_content


def test_application_upload_service_verifies_postal_supported_documents():
    pass


def test_application_upload_service_virus_scans_files_before_uploading():
    pass


def test_application_upload_service_handles_s3_failures():
    pass
