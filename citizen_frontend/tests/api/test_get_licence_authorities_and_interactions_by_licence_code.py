import json

import pytest
from django.urls import reverse

# TODO TEST CASES:
#   Happy path mocked out
#   Licence with code not found
#   No authorities found => different response => current code sends 404


@pytest.fixture
def mock_lookup_service(mocker):
    mock_look_up_service = mocker.MagicMock()
    mocker.patch(
        "citizen_frontend.api.find_a_licence_integration.LicenceLookupService", return_value=mock_look_up_service
    )
    yield mock_look_up_service


def test_get_licence_authorities_and_interactions_by_licence_code_happy_path(client, mock_lookup_service):
    mock_lookup_service.get_licence_authority_and_interactions.return_value = {}
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
