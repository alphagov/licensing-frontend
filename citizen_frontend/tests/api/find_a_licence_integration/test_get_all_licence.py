import json

import pytest
from django.urls import reverse
from pydantic import ValidationError

from citizen_frontend.api.models.api_responses import LicenceResponse
from citizen_frontend.api.repository import licence_repository
from citizen_frontend.exceptions import DataError, DocumentDBError
from citizen_frontend.tests.conftest import TEST_LICENCE


@pytest.fixture
def mock_get_all_licences(mocker):
    yield mocker.patch.object(licence_repository, "get_all_licences")


def test_get_all_licences_returns_expected_result(client, mock_get_all_licences):
    mock_get_all_licences.return_value = [TEST_LICENCE]
    with open("citizen_frontend/tests/api/find_a_licence_integration/mock_get_all_licences_response.json") as f:
        expected = json.load(f)

    response = client.get(reverse("get_all_licences"))

    mock_get_all_licences.assert_called_once()
    assert response.status_code == 200
    assert response.json() == expected


def test_get_all_licences_returns_404_empty_result(client, mock_get_all_licences):
    mock_get_all_licences.return_value = []

    response = client.get(reverse("get_all_licences"))

    assert response.status_code == 404


def test_get_all_licences_returns_405_non_get_request_call(client, mock_get_all_licences):
    mock_get_all_licences.return_value = [TEST_LICENCE]

    response = client.post(reverse("get_all_licences"))

    assert response.status_code == 405


def test_get_all_licences_returns_404_data_error(client, mock_get_all_licences):
    mock_get_all_licences.side_effect = DataError("Invalid")

    response = client.get(reverse("get_all_licences"))

    assert response.json() == ["Invalid"]
    assert response.status_code == 404


def test_get_all_licences_returns_404_documentdb_error(client, mock_get_all_licences):
    mock_get_all_licences.side_effect = DocumentDBError("Connection failure")

    response = client.get(reverse("get_all_licences"))

    assert response.json() == ["Connection failure"]
    assert response.status_code == 404


def test_get_all_licences_returns_404_pydantic_validation_error(client, mock_get_all_licences, mocker):
    mock_get_all_licences.return_value = [TEST_LICENCE]

    mock_validation_error = ValidationError.from_exception_data(
        title="LicenceResponse",
        line_errors=[
            {
                "type": "string_type",
                "loc": ("url",),
                "msg": "Input should be a valid string",
                "input": 123,
            }
        ],
    )

    mocker.patch.object(LicenceResponse, "__init__", side_effect=mock_validation_error)

    response = client.get(reverse("get_all_licences"))

    assert response.status_code == 404
    assert response.json() == "Invalid response"


def test_get_all_licences_returns_500_with_unhandled_exception(client, mock_get_all_licences):
    mock_get_all_licences.side_effect = Exception("Test error")

    response = client.get(reverse("get_all_licences"))

    assert response.status_code == 500
    assert response.json() == {"message": "Unhandled exception: Test error"}
