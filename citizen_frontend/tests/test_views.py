import pytest
from django.test import Client
from django.urls import reverse
from pytest_mock import MockerFixture

import citizen_frontend.views
from citizen_frontend.services.licence_lookup_service import LicenceInteractionContext


@pytest.fixture
def begin_application_steps_view():
    return reverse(
        "begin_application_steps",
        kwargs={
            "licence_slug": "string",
            "authority_slug": "string",
            "interaction_id": "string",
            "interaction_sub_id": 5,
        },
    )


def test_begin_application_steps_redirects_to_not_found_when_no_licence_context_found(
    client: Client, mock_get_licence_interaction_context, begin_application_steps_view
):
    mock_get_licence_interaction_context.return_value = None
    response = client.get(begin_application_steps_view)
    assert response.status_code == 404
    assert response.context["exception"].lower() == "missing details"


def test_begin_application_steps_redirects_to_not_handled_when_not_handled_by_licensify(
    client: Client, mock_get_licence_interaction_context, begin_application_steps_view
):
    mock_get_licence_interaction_context.return_value: LicenceInteractionContext = (
        mock_get_licence_interaction_context.return_value
    )
    mock_get_licence_interaction_context.return_value.licence_detail.using_gov_uk = False
    response = client.get(begin_application_steps_view)
    assert response.status_code == 404
    assert response.context["exception"].lower() == "unhandled"


def test_begin_application_steps_redirects_to_suspended_licence_when_no_published_customisation(
    client: Client,
    mock_get_licence_interaction_context,
    begin_application_steps_view,
    mock_find_published_customisation,
):
    response = client.get(begin_application_steps_view)
    assert response.status_code == 404
    assert response.context["exception"].lower() == "suspended"
