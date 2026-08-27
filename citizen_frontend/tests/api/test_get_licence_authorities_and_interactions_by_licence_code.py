from django.urls import reverse


def test_get_licence_authorities_and_interactions_by_licence_code_happy_path(client):
    response = client.get(
        reverse("get_licence_authority_and_interactions_by_licence_code", kwargs={"licence_code": "1234"})
    )

    assert response.status_code == 200
