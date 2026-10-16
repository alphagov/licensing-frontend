import http

import citizen_frontend.views as views


def test_licence_must_be_applied_for_locally():
    response = views.licence_must_be_applied_for_locally(None)
    assert response.status_code == http.HTTPStatus.OK
