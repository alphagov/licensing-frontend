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
def mock_get_licence_interaction_context(mocker):
    yield mocker.patch.object(licence_lookup_service, "get_licence_interaction_context")


def test_generate_form_returns_file_response(
    client, generate_form_url, mock_authority_repository, mock_licence_repository, mock_get_licence_interaction_context
):
    response = client.get(generate_form_url())

    assert type(response) is FileResponse
    assert response.status_code == 200


def test_generate_form_calls_licence_lookup_service_for_context(
    client, generate_form_url, mock_get_licence_interaction_context
):
    client.get(generate_form_url())

    mock_get_licence_interaction_context.assert_called_with(
        authority_url_slug=TEST_AUTHORITY.url_slug,
        licence_url_slug=TEST_LICENCE.url_slug,
        interaction=TEST_LICENCE.licence_interactions[0].interaction_id,
        interaction_sub_id=TEST_LICENCE.licence_interactions[0].interaction_sub_id,
    )
