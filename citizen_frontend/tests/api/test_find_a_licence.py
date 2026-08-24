import pytest
from django.urls import reverse


@pytest.fixture
def mock_get_all_licences_from_db(mocker):
    yield mocker.patch("citizen_frontend.views.get_all_licences_from_db")


@pytest.mark.django_db
def test_get_all_licences_with_descriptions(client):
    response = client.get(reverse("get_all_licences"))
    assert response.status_code == 200


def test_get_all_licences_from_db(client, mock_get_all_licences_from_db):
    client.get(reverse("get_all_licences"))
    mock_get_all_licences_from_db.assert_called_once()
