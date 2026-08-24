import pytest


@pytest.mark.django_db
def test_get_all_licences_with_descriptions(client):
    response = client.get("/api/licences")
    assert response.status_code == 200
