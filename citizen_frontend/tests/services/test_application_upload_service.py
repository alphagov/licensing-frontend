import pytest
from common.models.licence_application import SupportingDocument
from common.models.shared_models import SupportingDocumentDefinition
from conftest import TEST_AUTHORITY, TEST_CUSTOMISATION_NO_FEE, TEST_LICENCE, TEST_UUID
from django.core.files.uploadedfile import SimpleUploadedFile

from citizen_frontend.services.application_upload_service import ApplicationUploadService


@pytest.fixture
def mock_application_upload_service(mock_s3_service, mocker):
    service = ApplicationUploadService()
    mocker.patch.object(service, "licence_application_repository")
    yield service


MOCK_PDF_CONTENT = b"%PDF-1.4 fake pdf content"


def test_application_upload_service_uploads_submitted_forms_to_s3(
    mock_s3, mock_application_upload_service, mock_uuid, mock_s3_client
):
    mock_application = SimpleUploadedFile(
        name="application.pdf", content_type="application/pdf", content=MOCK_PDF_CONTENT
    )

    mock_application_upload_service.upload_document(mock_application, f"{TEST_UUID}/{mock_application.name}")

    file = mock_s3_client.get_object(
        Bucket="test-bucket",
        Key=f"{TEST_UUID}/{mock_application.name}",
    )
    assert file["Body"].read() == MOCK_PDF_CONTENT


def test_application_handles_supported_documents(mock_application_upload_service, mocker, mock_uuid):
    mocker.patch.object(mock_application_upload_service, "upload_document")
    mock_object_creation = mocker.patch.object(
        mock_application_upload_service, "create_supporting_document_entry_objects"
    )

    supporting_documents = {
        "supporting_document_0": SimpleUploadedFile(
            name="supporting_0.pdf", content_type="application/pdf", content=MOCK_PDF_CONTENT
        ),
        "supporting_document_1": SimpleUploadedFile(
            name="supporting_1.pdf", content_type="application/pdf", content=MOCK_PDF_CONTENT
        ),
    }

    mock_application_upload_service.handle_supporting_documents(
        supporting_documents, TEST_UUID, TEST_CUSTOMISATION_NO_FEE, True
    )

    mock_application_upload_service.upload_document.assert_has_calls(
        [
            mocker.call(
                document=supporting_documents["supporting_document_0"],
                path=f"{TEST_UUID}/{supporting_documents['supporting_document_0'].name}",
            ),
            mocker.call(
                document=supporting_documents["supporting_document_1"],
                path=f"{TEST_UUID}/{supporting_documents['supporting_document_1'].name}",
            ),
        ]
    )

    mock_object_creation.assert_called()


# def test_create_supporting_document_entry_objects(mock_application_upload_service, mock_s3):
#
#     supporting_documents = [
#         SimpleUploadedFile(name="supporting_0.pdf", content_type="application/pdf", content=MOCK_PDF_CONTENT),
#         SimpleUploadedFile(name="supporting_1.pdf", content_type="application/pdf", content=MOCK_PDF_CONTENT),
#     ]
#
#     expected = [
#         SupportingDocument(
#             id=f"{TEST_UUID}/{supporting_documents[0].name}",
#             file_name=supporting_documents[0].name,
#
#         )
#     ]


def test_create_application_document_returns_expected_object(mock_application_upload_service, mock_uuid):
    mock_application = SimpleUploadedFile(
        name="application.pdf", content_type="application/pdf", content=MOCK_PDF_CONTENT
    )

    expected_object = SupportingDocument(
        _id=f"{TEST_UUID}/{mock_application.name}",
        file_name=mock_application.name,
        definition=SupportingDocumentDefinition(
            name="Completed form",
            description="Downloaded and filled PDF form",
            is_mandatory=True,
        ),
    )

    actual = mock_application_upload_service.create_application_document(mock_application, TEST_UUID)
    assert actual._id == expected_object._id


def test_application_upload_service_virus_scans_files_before_uploading():
    pass


def test_application_upload_service_handles_s3_failures():
    pass


def skip_test_handle_submission_creates_new_entry_in_licence_applications_no_fee_online_documents(
    mock_application_upload_service, mock_s3
):
    files = {
        "application_upload": SimpleUploadedFile(
            name="application.pdf", content_type="application/pdf", content=MOCK_PDF_CONTENT
        ),
    }

    mock_application_upload_service.handle_form_submission(files, TEST_CUSTOMISATION_NO_FEE)

    mock_application_upload_service.licence_application_repository.create_new_licence_application.assert_called_with(
        email="mock_email",
        authority=TEST_AUTHORITY,
        licence=TEST_LICENCE,
        customisation=TEST_CUSTOMISATION_NO_FEE,
        supporting_documents=[],
    )


def test_handle_submission_creates_new_entry_in_licence_applications_no_fee_posted_documents():
    pass
