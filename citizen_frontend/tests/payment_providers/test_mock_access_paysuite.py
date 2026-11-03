# TODO scenarios to cover:
#   cancel, goback,, generic failure => cancel and go back go to a call backurl set in the paymount account
#   build out mock request, and response, probably best to stick them straight in their own file/dir
#   forms again?
from urllib.parse import urlencode

import pytest
from django.urls import reverse

from citizen_frontend.payment_providers.mock_providers.access_paysuite.mock_requests import mock_access_paysuite_request
from citizen_frontend.payment_providers.mock_providers.access_paysuite.mock_responses import (
    card_declined_response,
    known_failure_response,
    success_response,
    unknown_failure_response,
)


@pytest.mark.parametrize(
    "route, expected_response",
    [
        ("access_paysuite_success", success_response),
        ("access_paysuite_known_failure", known_failure_response),
        ("access_paysuite_unknown_failure", unknown_failure_response),
        ("access_paysuite_card_declined", card_declined_response),
    ],
)
def test_mock_access_paysuite_handles_different_scenarios(client, route, expected_response):
    response = client.post(reverse(route), data=mock_access_paysuite_request)

    data = expected_response
    encoded_params = urlencode(data)
    assert response.status_code == 302
    assert response.url == "http://testserver/fake/payment/accessPaysuiteCallback" + "?" + encoded_params


def test_mock_access_paysuite_returns_400_invalid_request(client):
    response = client.post(reverse("access_paysuite_success"), data={"invalid": "request"})

    assert response.status_code == 400
