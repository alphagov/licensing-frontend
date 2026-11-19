from copy import deepcopy

import pytest
from conftest import TEST_AUTHORITY, TEST_CUSTOMISATION_NO_FEE, TEST_LICENCE, TEST_OBJECT_ID, TEST_UUID
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from citizen_frontend.exceptions import DocumentStorageError
from citizen_frontend.services.application_submission_service import ApplicationSubmissionService


@pytest.fixture
def submit_url_path():
    def _url(**overrides) -> str:
        defaults = {
            "licence_slug": TEST_LICENCE.url_slug,
            "authority_slug": TEST_AUTHORITY.url_slug,
            "interaction_id": "apply",
            "interaction_sub_id": TEST_LICENCE.licence_interactions[0].interaction_sub_id,
        }

        merged_kwargs = {**defaults, **overrides}
        return reverse("submit", kwargs=merged_kwargs)

    return _url


@pytest.fixture
def application_upload_service(mock_s3, mock_s3_client, mock_licence_application_repo):
    service = ApplicationSubmissionService()
    yield service


@pytest.fixture
def session_client(client, settings):
    settings.SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    return client


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


def test_submit_uploads_application_documents_to_s3_when_postal_is_not_allowed(
    application_upload_service,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_no_fee,
    submit_url_path,
    mock_uuid,
    session_client,
):
    session_client.post(submit_url_path(), data=VALID_FORM_SUBMISSION)

    application_form = application_upload_service.document_store.get_file(key=f"{TEST_UUID}/application_upload.pdf")
    supporting_document = application_upload_service.document_store.get_file(
        key=f"{TEST_UUID}/supporting_document_0.pdf"
    )

    assert application_form.read() == MOCK_PDF_CONTENT
    assert supporting_document.read() == MOCK_PDF_CONTENT


def test_submit_does_not_upload_supporting_documents_to_s3_when_postal_is_allowed_will_post_checked_mandatory_document(
    application_upload_service,
    mock_uuid,
    session_client,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_no_fee,
    submit_url_path,
):
    postal_allowed_free_customisation = deepcopy(TEST_CUSTOMISATION_NO_FEE)
    postal_allowed_free_customisation.is_postal_allowed = True

    mock_find_published_customisation_with_no_fee.return_value = postal_allowed_free_customisation

    session_client.post(
        submit_url_path(),
        data={
            "email": "anemail@example.com",
            "confirmation_email": "anemail@example.com",
            "application_upload": SimpleUploadedFile(
                name="application_upload.pdf", content_type="application/pdf", content=MOCK_PDF_CONTENT
            ),
            "declaration": "on",
            "will_submit_by_post": "on",
        },
    )

    application_form = application_upload_service.document_store.get_file(key=f"{TEST_UUID}/application_upload.pdf")

    assert application_form.read() == MOCK_PDF_CONTENT

    # Raise error because object does not exist.
    with pytest.raises(DocumentStorageError) as e:
        application_upload_service.document_store.get_file(key=f"{TEST_UUID}/supporting_document_0.pdf")

    assert e.value.args[0] == "Failed to get file from S3."

    # TODO, research what happens when is_postal allowed, and will submit via post is checked
    #   Does the application still creat an entry for them, or does it just exit user journey?...
    #  looks like only the PDF is uploaded AND only supporting documentation is allowed via post

    #  would be nice to be able to dynamically disable the supporting document uploads using HTMX here


def test_submit_uploads_supporting_documents_to_s3_when_postal_is_allowed_will_post_not_checked_mandatory_document(
    application_upload_service,
    mock_uuid,
    session_client,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_no_fee,
    submit_url_path,
):
    postal_allowed_free_customisation = deepcopy(TEST_CUSTOMISATION_NO_FEE)
    postal_allowed_free_customisation.is_postal_allowed = True

    session_client.post(
        submit_url_path(),
        data={
            "email": "anemail@example.com",
            "confirmation_email": "anemail@example.com",
            "application_upload": SimpleUploadedFile(
                name="application_upload.pdf", content_type="application/pdf", content=MOCK_PDF_CONTENT
            ),
            "supporting_document_0": SimpleUploadedFile(
                name="supporting_document_0.pdf", content_type="application/pdf", content=MOCK_PDF_CONTENT
            ),
            "declaration": "on",
            "will_submit_by_post": "off",
        },
    )

    application_form = application_upload_service.document_store.get_file(key=f"{TEST_UUID}/application_upload.pdf")
    supporting_document = application_upload_service.document_store.get_file(
        key=f"{TEST_UUID}/supporting_document_0.pdf"
    )

    assert application_form.read() == MOCK_PDF_CONTENT
    assert supporting_document.read() == MOCK_PDF_CONTENT


def test_submit_handles_document_storage_failures_throws_500_response(
    session_client,
    mocker,
    submit_url_path,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_no_fee,
):
    mock_call = mocker.patch(
        "citizen_frontend.controllers.application_form.ApplicationSubmissionService.handle_form_submission"
    )
    mock_call.side_effect = DocumentStorageError("Failed to upload document")

    response = session_client.post(
        submit_url_path(),
        data={
            "email": "anemail@example.com",
            "confirmation_email": "anemail@example.com",
            "application_upload": SimpleUploadedFile(
                name="application_upload.pdf", content_type="application/pdf", content=MOCK_PDF_CONTENT
            ),
            "supporting_document_0": SimpleUploadedFile(
                name="supporting_document_0.pdf", content_type="application/pdf", content=MOCK_PDF_CONTENT
            ),
            "declaration": "on",
            "will_submit_by_post": "off",
        },
    )

    assert response.status_code == 500


def test_submit_writes_new_application_reference_to_session_on_successful_submission(
    session_client,
    mocker,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_no_fee,
    submit_url_path,
):
    mocker.patch(
        "citizen_frontend.controllers.application_form.ApplicationSubmissionService.handle_form_submission"
    ).return_value = str(TEST_OBJECT_ID)

    session_client.post(
        submit_url_path(),
        data={
            "email": "anemail@example.com",
            "confirmation_email": "anemail@example.com",
            "application_upload": SimpleUploadedFile(
                name="application_upload.pdf", content_type="application/pdf", content=MOCK_PDF_CONTENT
            ),
            "supporting_document_0": SimpleUploadedFile(
                name="supporting_document_0.pdf", content_type="application/pdf", content=MOCK_PDF_CONTENT
            ),
            "supporting_document_1": SimpleUploadedFile(
                name="supporting_document_1.pdf", content_type="application/pdf", content=MOCK_PDF_CONTENT
            ),
            "supporting_document_2": SimpleUploadedFile(
                name="supporting_document_1.pdf", content_type="application/pdf", content=MOCK_PDF_CONTENT
            ),
            "declaration": "on",
        },
    )

    assert str(TEST_OBJECT_ID) in session_client.session["applicationReferenceNumbers"]
