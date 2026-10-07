import json

import pytest
from django.urls import reverse

from citizen_frontend.exceptions import LicenceLookupError
from citizen_frontend.tests.conftest import TEST_LICENCE_AUTH_AND_INTERACTION_RESPONSE


@pytest.mark.parametrize(
    "view_name, kwargs",
    [
        ("get_licence_authorities_and_interactions_by_licence_code", {"licence_code": "1234"}),
        (
            "get_licence_authorities_and_interactions_by_licence_code_and_snac_code",
            {"licence_code": "12345", "snac_code": "56789"},
        ),
    ],
)
def test_get_licence_authorities_and_interactions_happy_paths(client, mock_lookup_service, view_name, kwargs):
    mock_lookup_service.get_licence_authorities_and_interactions.return_value = (
        TEST_LICENCE_AUTH_AND_INTERACTION_RESPONSE
    )
    with open(
        "citizen_frontend/tests/api/find_a_licence_integration/mock_get_licence_authorities_and_interactions_by_licence_code.json"
    ) as f:
        expected = json.load(f)

    response = client.get(reverse(view_name, kwargs=kwargs))

    mock_lookup_service.get_licence_authorities_and_interactions.assert_called_with(
        licence_code=kwargs.get("licence_code"), snac_code=kwargs.get("snac_code")
    )
    assert response.status_code == 200
    assert response.json() == expected


@pytest.mark.parametrize(
    "view_name, kwargs",
    [
        ("get_licence_authorities_and_interactions_by_licence_code", {"licence_code": "1234"}),
        (
            "get_licence_authorities_and_interactions_by_licence_code_and_snac_code",
            {"licence_code": "12345", "snac_code": "56789"},
        ),
    ],
)
def test_get_licence_authorities_and_interactions_returns_405_unsupported_method(client, view_name, kwargs):
    response = client.post(reverse(view_name, kwargs=kwargs))

    assert response.status_code == 405


@pytest.mark.parametrize(
    "view_name, kwargs",
    [
        ("get_licence_authorities_and_interactions_by_licence_code", {"licence_code": "1234"}),
        (
            "get_licence_authorities_and_interactions_by_licence_code_and_snac_code",
            {"licence_code": "12345", "snac_code": "56789"},
        ),
    ],
)
def test_get_licence_authorities_and_interactions_returns_404_licence_lookup_error(
    client, mock_lookup_service, view_name, kwargs
):
    mock_lookup_service.get_licence_authorities_and_interactions.side_effect = LicenceLookupError("test error")

    response = client.get(reverse(view_name, kwargs=kwargs))

    actual = response.json()

    assert response.status_code == 404
    assert actual == "test error"


@pytest.mark.parametrize(
    "view_name, kwargs",
    [
        ("get_licence_authorities_and_interactions_by_licence_code", {"licence_code": "1234"}),
        (
            "get_licence_authorities_and_interactions_by_licence_code_and_snac_code",
            {"licence_code": "12345", "snac_code": "56789"},
        ),
    ],
)
def test_get_licence_authorities_and_interactions_returns_500_with_unhandled_exception(
    client, mock_lookup_service, view_name, kwargs
):
    mock_lookup_service.get_licence_authorities_and_interactions.side_effect = Exception("Test error")

    response = client.get(reverse(view_name, kwargs=kwargs))

    assert response.status_code == 500
    assert response.json() == {"message": "Unhandled exception: Test error"}
