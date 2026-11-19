from copy import deepcopy

import pytest
from conftest import TEST_AUTHORITY, TEST_CUSTOMISATION_NO_FEE, TEST_LICENCE, TEST_UUID
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from citizen_frontend.exceptions import DocumentStorageError
from citizen_frontend.services.application_upload_service import ApplicationUploadService


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
def store_service(mock_s3, mock_s3_client):
    service = ApplicationUploadService()
    yield service


def test_submit_uploads_application_documents_to_s3_when_postal_is_not_allowed(
    store_service,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_no_fee,
    submit_url_path,
    mock_uuid,
    client,
):
    expected_content = b"%PDF-1.4 fake pdf content"
    client.post(
        submit_url_path(),
        data={
            "email": "anemail@example.com",
            "confirmation_email": "anemail@example.com",
            "application_upload": SimpleUploadedFile(
                name="application_upload.pdf", content_type="application/pdf", content=expected_content
            ),
            "supporting_document_0": SimpleUploadedFile(
                name="supporting_document_0.pdf", content_type="application/pdf", content=expected_content
            ),
            "declaration": "on",
        },
    )

    application_form = store_service.document_store.get_file(key=f"{TEST_UUID}/application_upload.pdf")
    supporting_document = store_service.document_store.get_file(key=f"{TEST_UUID}/supporting_document_0.pdf")

    assert application_form.read() == expected_content
    assert supporting_document.read() == expected_content


def test_submit_does_not_upload_supporting_documents_to_s3_when_postal_is_allowed_will_post_checked_mandatory_document(
    store_service,
    mock_uuid,
    client,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_no_fee,
    submit_url_path,
):
    postal_allowed_free_customisation = deepcopy(TEST_CUSTOMISATION_NO_FEE)
    postal_allowed_free_customisation.is_postal_allowed = True

    mock_find_published_customisation_with_no_fee.return_value = postal_allowed_free_customisation

    expected_content = b"%PDF-1.4 fake pdf content"
    client.post(
        submit_url_path(),
        data={
            "email": "anemail@example.com",
            "confirmation_email": "anemail@example.com",
            "application_upload": SimpleUploadedFile(
                name="application_upload.pdf", content_type="application/pdf", content=expected_content
            ),
            "declaration": "on",
            "will_submit_by_post": "on",
        },
    )

    application_form = store_service.document_store.get_file(key=f"{TEST_UUID}/application_upload.pdf")

    assert application_form.read() == expected_content

    # Raise error because object does not exist.
    with pytest.raises(DocumentStorageError):
        store_service.document_store.get_file(key=f"{TEST_UUID}/supporting_document_0.pdf")

    # TODO, research what happens when is_postal allowed, and will submit via post is checked
    #   Does the application still creat an entry for them, or does it just exit user journey?...
    #  looks like only the PDF is uploaded AND only supporting documentation is allowed via post

    #  would be nice to be able to dynamically disable the supporting document uploads using HTMX here


def test_submit_uploads_supporting_documents_to_s3_when_postal_is_allowed_will_post_not_checked_mandatory_document(
    store_service,
    mock_uuid,
    client,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_no_fee,
    submit_url_path,
):
    postal_allowed_free_customisation = deepcopy(TEST_CUSTOMISATION_NO_FEE)
    postal_allowed_free_customisation.is_postal_allowed = True

    expected_content = b"%PDF-1.4 fake pdf content"
    client.post(
        submit_url_path(),
        data={
            "email": "anemail@example.com",
            "confirmation_email": "anemail@example.com",
            "application_upload": SimpleUploadedFile(
                name="application_upload.pdf", content_type="application/pdf", content=expected_content
            ),
            "supporting_document_0": SimpleUploadedFile(
                name="supporting_document_0.pdf", content_type="application/pdf", content=expected_content
            ),
            "declaration": "on",
            "will_submit_by_post": "off",
        },
    )

    application_form = store_service.document_store.get_file(key=f"{TEST_UUID}/application_upload.pdf")
    supporting_document = store_service.document_store.get_file(key=f"{TEST_UUID}/supporting_document_0.pdf")

    assert application_form.read() == expected_content
    assert supporting_document.read() == expected_content


def test_submit_handles_document_storage_failures_throws_500_question(
    client,
    mocker,
    submit_url_path,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_no_fee,
):
    mock_call = mocker.patch(
        "citizen_frontend.controllers.application_form.ApplicationUploadService.handle_form_submission"
    )
    mock_call.side_effect = DocumentStorageError("Failed to upload document")

    expected_content = b"%PDF-1.4 fake pdf content"
    response = client.post(
        submit_url_path(),
        data={
            "email": "anemail@example.com",
            "confirmation_email": "anemail@example.com",
            "application_upload": SimpleUploadedFile(
                name="application_upload.pdf", content_type="application/pdf", content=expected_content
            ),
            "supporting_document_0": SimpleUploadedFile(
                name="supporting_document_0.pdf", content_type="application/pdf", content=expected_content
            ),
            "declaration": "on",
        },
    )

    assert response.status_code == 500
