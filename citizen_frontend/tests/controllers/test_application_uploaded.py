from django.urls import reverse

def test_application_uploaded_returns_404_when_no_id_in_query_string(
        client
):
    response = client.get(reverse("application_uploaded"))

    assert response.status_code == 404


def test_application_uploaded_returns_200(client):
    response = client.get(reverse("application_uploaded", query={"id": "ApplicationRef1"}))
    assert response.status_code == 200