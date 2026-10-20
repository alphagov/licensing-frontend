# TODO scenarios to cover:
#   success, card declined, cancel, goback, know failure, unknown failure, generic failure
#   build out mock request, and response, probably best to stick them straight in their own file/dir
#   forms again?
import pytest
import requests
from django.urls import reverse


@pytest.fixture
def mock_get(mocker):
    yield mocker.patch.object(requests, "get")


def test_mock_access_paysuite_handles_success(client, mock_get):
    response = client.post(reverse("access_paysuite_success"))

    mock_get.assert_called_with(url="http://testserver/fake/payment/accessPaysuiteCallback")

    assert response.status_code == 200
