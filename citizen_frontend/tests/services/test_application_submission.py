from copy import deepcopy
from datetime import datetime, timedelta

import pytest
from common.models.licence_application import SupportingDocument
from common.models.shared_models import SupportingDocumentDefinition
from conftest import (
    TEST_AUTHORITY,
    TEST_CUSTOMISATION_NO_FEE,
    TEST_LICENCE,
    TEST_UUID,
)
from django.core.files.uploadedfile import SimpleUploadedFile
from freezegun import freeze_time

from citizen_frontend.exceptions import (
    DataIntegrityError,
    DocumentDBError,
    DocumentStorageError,
    LicenceSubmissionError,
)
from citizen_frontend.services.application_submission_service import Application, ApplicationSubmission

MOCK_PDF_CONTENT = b"%PDF-1.4 fake pdf content"

VALID_FORM_SUBMISSION = {
    "email": "anemail@example.com",
    "confirmation_email": "anemail@example.com",
    "application_upload": SimpleUploadedFile(
        name="application_upload.pdf", content_type="application/pdf", content=MOCK_PDF_CONTENT
    ),
    "supporting_document_0": SimpleUploadedFile(
        name="supporting_document_0.pdf", content_type="application/pdf", content=MOCK_PDF_CONTENT
    ),
    "declaration": "on",
}


@pytest.fixture
def mock_application():
    yield Application(
        email=VALID_FORM_SUBMISSION["email"],
        files={
            "application_upload": SimpleUploadedFile(
                name="application_upload.pdf", content_type="application/pdf", content=MOCK_PDF_CONTENT
            ),
            "supporting_document_0": SimpleUploadedFile(
                name="supporting_document_0.pdf", content_type="application/pdf", content=MOCK_PDF_CONTENT
            ),
        },
        licence=TEST_LICENCE,
        authority=TEST_AUTHORITY,
        customisation=TEST_CUSTOMISATION_NO_FEE,
        interaction=TEST_LICENCE.licence_interactions[0],
        are_supporting_documents_online=False,
    )


@pytest.fixture
def application_submission(mock_s3_service, mocker, mock_application, mock_uuid):
    service = ApplicationSubmission(mock_application)
    mocker.patch.object(service, "licence_application_repository")
    yield service


@pytest.fixture
def ni_application_submission(mock_application, mock_uuid, mocker, mock_s3_service):
    ni_application = deepcopy(mock_application)
    ni_application.authority.countries[0] = "NI"
    service = ApplicationSubmission(ni_application)

    mocker.patch.object(service, "licence_application_repository")
    yield service


def test_application_upload_service_uploads_submitted_forms_to_s3(
    mock_s3, application_submission, mock_uuid, mock_s3_client
):
    mock_file_upload = SimpleUploadedFile(
        name="application.pdf", content_type="application/pdf", content=MOCK_PDF_CONTENT
    )

    application_submission._upload_document(mock_file_upload, f"{TEST_UUID}/{mock_file_upload.name}")

    file = mock_s3_client.get_object(
        Bucket="test-bucket",
        Key=f"{TEST_UUID}/{mock_file_upload.name}",
    )
    assert file["Body"].read() == MOCK_PDF_CONTENT


def test_application_handles_supported_documents(application_submission, mocker, mock_uuid):
    mocker.patch.object(application_submission, "_upload_document")
    mock_object_creation = mocker.patch.object(application_submission, "_create_supporting_document_entry_objects")

    application_submission._upload_supporting_documents()

    application_submission._upload_document.assert_has_calls(
        [
            mocker.call(
                document=application_submission.supporting_document_files["supporting_document_0"],
                path=f"{TEST_UUID}/{application_submission.supporting_document_files['supporting_document_0'].name}",
            )
        ]
    )

    mock_object_creation.assert_called()


def test_create_application_document_returns_expected_object(application_submission, mock_uuid):
    mock_file_upload = SimpleUploadedFile(
        name="application.pdf", content_type="application/pdf", content=MOCK_PDF_CONTENT
    )

    expected_object = SupportingDocument(
        _id=f"{TEST_UUID}/{mock_file_upload.name}",
        file_name=mock_file_upload.name,
        definition=SupportingDocumentDefinition(
            name="Completed form",
            description="Downloaded and filled PDF form",
            is_mandatory=True,
        ),
    )

    actual = application_submission._create_application_document(mock_file_upload)
    assert actual._id == expected_object._id


def test_application_upload_service_virus_scans_files_before_uploading():
    # TODO separate ticket
    pass


