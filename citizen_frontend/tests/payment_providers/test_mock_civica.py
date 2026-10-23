from urllib.parse import urlencode

from django.urls import reverse

from citizen_frontend.payment_providers.mock_providers.civica.mock_request import (
    mock_request,
)
from citizen_frontend.payment_providers.mock_providers.civica.mock_responses import mock_success_response


def test_civica_handles_successful_payment(client):
    response = client.post(reverse("civica_success"), data=mock_request)

    expected_response = mock_success_response
    encoded_params = urlencode(expected_response)

    assert response.status_code == 302
    assert response.url == "http://testserver/fake/payment/civicaCallback" + "?" + encoded_params
