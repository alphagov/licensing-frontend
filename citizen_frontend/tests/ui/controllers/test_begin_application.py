import http
from copy import deepcopy

import pytest
from conftest import LICENCE_INTERACTION_CONTEXT, TEST_AUTHORITY, TEST_CUSTOMISATION_FIXED_FEE, TEST_LICENCE
from django.core.exceptions import ObjectDoesNotExist
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from citizen_frontend.exceptions import DataIntegrityError, DocumentDBError


@pytest.fixture
def mock_lookup_service(mocker):
    service = mocker.MagicMock()
    mocker.patch("citizen_frontend.controllers.begin_application.LicenceLookupService", return_value=service)
    yield service


@pytest.fixture
def mock_customisation_repository(mocker):
    repo = mocker.MagicMock()
    mocker.patch("citizen_frontend.controllers.begin_application.CustomisationRepository", return_value=repo)
    yield repo


@pytest.fixture
def get_begin_application_steps_url():
    def _url(**overrides) -> str:
        defaults = {
            "licence_slug": TEST_LICENCE.url_slug,
            "authority_slug": TEST_AUTHORITY.url_slug,
            "interaction_id": "apply",
            "interaction_sub_id": 5,
        }

        merged_kwargs = {**defaults, **overrides}
        return reverse("begin_application_steps", kwargs=merged_kwargs)

    return _url


@pytest.mark.parametrize("error", [DataIntegrityError, DocumentDBError, ObjectDoesNotExist])
def test_begin_application_steps_redirects_to_not_found_when_no_licence_context_found(
    client: Client, mock_lookup_service, get_begin_application_steps_url, error
):
    expected_error_message = "Incorrect licence, or authority does not exist"
    mock_lookup_service.get_licence_interaction_context.side_effect = error("some other error message")

    response = client.get(get_begin_application_steps_url())

    assert response.status_code == 404
    assert response.context["exception"] == expected_error_message
    assertTemplateUsed(response, "404.html")


def test_begin_application_steps_displays_licence_must_be_applied_for_locally_when_cant_apply_with_licensify(
    client: Client, get_begin_application_steps_url, mock_lookup_service
):
    modified_context = deepcopy(LICENCE_INTERACTION_CONTEXT)
    modified_context[3].using_gov_uk = False

    mock_lookup_service.get_licence_interaction_context.return_value = modified_context

    response = client.get(get_begin_application_steps_url())
    assert response.status_code == http.HTTPStatus.OK
    assertTemplateUsed(response, "citizen_frontend/licence_must_be_applied_for_locally_page.html")


def test_begin_application_steps_redirects_to_suspended_licence_when_no_published_customisation(
    client: Client, get_begin_application_steps_url, mock_customisation_repository, mock_lookup_service
):
    mock_lookup_service.get_licence_interaction_context.return_value = LICENCE_INTERACTION_CONTEXT
    mock_customisation_repository.find_published_customisation.return_value = None

    response = client.get(get_begin_application_steps_url())

    assert response.status_code == http.HTTPStatus.OK
    assertTemplateUsed(response, "citizen_frontend/licence_not_available_online_page.html")


def test_begin_application_steps_reaches_correct_page_when_all_data_exists(
    client: Client, get_begin_application_steps_url, mock_lookup_service, mock_customisation_repository
):
    mock_lookup_service.get_licence_interaction_context.return_value = LICENCE_INTERACTION_CONTEXT
    mock_customisation_repository.find_published_customisation.return_value = TEST_CUSTOMISATION_FIXED_FEE

    response = client.get(get_begin_application_steps_url())

    assert response.status_code == 200
    assertTemplateUsed(response, "citizen_frontend/licence_introduction_page.html")


def test_begin_application_steps_returns_published_customisation_information_url_as_legislation_url_if_exists(
    client: Client,
    mock_lookup_service,
    mock_customisation_repository,
    mock_get_licence_interaction_context,
    get_begin_application_steps_url,
    mock_find_published_customisation_with_fixed_fee,
):
    modified_context = deepcopy(LICENCE_INTERACTION_CONTEXT)
    modified_context[3].authority_url = "www.fallbackurl.com"
    mock_lookup_service.get_licence_interaction_context.return_value = modified_context

    expected_url = "https://test-information.com"
    mock_customisation_repository.find_published_customisation.return_value = TEST_CUSTOMISATION_FIXED_FEE

    response = client.get(get_begin_application_steps_url())
    assert response.context["legislation_info_url"] == expected_url


def test_begin_application_steps_returns_authority_url_as_fallback(
    client: Client, mock_lookup_service, mock_customisation_repository, get_begin_application_steps_url
):
    expected_url = "https://test-authority.com"
    mock_lookup_service.get_licence_interaction_context.return_value = LICENCE_INTERACTION_CONTEXT

    modified_customisation = deepcopy(TEST_CUSTOMISATION_FIXED_FEE)
    modified_customisation.information_url = None
    mock_customisation_repository.find_published_customisation.return_value = modified_customisation

    response = client.get(get_begin_application_steps_url())
    assert response.context["legislation_info_url"] == expected_url


def test_begin_application_steps_returns_error_when_no_licence_interaction_found(
    client: Client,
    get_begin_application_steps_url,
):
    non_existent_interaction_id = "not_real_interaction"
    response = client.get(get_begin_application_steps_url(interaction_id=non_existent_interaction_id))
    assert response.status_code == 404
    assert response.context["exception"] == "Invalid interaction ID"
    assertTemplateUsed(response, "404.html")
