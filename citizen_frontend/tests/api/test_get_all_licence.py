import json

import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse

from citizen_frontend.tests.conftest import TEST_LICENCE


@pytest.fixture
def mock_get_all_licences_from_database(mocker):
    yield mocker.patch("citizen_frontend.api.find_a_licence_integration.get_all_licences_from_database")


def test_get_all_licences_returns_expected_result(client, mock_get_all_licences_from_database):
    mock_get_all_licences_from_database.return_value = [TEST_LICENCE]
    with open("citizen_frontend/tests/api/mock_get_all_licences_response.json") as f:
        expected = json.load(f)

    response = client.get(reverse("get_all_licences"))

    mock_get_all_licences_from_database.assert_called_once()
    assert response.status_code == 200
    assert response.json() == expected


def test_get_all_licences_returns_404_empty_result(client, mock_get_all_licences_from_database):
    mock_get_all_licences_from_database.return_value = []

    response = client.get(reverse("get_all_licences"))

    assert response.status_code == 404


def test_get_all_licences_throws_error_incorrect_data_format_from_database(client, mock_get_all_licences_from_database):
    mock_get_all_licences_from_database.side_effect = ValidationError(message="Invalid")

    response = client.get(reverse("get_all_licences"))

    assert response.json() == ["Invalid"]
    assert response.status_code == 404


def test_get_all_licences_returns_405_non_get_request_call(client, mock_get_all_licences_from_database):
    mock_get_all_licences_from_database.return_value = [TEST_LICENCE]

    response = client.post(reverse("get_all_licences"))

    assert response.status_code == 405
