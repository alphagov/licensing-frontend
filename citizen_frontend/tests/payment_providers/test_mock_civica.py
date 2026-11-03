from urllib.parse import urlencode

import pytest
from django.urls import reverse

from citizen_frontend.payment_providers.mock_providers.civica.mock_request import (
    mock_request,
)
from citizen_frontend.payment_providers.mock_providers.civica.mock_responses import (
    mock_failure_response,
    mock_goback_response,
    mock_success_response,
)


@pytest.mark.parametrize(
    "route, expected_response",
    [
        ("civica_success", mock_success_response),
        ("civica_failure", mock_failure_response),
        ("civica_goback", mock_goback_response),
    ],
)
def test_mock_civica_handles_payment_different_scenarios(client, route, expected_response):
    response = client.post(reverse(route), data=mock_request)

    expected_response = expected_response
    encoded_params = urlencode(expected_response)

    assert response.status_code == 302
    assert response.url == "http://testserver/fake/payment/civicaCallback" + "?" + encoded_params


def test_mock_civica_returns_400_invalid_request(client):
    response = client.post(reverse("civica_success"), data={"invalid": "request"})

    assert response.status_code == 400
