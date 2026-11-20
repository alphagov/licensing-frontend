import pytest
from common.models.licence_application import SupportingDocument
from common.models.shared_models import SupportingDocumentDefinition
from conftest import (
    TEST_AUTHORITY,
    TEST_CUSTOMISATION_NO_FEE,
    TEST_LICENCE,
    TEST_LICENCE_INTERACTION,
    TEST_UUID,
)
from django.core.files.uploadedfile import SimpleUploadedFile

from citizen_frontend.exceptions import (
    DataIntegrityError,
    DocumentDBError,
    DocumentStorageError,
    LicenceSubmissionError,
)
from citizen_frontend.services.application_submission_service import ApplicationSubmissionService


@pytest.fixture
def mock_application_upload_service(mock_s3_service, mocker):
    service = ApplicationSubmissionService()
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


@pytest.mark.parametrize("error", [DataIntegrityError, DocumentDBError])
def test_application_upload_service_handles_application_licence_repository_errors(
    mock_application_upload_service, mock_s3, mock_licence_application_repo, error, mocker
):
    mocker.patch.object(
        mock_application_upload_service.licence_application_repository,
        "create_new_licence_application",
        side_effect=error,
    )

    mock_application = {
        "application_upload": SimpleUploadedFile(
            name="application.pdf", content_type="application/pdf", content=MOCK_PDF_CONTENT
        )
    }

    with pytest.raises(LicenceSubmissionError):
        mock_application_upload_service.handle_form_submission(
            files=mock_application,
            customisation=TEST_CUSTOMISATION_NO_FEE,
            email="mock_email",
            is_supporting_documents_online=True,
            authority=TEST_AUTHORITY,
            licence=TEST_LICENCE,
            interaction=TEST_LICENCE_INTERACTION,
        )


def test_application_upload_service_handles_document_storage_errors(
    mock_application_upload_service, mock_s3, mock_licence_application_repo, mocker
):
    mocker.patch.object(
        mock_application_upload_service.licence_application_repository,
        "create_new_licence_application",
        side_effect=DocumentStorageError,
    )

    mock_application = {
        "application_upload": SimpleUploadedFile(
            name="application.pdf", content_type="application/pdf", content=MOCK_PDF_CONTENT
        )
    }

    with pytest.raises(LicenceSubmissionError):
        mock_application_upload_service.handle_form_submission(
            files=mock_application,
            customisation=TEST_CUSTOMISATION_NO_FEE,
            email="mock_email",
            is_supporting_documents_online=True,
            authority=TEST_AUTHORITY,
            licence=TEST_LICENCE,
            interaction=TEST_LICENCE_INTERACTION,
        )


def test_handle_submission_creates_new_entry_in_licence_applications(
    mock_application_upload_service, mock_s3, mock_uuid, mocker
):

    supporting_docs = mocker.patch.object(
        mock_application_upload_service,
        "create_supporting_document_entry_objects",
        return_value=[
            SupportingDocument(definition=TEST_CUSTOMISATION_NO_FEE.supporting_document_definitions[0]),
            SupportingDocument(definition=TEST_CUSTOMISATION_NO_FEE.supporting_document_definitions[1]),
            SupportingDocument(definition=TEST_CUSTOMISATION_NO_FEE.supporting_document_definitions[2]),
        ],
    )

    files = {
        "application_upload": SimpleUploadedFile(
            name="application.pdf", content_type="application/pdf", content=MOCK_PDF_CONTENT
        ),
    }

    expected_application_document = mocker.patch.object(
        mock_application_upload_service,
        "create_application_document",
        return_value=SupportingDocument(
            _id=f"{TEST_UUID}/{files['application_upload'].name}",
            file_name=files["application_upload"].name,
            definition=SupportingDocumentDefinition(
                name="Completed form",
                description="Downloaded and filled PDF form",
                is_mandatory=True,
            ),
        ),
    )

    mock_application_upload_service.handle_form_submission(
        files=files,
        customisation=TEST_CUSTOMISATION_NO_FEE,
        email="mock_email",
        is_supporting_documents_online=True,
        authority=TEST_AUTHORITY,
        licence=TEST_LICENCE,
        interaction=TEST_LICENCE_INTERACTION,
    )

    mock_application_upload_service.licence_application_repository.create_new_licence_application.assert_called_with(
        email="mock_email",
        application_document=expected_application_document.return_value,
        supporting_documents=supporting_docs.return_value,
        authority=TEST_AUTHORITY,
        licence=TEST_LICENCE,
        customisation=TEST_CUSTOMISATION_NO_FEE,
        interaction=TEST_LICENCE_INTERACTION,
        is_supporting_documents_online=True,
    )


def test_handle_submission_creates_new_entry_in_licence_applications_no_fee_posted_documents():
    pass
