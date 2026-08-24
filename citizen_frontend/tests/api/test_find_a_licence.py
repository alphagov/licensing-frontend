import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_get_all_licences_with_descriptions(client):
    response = client.get(reverse("get_all_licences"))
    assert response.status_code == 200
