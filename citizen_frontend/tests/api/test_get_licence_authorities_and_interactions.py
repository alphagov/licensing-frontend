import json

import pytest
from django.urls import reverse

from citizen_frontend.exceptions import LicenceLookupError
from citizen_frontend.tests.conftest import TEST_LICENCE_AUTH_AND_INTERACTION_RESPONSE


def test_get_licence_authorities_and_interactions_by_licence_code_happy_path(client, mock_lookup_service):
    mock_lookup_service.get_licence_authorities_and_interactions.return_value = (
        TEST_LICENCE_AUTH_AND_INTERACTION_RESPONSE
    )
    with open("citizen_frontend/tests/api/mock_get_licence_authorities_and_interactions_by_licence_code.json") as f:
        expected = json.load(f)

    response = client.get(
        reverse("get_licence_authorities_and_interactions_by_licence_code", kwargs={"licence_code": "1234"})
    )

    mock_lookup_service.get_licence_authorities_and_interactions.assert_called_with(licence_code="1234", snac_code=None)
    assert response.status_code == 200
    assert response.json() == expected


def test_get_licence_authorities_and_interactions_by_licence_code_returns_405_unsupported_method(client):
    response = client.post(
        reverse("get_licence_authorities_and_interactions_by_licence_code", kwargs={"licence_code": "1234"})
    )

    assert response.status_code == 405


@pytest.mark.parametrize("result", [{}, [], ()])
def test_get_licence_authorities_and_interactions_by_licence_code_returns_404_empty_result_from_lookup_service(
    client, mock_lookup_service, result
):
    mock_lookup_service.get_licence_authorities_and_interactions.return_value = result

    response = client.get(
        reverse("get_licence_authorities_and_interactions_by_licence_code", kwargs={"licence_code": "1234"})
    )

    assert response.status_code == 404


def test_get_licence_authorities_and_interactions_by_licence_code_returns_404_licence_lookup_error(
    client, mock_lookup_service
):
    mock_lookup_service.get_licence_authorities_and_interactions.side_effect = LicenceLookupError("test error")

    response = client.get(
        reverse("get_licence_authorities_and_interactions_by_licence_code", kwargs={"licence_code": "1234"})
    )

    actual = json.loads(response.content.decode("utf-8"))

    assert response.status_code == 404
    assert actual == "test error"


def test_get_licence_authorities_and_interactions_by_licence_code_and_snac(client, mock_lookup_service):
    mock_lookup_service.get_licence_authorities_and_interactions.return_value = (
        TEST_LICENCE_AUTH_AND_INTERACTION_RESPONSE
    )

    with open("citizen_frontend/tests/api/mock_get_licence_authorities_and_interactions_by_licence_code.json") as f:
        expected = json.load(f)

    response = client.get(
        reverse(
            "get_licence_authorities_and_interactions_by_licence_code_and_snac_code",
            kwargs={"licence_code": "12345", "snac_code": "56789"},
        )
    )

    mock_lookup_service.get_licence_authorities_and_interactions.assert_called_with(
        licence_code="12345", snac_code="56789"
    )

    assert response.status_code == 200
    assert response.json() == expected


@pytest.mark.parametrize("empty_result", [{}, (), []])
def test_get_licence_authorities_and_interactions_by_licence_code_and_snac_returns_404_empty_results(
    client, mock_lookup_service, empty_result
):
    mock_lookup_service.get_licence_authorities_and_interactions.return_value = empty_result

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


def test_get_licence_authorities_and_interactions_returns_500_with_unhandled_exception(client, mock_lookup_service):
    mock_lookup_service.get_licence_authorities_and_interactions.side_effect = Exception("Test error")

    response = client.get(
        reverse("get_licence_authorities_and_interactions_by_licence_code", kwargs={"licence_code": "1234"})
    )

    assert response.status_code == 500
    assert response.json() == {"message": "Unhandled exception: Test error"}
