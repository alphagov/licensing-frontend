import pytest
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from citizen_frontend.controllers.application_uploaded import application_uploaded


@pytest.fixture
def session_client(client, settings):
    settings.SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    session = client.session
    session["applicationReferenceNumbers"] = ["ApplicationRef1", "ApplicationRef2"]
    session.save()
    return client


def test_application_uploaded_returns_404_when_no_id_in_query_string(client):
    response = client.get(reverse("application_uploaded"))
    assert response.status_code == 404


def test_application_uploaded_returns_404_when_id_not_in_session(client):
    response = client.get(reverse("application_uploaded", query={"id": "ApplicationRef1"}))
    assert response.status_code == 404


@pytest.mark.parametrize(
    ("app_ref", "expected_template"),
    [
        ("ApplicationRef1", "citizen_frontend/licence_submission_success_page.html"),
        ("ApplicationRef2", "citizen_frontend/licence_submission_success_page.html"),
    ]
)
def test_application_uploaded_returns_200_when_id_matches_session_ids(
        session_client, app_ref, expected_template
):
    response = session_client.get(reverse("application_uploaded", query={"id": app_ref}))

    assert response.status_code == 200
    assertTemplateUsed(response, expected_template)

