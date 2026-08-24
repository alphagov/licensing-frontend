import json

import pytest
from django.urls import reverse

from citizen_frontend.tests.conftest import TEST_TEMP_EVENT_LICENCE


@pytest.fixture
def mock_get_all_licences_from_db(mocker):
    yield mocker.patch("citizen_frontend.views.get_all_licences_from_db")


@pytest.mark.django_db
def test_get_all_licences_with_descriptions(client, mock_get_all_licences_from_db):
    mock_get_all_licences_from_db.return_value = []
    response = client.get(reverse("get_all_licences"))
    assert response.status_code == 200


def test_get_all_licences_from_db(client, mock_get_all_licences_from_db):
    mock_get_all_licences_from_db.return_value = [TEST_TEMP_EVENT_LICENCE]
    with open("citizen_frontend/tests/api/mocked_response.json") as f:
        expected = json.load(f)

    response = client.get(reverse("get_all_licences"))

    mock_get_all_licences_from_db.assert_called_once()
    assert response.json() == expected
