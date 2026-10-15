import pytest
import requests
from django.urls import reverse


@pytest.fixture
def mock_get(mocker):
    yield mocker.patch.object(requests, "get")


def test_mock_northgate_handles_get_request(client):
    response = client.get(reverse("northgate"))

    assert response.status_code == 200


def test_mock_northgate_throws_405_on_anything_but_get(client):
    response = client.post(reverse("northgate"), data={"hello": "world"})

    assert response.status_code == 405


def test_mock_northgate_calls_callback_valid_request(client, mock_get):
    with open("citizen_frontend/payment_providers/mock_providers/mock_record.xml", encoding="utf-8") as f:
        xml_string = f.read().strip()

    request_data = {
        "data": "we send this and then expect it back",
        "returnurl": "to our callback url",
        "returntext": "take me back",
        "amount": "10",
        "recordxml": xml_string,
        "payforbasketmode": "true",
        "ignoreconfirmation": "true",
    }
    response = client.get(reverse("northgate"), data=request_data)

    assert response.status_code == 200
    mock_get.assert_called()
