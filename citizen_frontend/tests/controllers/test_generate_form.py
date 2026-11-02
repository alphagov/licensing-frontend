import pytest
from conftest import TEST_AUTHORITY, TEST_LICENCE
from django.http import FileResponse
from django.urls import reverse

from citizen_frontend.services import licence_lookup_service


@pytest.fixture
def generate_form_url():
    def _url(**overrides) -> str:
        defaults = {
            "licence_slug": TEST_LICENCE.url_slug,
            "authority_slug": TEST_AUTHORITY.url_slug,
            "licence_code": TEST_LICENCE.licence_code,
            "interaction_id": TEST_LICENCE.licence_interactions[0].interaction_id,
            "interaction_sub_id": TEST_LICENCE.licence_interactions[0].interaction_sub_id,
        }

        merged_kwargs = {**defaults, **overrides}
        return reverse("generate_form", kwargs=merged_kwargs)

    return _url


@pytest.fixture
def mock_lookup_form_details(mocker):
    yield mocker.patch.object(licence_lookup_service, "lookup_form_details")


def test_generate_form_returns_file_response(
    client, generate_form_url, mock_authority_repository, mock_licence_repository
):
    response = client.get(generate_form_url())

    mock_authority_repository.find_authority_by_url_slug.return_value = TEST_AUTHORITY
    mock_licence_repository.get_licence_by_url_slug.return_value = TEST_LICENCE

    assert type(response) is FileResponse
    assert response.status_code == 200


def test_generate_form_calls_licence_lookup_service_for_form_details_with_correct_args(
    client,
    generate_form_url,
    mock_lookup_form_details,
):
    client.get(generate_form_url())

    mock_lookup_form_details.assert_called_with(
        authority_slug=TEST_AUTHORITY.url_slug,
        licence_slug=TEST_LICENCE.url_slug,
        interaction_id=TEST_LICENCE.licence_interactions[0].interaction_id,
        interaction_sub_id=TEST_LICENCE.licence_interactions[0].interaction_sub_id,
    )
