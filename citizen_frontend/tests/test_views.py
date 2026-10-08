import pytest
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed


@pytest.fixture
def get_begin_application_steps_url():
    def _url(**overrides) -> str:
        defaults = {
            "licence_slug": "string",
            "authority_slug": "string",
            "interaction_id": "apply",
            "interaction_sub_id": 5,
        }

        merged_kwargs = {**defaults, **overrides}
        return reverse("begin_application_steps", kwargs=merged_kwargs)

    return _url


def test_begin_application_steps_redirects_to_not_found_when_no_licence_context_found(
    client: Client, mock_get_licence_interaction_context, get_begin_application_steps_url
):
    mock_get_licence_interaction_context.return_value = None
    response = client.get(get_begin_application_steps_url())
    assert response.status_code == 404
    assert response.context["exception"].lower() == "missing details"


def test_begin_application_steps_redirects_to_not_handled_when_not_handled_by_licensify(
    client: Client, mock_get_licence_interaction_context, get_begin_application_steps_url
):
    mock_get_licence_interaction_context.return_value = mock_get_licence_interaction_context.return_value
    mock_get_licence_interaction_context.return_value.licence_detail.using_gov_uk = False
    response = client.get(get_begin_application_steps_url())
    assert response.status_code == 404
    assert response.context["exception"].lower() == "unhandled"


def test_begin_application_steps_redirects_to_suspended_licence_when_no_published_customisation(
    client: Client,
    mock_get_licence_interaction_context,
    get_begin_application_steps_url,
    mock_find_published_customisation_with_fixed_fee,
):
    mock_find_published_customisation_with_fixed_fee.return_value = None
    response = client.get(get_begin_application_steps_url())
    assert response.status_code == 404
    assert response.context["exception"].lower() == "suspended"


def test_begin_application_steps_reaches_correct_page_when_all_data_exists(
    client: Client,
    mock_get_licence_interaction_context,
    get_begin_application_steps_url,
    mock_find_published_customisation_with_fixed_fee,
):
    response = client.get(get_begin_application_steps_url())
    assert response.status_code == 200
    assertTemplateUsed(response, "citizen_frontend/licence_introduction_page.html")


def test_begin_application_steps_returns_published_customisation_information_url_as_legislation_url_if_exists(
    client: Client,
    mock_get_licence_interaction_context,
    get_begin_application_steps_url,
    mock_find_published_customisation_with_fixed_fee,
):
    expected_url = "www.superceedingurl.com"
    mock_find_published_customisation_with_fixed_fee.return_value.information_url = expected_url
    mock_get_licence_interaction_context.return_value.licence_detail.authority_url = "www.fallbackurl.com"
    response = client.get(get_begin_application_steps_url())
    assert response.context["legislation_info_url"] == expected_url


def test_begin_application_steps_returns_authority_url_as_fallback(
    client: Client,
    mock_get_licence_interaction_context,
    get_begin_application_steps_url,
    mock_find_published_customisation_with_fixed_fee,
):
    expected_url = "www.fallbackurl.com"
    mock_find_published_customisation_with_fixed_fee.return_value.information_url = None
    mock_get_licence_interaction_context.return_value.licence_detail.authority_url = expected_url
    response = client.get(get_begin_application_steps_url())
    assert response.context["legislation_info_url"] == expected_url


def test_begin_application_steps_returns_error_when_no_licence_interaction_found(
    client: Client,
    get_begin_application_steps_url,
):
    non_existant_interaction_id = "not_real_interaction"
    response = client.get(get_begin_application_steps_url(interaction_id=non_existant_interaction_id))
    assert response.status_code == 404
    assert response.context["exception"].lower() == "bad interaction"
