from django.contrib.sessions.backends.base import SessionBase
from django.test.client import RequestFactory
from django.urls import reverse
from citizen_frontend.controllers.application_uploaded import application_uploaded


def test_application_uploaded_returns_404_when_no_id_in_query_string(client):
    response = client.get(reverse("application_uploaded"))
    assert response.status_code == 404


def test_application_uploaded_returns_404_when_id_not_in_session(client):
    response = client.get(reverse("application_uploaded", query={"id": "ApplicationRef1"}))
    assert response.status_code == 404


def test_application_uploaded_returns_200_when_id_matches_session_ids(client):
    request = RequestFactory().get(reverse("application_uploaded", query={"id": "ApplicationRef1"}))
    session = SessionBase()
    session["applicationReferenceNumbers"] = ["ApplicationRef1"]
    request.session = session

    response = application_uploaded(request)
    assert response.status_code == 200