import pytest
import requests
from django.urls import reverse

from citizen_frontend.payment_providers.forms.mock_forms import (
    MOCK_SUCCESS_REQUEST_NORTHGATE,
    MOCK_SUCCESS_RESPONSE_NORHTGATE,
    MockNorthgateResponseForm,
    build_northgate_response_with_hash,
)
from citizen_frontend.payment_providers.mock_providers.mock_northgate import build_response

# TODO scenarios: successful transaction
#                error in transaction
#                non matching hash
#                reason "cancel" present
#                service processed != "true"
# hash generation?...


@pytest.fixture
def mock_get(mocker):
    yield mocker.patch.object(requests, "get")


def test_mock_northgate_handles_get_request(client):
    response = client.get(reverse("northgate"))

    assert response.status_code == 200


def test_mock_northgate_throws_405_on_anything_but_get(client):
    response = client.post(reverse("northgate"), data={"hello": "world"})

    assert response.status_code == 405


def test_mock_northgate_calls_callback_with_correct_args_valid_request(client, mock_get):
    response = client.get(reverse("northgate"), data=MOCK_SUCCESS_REQUEST_NORTHGATE)

    assert response.status_code == 200
    expected_success_form = MockNorthgateResponseForm(
        build_northgate_response_with_hash(MOCK_SUCCESS_RESPONSE_NORHTGATE)
    )
    if expected_success_form.is_valid():
        data = expected_success_form.cleaned_data

    mock_get.assert_called_with(url=MOCK_SUCCESS_REQUEST_NORTHGATE["returnurl"], data=data)


def test_build_response_builds_success_response():
    expected_success_form = MockNorthgateResponseForm(
        build_northgate_response_with_hash(MOCK_SUCCESS_RESPONSE_NORHTGATE)
    )
    if expected_success_form.is_valid():
        actual = build_response()
        assert actual == expected_success_form.cleaned_data
