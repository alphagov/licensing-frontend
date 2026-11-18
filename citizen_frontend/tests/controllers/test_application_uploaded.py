from copy import deepcopy

import pytest
from conftest import (
    TEST_CUSTOMISATION_FIXED_FEE,
    TEST_CUSTOMISATION_NO_FEE,
    TEST_LICENCE_APPLICATION,
)
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed


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


@pytest.fixture
def mock_application_repo(mocker):
    mock_repo = mocker.MagicMock()
    mocker.patch(
        "citizen_frontend.controllers.application_uploaded.LicenceApplicationRepository", return_value=mock_repo
    )
    yield mock_repo


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
    ],
)
def test_application_uploaded_returns_success_page_when_id_matches_session_ids(
    session_client, mock_get_details, app_ref, expected_template
):
    application = deepcopy(TEST_LICENCE_APPLICATION)
    application.required_payment_amount = None
    mock_get_details.return_value = (application, TEST_CUSTOMISATION_NO_FEE)
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


def test_get_details_calls_correct_repository_to_get_application_from_id(
    session_client,
    mock_application_repo,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_fixed_fee
):
    mock_application_repo.get_application_from_id.return_value = TEST_LICENCE_APPLICATION
    session_client.get(reverse("application_uploaded", query={"id": "ApplicationRef1"}))

    mock_application_repo.get_application_from_id.assert_called()


def test_get_details_calls_licence_look_up_service_with_correct_args(
    session_client,
    mock_application_repo,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_fixed_fee
):
    mock_application_repo.get_application_from_id.return_value = TEST_LICENCE_APPLICATION

    session_client.get(reverse("application_uploaded", query={"id": "ApplicationRef1"}))

    mock_get_licence_interaction_context.assert_called_with(
        TEST_LICENCE_APPLICATION.authority,
        TEST_LICENCE_APPLICATION.licence,
        TEST_LICENCE_APPLICATION.service.interaction_id,
        TEST_LICENCE_APPLICATION.service.interaction_sub_id,
    )


def test_get_details_calls_interaction_customisation_repository_with_correct_args(
        session_client,
        mock_application_repo,
        mock_get_licence_interaction_context,
        mock_find_published_customisation_with_fixed_fee
):
    mock_application_repo.get_application_from_id.return_value = TEST_LICENCE_APPLICATION

    session_client.get(reverse("application_uploaded", query={"id": "ApplicationRef1"}))

    mock_find_published_customisation_with_fixed_fee.assert_called_with(
        TEST_LICENCE_APPLICATION.authority,
        TEST_LICENCE_APPLICATION.service.licence_code,
        TEST_LICENCE_APPLICATION.service.interaction_id,
        TEST_LICENCE_APPLICATION.service.interaction_sub_id,
    )