@pytest.mark.parametrize("error", [DataIntegrityError, DocumentDBError])
def test_application_upload_service_handles_application_licence_repository_errors(
    application_submission, mock_s3, mock_licence_application_repo, error, mocker
):
    mocker.patch.object(
        application_submission.licence_application_repository,
        "create_new_licence_application",
        side_effect=error,
    )

    with pytest.raises(LicenceSubmissionError):
        application_submission.submit()


def test_application_upload_service_handles_document_storage_errors(
    application_submission, mock_s3, mock_licence_application_repo, mocker
):
    mocker.patch.object(
        application_submission.licence_application_repository,
        "create_new_licence_application",
        side_effect=DocumentStorageError,
    )

    with pytest.raises(LicenceSubmissionError):
        application_submission.submit()


def test_handle_submission_creates_new_entry_in_licence_applications(
    application_submission, mock_s3, mock_uuid, mocker
):

    application_submission.application.are_supporting_documents_online = True

    supporting_docs = mocker.patch.object(
        application_submission,
        "_create_supporting_document_entry_objects",
        return_value=[
            SupportingDocument(definition=TEST_CUSTOMISATION_NO_FEE.supporting_document_definitions[0]),
            SupportingDocument(definition=TEST_CUSTOMISATION_NO_FEE.supporting_document_definitions[1]),
            SupportingDocument(definition=TEST_CUSTOMISATION_NO_FEE.supporting_document_definitions[2]),
        ],
    )

    expected_application_document = mocker.patch.object(
        application_submission,
        "_create_application_document",
        return_value=SupportingDocument(
            _id=f"{TEST_UUID}/{application_submission.application.files['application_upload'].name}",
            file_name=application_submission.application.files["application_upload"].name,
            definition=SupportingDocumentDefinition(
                name="Completed form",
                description="Downloaded and filled PDF form",
                is_mandatory=True,
            ),
        ),
    )

    application_submission.submit()

    application_submission.licence_application_repository.create_new_licence_application.assert_called_with(
        application_document=expected_application_document.return_value,
        supporting_documents=supporting_docs.return_value,
        application_submission=application_submission.application,
    )


def test_handle_submission_creates_new_entry_in_licence_applications_no_fee_posted_documents():
    pass


def test_calculate_expected_processing_date_only_working_days_false(application_submission):
    application_submission.application.customisation.number_of_days_to_process = 20
    application_submission.application.customisation.is_processing_days_working_days = False
    expected_processing_date = datetime.today() + timedelta(days=20)

    actual = application_submission._calculate_expected_processing_date()
    assert actual == expected_processing_date.date()


@freeze_time("2026-11-27")
def test_calculate_expected_processing_date_working_days_true_handles_weekends(application_submission):
    application_submission.application.customisation.number_of_days_to_process = 2
    application_submission.application.customisation.is_processing_days_working_days = True
    application_submission.country = "England"
    expected_processing_date = datetime.fromisoformat("2026-12-01")

    actual = application_submission._calculate_expected_processing_date()

    assert actual == expected_processing_date.date()


@freeze_time("2026-11-08")
def test_calculate_expected_processing_date_5_working_days_sunday_submission_expected_processing_date_is_week_monday(
    application_submission,
):
    application_submission.application.customisation.number_of_days_to_process = 5
    application_submission.application.customisation.is_processing_days_working_days = True
    application_submission.country = "England"

    expected_date = datetime(2026, 11, 16).date()

    actual = application_submission._calculate_expected_processing_date()

    assert actual == expected_date


@freeze_time("2026-12-24")
def test_calculate_expected_processing_days_handles_holidays(application_submission):
    application_submission.application.customisation.number_of_days_to_process = 2
    application_submission.application.customisation.is_processing_days_working_days = True
    application_submission.country = "England"

    expected_date = datetime(2026, 12, 30).date()

    actual = application_submission._calculate_expected_processing_date()
    assert actual == expected_date


@freeze_time("2027-03-16")
@pytest.mark.parametrize(
    "country, expected_date, application_submission_to_test",
    [("England", "2027-03-18", "application_submission"), ("NI", "2027-03-19", "ni_application_submission")],
)
def test_calculate_expected_processing_date_handles_division_holidays(
    request, application_submission_to_test, country, expected_date
):
    application_submission_under_test = request.getfixturevalue(application_submission_to_test)
    application_submission_under_test.application.customisation.number_of_days_to_process = 2
    application_submission_under_test.application.customisation.is_processing_days_working_days = True

    expected_date = datetime.fromisoformat(expected_date).date()

    actual = application_submission_under_test._calculate_expected_processing_date()
    assert actual == expected_date
