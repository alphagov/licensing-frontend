import json

import pytest
from django.urls import reverse

from citizen_frontend.tests.conftest import TEST_LICENCE_AUTH_AND_INTERACTION

# TODO TEST CASES:
#   Happy path mocked out
#   Licence with code not found
#   No authorities found => different response => current code sends 404
#  DB connectivity issues


def test_get_licence_authorities_and_interactions_by_licence_code_happy_path(client, mock_lookup_service):
    mock_lookup_service.get_licence_authority_and_interactions.return_value = TEST_LICENCE_AUTH_AND_INTERACTION
    with open("citizen_frontend/tests/api/mock_get_licence_authorities_and_interactions_by_licence_code.json") as f:
        expected = json.load(f)

    response = client.get(
        reverse("get_licence_authority_and_interactions_by_licence_code", kwargs={"licence_code": "1234"})
    )

    mock_lookup_service.get_licence_authority_and_interactions.assert_called_with(licence_code="1234")
    assert response.status_code == 200
    assert response.json() == expected


def test_get_licence_authority_and_interactions_by_licence_code_returns_405_unsupported_method(client):
    response = client.post(
        reverse("get_licence_authority_and_interactions_by_licence_code", kwargs={"licence_code": "1234"})
    )

    assert response.status_code == 405


@pytest.mark.parametrize("result", [{}, [], ()])
def test_get_licence_authority_and_interactions_by_licence_code_returns_404_empty_result_from_lookup_service(
    client, mock_lookup_service, result
):
    mock_lookup_service.get_licence_authority_and_interactions.return_value = result

    response = client.get(
        reverse("get_licence_authority_and_interactions_by_licence_code", kwargs={"licence_code": "1234"})
    )

    assert response.status_code == 404
