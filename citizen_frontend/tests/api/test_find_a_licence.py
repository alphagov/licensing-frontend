import json

import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse

from citizen_frontend.tests.conftest import TEST_TEMP_EVENT_LICENCE


@pytest.fixture
def mock_get_all_licences_from_database(mocker):
    yield mocker.patch("citizen_frontend.views.get_all_licences_from_database")


def test_get_all_licences_from_database_returns_expected_result(client, mock_get_all_licences_from_database):
    mock_get_all_licences_from_database.return_value = [TEST_TEMP_EVENT_LICENCE]
    with open("citizen_frontend/tests/api/mocked_response.json") as f:
        expected = json.load(f)

    response = client.get(reverse("get_all_licences"))

    mock_get_all_licences_from_database.assert_called_once()
    assert response.status_code == 200
    assert response.json() == expected


def test_get_all_licences_returns_404_empty_result(client, mock_get_all_licences_from_database):
    mock_get_all_licences_from_database.return_value = []

    response = client.get(reverse("get_all_licences"))

    assert response.status_code == 404


def test_get_all_licences_returns_404_db_error(client, mock_get_all_licences_from_database):
    pass


def test_get_all_licences_throws_error_incorrect_data_format_from_database(client, mock_get_all_licences_from_database):
    mock_get_all_licences_from_database.side_effect = ValidationError(message="Invalid")

    response = client.get(reverse("get_all_licences"))

    assert response.status_code == 404
    assert response.json() == ["Invalid"]


# TODO TEST CASES:
#   Other HTTP method requests?
#   DB Error unhappy path => pymongo error, connection error, operation error...?
#   Empty result
