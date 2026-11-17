from copy import deepcopy

import pytest
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from conftest import TEST_LICENCE_APPLICATION, TEST_CUSTOMISATION_FIXED_FEE, TEST_CUSTOMISATION_NO_FEE


@pytest.fixture
def session_client(client, settings):
    settings.SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    session = client.session
    session["applicationReferenceNumbers"] = ["ApplicationRef1", "ApplicationRef2", "ApplicationRef3"]
    session.save()
    return client


@pytest.fixture
def mock_get_details(mocker):
    yield mocker.patch("citizen_frontend.controllers.application_uploaded.get_details")


def test_application_uploaded_returns_404_when_no_id_in_query_string(client):
    response = client.get(reverse("application_uploaded"))
    assert response.status_code == 404


def test_application_uploaded_returns_404_when_id_not_in_session(client):
    response = client.get(reverse("application_uploaded", query={"id": "ApplicationRef1"}))
    assert response.status_code == 404


@pytest.mark.parametrize(
    ("app_ref", "expected_template"),
    [
        ("ApplicationRef1", "citizen_frontend/licence_submission_success_page.html"),
        ("ApplicationRef2", "citizen_frontend/licence_submission_success_page.html"),
    ]
)
def test_application_uploaded_returns_success_page_when_id_matches_session_ids(
        session_client, mock_get_details, app_ref, expected_template
):
    application = deepcopy(TEST_LICENCE_APPLICATION)
    application.required_payment_amount = None
    mock_get_details.return_value = (application,TEST_CUSTOMISATION_NO_FEE)
    response = session_client.get(reverse("application_uploaded", query={"id": app_ref}))

    assert response.status_code == 200
    assertTemplateUsed(response, expected_template)


def test_application_uploaded_returns_provide_fee_page_when_payment_required_but_amount_is_none(
        session_client, mock_get_details
):
    application = deepcopy(TEST_LICENCE_APPLICATION)
    application.required_payment_amount = None
    mock_get_details.return_value = (application, TEST_CUSTOMISATION_FIXED_FEE)

    response = session_client.get(reverse("application_uploaded", query={"id": "ApplicationRef1"}))

    assert response.status_code == 200
    assertTemplateUsed(response, "citizen_frontend/licence_application_provide_fee_amount_page.html")


def test_application_uploaded_returns_prepayment_page_when_required_payment_amount_provided(
        session_client, mock_get_details
):
    mock_get_details.return_value = (TEST_LICENCE_APPLICATION, TEST_CUSTOMISATION_FIXED_FEE)

    response = session_client.get(reverse("application_uploaded", query={"id": "ApplicationRef1"}))

    assert response.status_code == 200
    assertTemplateUsed(response, "citizen_frontend/licence_application_prepayment_page.html")