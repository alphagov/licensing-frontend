# TODO scenarios to cover:
#   success, card declined, cancel, goback, know failure, unknown failure, generic failure
#   build out mock request, and response, probably best to stick them straight in their own file/dir
#   forms again?
import pytest
import requests
from django.urls import reverse

from citizen_frontend.payment_providers.mock_providers.access_paysuite.mock_requests import mock_access_paysuite_request
from citizen_frontend.payment_providers.mock_providers.access_paysuite.mock_responses import (
    MOCK_ACCESS_PAYSUITE_KNOWN_FAILURE_FORM,
    MOCK_ACCESS_PAYSUITE_SUCCESS_FORM,
)


@pytest.fixture
def mock_get(mocker):
    yield mocker.patch.object(requests, "get")


def test_mock_access_paysuite_handles_success(client, mock_get):
    response = client.post(reverse("access_paysuite_success"), data=mock_access_paysuite_request)
    expected_data = MOCK_ACCESS_PAYSUITE_SUCCESS_FORM

    if expected_data.is_valid():
        data = expected_data.cleaned_data

    mock_get.assert_called_with(url="http://testserver/fake/payment/accessPaysuiteCallback", params=data)

    assert response.status_code == 200


def test_mock_access_paysuite_handles_known_failures(client, mock_get):
    response = client.post(reverse("access_paysuite_known_failure"), data=mock_access_paysuite_request)

    expected_data = MOCK_ACCESS_PAYSUITE_KNOWN_FAILURE_FORM
    if expected_data.is_valid():
        data = expected_data.cleaned_data

    mock_get.assert_called_with(url="http://testserver/fake/payment/accessPaysuiteCallback", params=data)

    assert response.status_code == 200
