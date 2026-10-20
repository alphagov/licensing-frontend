# TODO scenarios to cover:
#   success, card declined, cancel, goback, know failure, unknown failure, generic failure
#   build out mock request, and response, probably best to stick them straight in their own file/dir
#   forms again?
from urllib.parse import urlencode

import pytest
from django.urls import reverse

from citizen_frontend.payment_providers.mock_providers.access_paysuite.mock_requests import mock_access_paysuite_request
from citizen_frontend.payment_providers.mock_providers.access_paysuite.mock_responses import (
    MOCK_ACCESS_PAYSUITE_KNOWN_FAILURE_FORM,
    MOCK_ACCESS_PAYSUITE_SUCCESS_FORM,
    card_declined_response,
    unknown_failure_response,
)


@pytest.fixture
def mock_redirect(mocker):
    yield mocker.patch(
        "citizen_frontend.payment_providers.mock_providers.access_paysuite.mock_access_paysuite.redirect"
    )


def test_mock_access_paysuite_handles_success(client, mock_redirect):
    response = client.post(reverse("access_paysuite_success"), data=mock_access_paysuite_request)
    expected_data = MOCK_ACCESS_PAYSUITE_SUCCESS_FORM

    if expected_data.is_valid():
        data = expected_data.cleaned_data
        encoded_params = urlencode(data)
    mock_redirect.assert_called_with(to="http://testserver/fake/payment/accessPaysuiteCallback" + "?" + encoded_params)

    assert response.status_code == 200


def test_mock_access_paysuite_handles_known_failures(client, mock_redirect):
    response = client.post(reverse("access_paysuite_known_failure"), data=mock_access_paysuite_request)

    expected_data = MOCK_ACCESS_PAYSUITE_KNOWN_FAILURE_FORM
    if expected_data.is_valid():
        data = expected_data.cleaned_data
        encoded_params = urlencode(data)
    mock_redirect.assert_called_with(to="http://testserver/fake/payment/accessPaysuiteCallback" + "?" + encoded_params)

    assert response.status_code == 200


def test_mock_access_paysuite_handles_cancellation(client, mock_redirect):
    client.post(reverse("access_paysuite_unknown_failure"), data=mock_access_paysuite_request)
    expected_data = unknown_failure_response

    encoded_params = urlencode(expected_data)
    mock_redirect.assert_called_with(to="http://testserver/fake/payment/accessPaysuiteCallback?" + encoded_params)


def test_mock_access_paysuite_handles_card_declined(client, mock_redirect):
    client.post(reverse("access_paysuite_card_declined"), data=mock_access_paysuite_request)
    expected_data = card_declined_response

    encoded_params = urlencode(expected_data)
    mock_redirect.assert_called_with(to="http://testserver/fake/payment/accessPaysuiteCallback?" + encoded_params)
