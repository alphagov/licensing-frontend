import pytest
from conftest import TEST_INTERACTION_ID, TEST_LICENCE_CODE
from django.http import FileResponse
from django.urls import reverse


@pytest.fixture
def generate_form_url():
    def _url(**overrides) -> str:
        defaults = {
            "licence_slug": "string",
            "authority_slug": "string",
            "licence_code": TEST_LICENCE_CODE,
            "interaction_id": TEST_INTERACTION_ID,
            "interaction_sub_id": 5,
        }

        merged_kwargs = {**defaults, **overrides}
        return reverse("generate_form", kwargs=merged_kwargs)

    return _url


def test_generate_form_returns_file_response(client, generate_form_url):
    response = client.get(generate_form_url())

    assert type(response) is FileResponse
    assert response.status_code == 200
