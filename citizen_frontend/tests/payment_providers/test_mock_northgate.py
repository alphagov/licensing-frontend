from urllib.parse import urlencode

import pytest
from django.urls import reverse

from citizen_frontend.payment_providers.forms.mock_forms import (
    NorthgateResponseForm,
)
from citizen_frontend.payment_providers.mock_providers.northgate.mock_northgate import build_response
from citizen_frontend.payment_providers.mock_providers.northgate.mock_requests import (
    MOCK_SUCCESS_REQUEST_NORTHGATE,
)
from citizen_frontend.payment_providers.mock_providers.northgate.mock_responses import (
    MOCK_NORTHGATE_CANCEL_RESPONSE,
    MOCK_NORTHGATE_ERROR_RESPONSE,
    MOCK_NORTHGATE_FAILURE_RESPONSE,
    MOCK_SUCCESS_RESPONSE_NORTHGATE,
    build_northgate_response_with_hash,
)


@pytest.fixture
def mock_redirect(mocker):
    yield mocker.patch("citizen_frontend.payment_providers.mock_providers.northgate.mock_northgate.redirect")


def test_mock_northgate_throws_405_on_anything_but_get(client):
    response = client.post(reverse("northgate_success"), data={"hello": "world"})

    assert response.status_code == 405


def test_mock_northgate_success_calls_callback_with_correct_args_valid_request(client, mock_redirect):
    response = client.get(reverse("northgate_success"), data=MOCK_SUCCESS_REQUEST_NORTHGATE)

    assert response.status_code == 200
    expected_success_form = NorthgateResponseForm(build_northgate_response_with_hash(MOCK_SUCCESS_RESPONSE_NORTHGATE))
    if expected_success_form.is_valid():
        data = expected_success_form.cleaned_data
        encoded_params = urlencode(data)

        mock_redirect.assert_called_with(to=f"{MOCK_SUCCESS_REQUEST_NORTHGATE['returnurl']}?{encoded_params}")


def test_build_response_builds_success_response():
    expected_success_form = NorthgateResponseForm(build_northgate_response_with_hash(MOCK_SUCCESS_RESPONSE_NORTHGATE))
    if expected_success_form.is_valid():
        actual = build_response("success")
        assert actual == expected_success_form.cleaned_data


def test_build_response_builds_failure_response():
    expected_failure_form = NorthgateResponseForm(build_northgate_response_with_hash(MOCK_NORTHGATE_FAILURE_RESPONSE))
    if expected_failure_form.is_valid():
        actual = build_response("failure")
        assert actual == expected_failure_form.cleaned_data


def test_build_response_builds_cancelled_response():
    expected_cancel_form = NorthgateResponseForm(build_northgate_response_with_hash(MOCK_NORTHGATE_CANCEL_RESPONSE))
    if expected_cancel_form.is_valid():
        actual = build_response("cancel")
        assert actual == expected_cancel_form.cleaned_data


def test_build_response_builds_error_response():
    expected_error_form = NorthgateResponseForm(build_northgate_response_with_hash(MOCK_NORTHGATE_ERROR_RESPONSE))
    if expected_error_form.is_valid():
        actual = build_response("error")
        assert actual == expected_error_form.cleaned_data
