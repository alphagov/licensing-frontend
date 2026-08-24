import pytest


@pytest.mark.django_db
def test_get_all_licences_with_descriptions(client):
    response = client.get("/apply-for-a-licence/api/licences/")
    assert response.status_code == 200
