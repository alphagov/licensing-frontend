import pytest
from conftest import TEST_AUTHORITY, TEST_LICENCE, TEST_UUID
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


def test_submit_uploads_application_documents_to_s3(
    mock_s3_service,
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
