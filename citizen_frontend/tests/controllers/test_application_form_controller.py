from copy import deepcopy

import pytest
from botocore.exceptions import ClientError
from conftest import TEST_AUTHORITY, TEST_CUSTOMISATION_NO_FEE, TEST_LICENCE, TEST_UUID
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse


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


def test_submit_uploads_application_documents_to_s3_when_postal_is_not_allowed(
    mock_s3,
    mock_s3_client,
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

    application_form = mock_s3_client.get_object(Bucket="test-bucket", Key=f"{TEST_UUID}/application_upload.pdf")

    supporting_document = mock_s3_client.get_object(Bucket="test-bucket", Key=f"{TEST_UUID}/supporting_document_0.pdf")

    assert application_form["Body"].read() == expected_content
    assert supporting_document["Body"].read() == expected_content


def test_submit_does_not_upload_supporting_documents_to_s3_when_postal_is_allowed_will_post_checked_mandatory_document(
    mock_s3,
    mock_s3_client,
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

    application_form = mock_s3_client.get_object(Bucket="test-bucket", Key=f"{TEST_UUID}/application_upload.pdf")

    assert application_form["Body"].read() == expected_content

    with pytest.raises(ClientError):
        mock_s3_client.get_object(Bucket="test-bucket", Key=f"{TEST_UUID}/supporting_document_0.pdf")

    # TODO, research what happens when is_postal allowed, and will submit via post is checked
    #   Does the application still creat an entry for them, or does it just exit user journey?...
    #  looks like only the PDF is uploaded AND only supporting documentation is allowed via post

    #  would be nice to be able to dynamically disable the supporting document uploads using HTMX here


def test_submit_uploads_supporting_documents_to_s3_when_postal_is_allowed_will_post_not_checked_mandatory_document(
    mock_s3,
    mock_s3_client,
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

    application_form = mock_s3_client.get_object(Bucket="test-bucket", Key=f"{TEST_UUID}/application_upload.pdf")
    supporting_document = mock_s3_client.get_object(Bucket="test-bucket", Key=f"{TEST_UUID}/supporting_document_0.pdf")

    assert application_form["Body"].read() == expected_content
    assert supporting_document["Body"].read() == expected_content
