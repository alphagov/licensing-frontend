import json

import pytest
from django.urls import reverse

from citizen_frontend.tests.conftest import TEST_LICENCE_AUTH_AND_INTERACTION


def test_get_licence_authorities_and_interactions_by_licence_code_and_snac(client, mock_lookup_service):
    mock_lookup_service.licence_authorities_and_interactions_by_snac_code.return_value = (
        TEST_LICENCE_AUTH_AND_INTERACTION
    )

    with open("citizen_frontend/tests/api/mock_get_licence_authorities_and_interactions_by_licence_code.json") as f:
        expected = json.load(f)

    response = client.get(
        reverse(
            "get_licence_authorities_and_interactions_by_licence_code_and_snac_code",
            kwargs={"licence_code": "12345", "snac_code": "56789"},
        )
    )

    mock_lookup_service.licence_authorities_and_interactions_by_snac_code.assert_called_with(
        snac_code="56789", licence_code="12345"
    )

    assert response.status_code == 200
    assert response.json() == expected


@pytest.mark.parametrize("empty_result", [{}, (), []])
def test_get_licence_authorities_and_interactions_by_licence_code_and_snac_returns_404_empty_results(
    client, mock_lookup_service, empty_result
):
    mock_lookup_service.licence_authorities_and_interactions_by_snac_code.return_value = empty_result

    response = client.get(
        reverse(
            "get_licence_authorities_and_interactions_by_licence_code_and_snac_code",
            kwargs={"licence_code": "12345", "snac_code": "56789"},
        )
    )

    assert response.status_code == 404


def test_get_licence_authorities_and_interactions_by_licence_code_and_snac_returns_405_unsupported_method(
    client, mock_lookup_service
):
    response = client.post(
        reverse(
            "get_licence_authorities_and_interactions_by_licence_code_and_snac_code",
            kwargs={"licence_code": "12345", "snac_code": "56789"},
        )
    )

    assert response.status_code == 405
