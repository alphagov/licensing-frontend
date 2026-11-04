import pytest


@pytest.fixture
def test_licence_application_cancelled_page_url(live_server):
    return f"{live_server.url}/apply-for-a-licence/payment/licenceCallback?id=gds-test-1816078"


@pytest.fixture
def mock_context(mocker):
    yield mocker.patch(
        "citizen_frontend.controllers.payment_licence_callback.mock_payment_licence_callback_cancelled_context"
    )


def test_page_has_correct_headings(get_dom_parser, test_licence_application_cancelled_page_url, mock_context):
    pass


def test_page_has_4_steps(get_dom_parser, test_licence_application_cancelled_page_url, mock_context):
    pass


def test_page_has_licence_name(get_dom_parser, test_licence_application_cancelled_page_url, mock_context):
    pass


def test_page_has_no_message_if_empty(get_dom_parser, test_licence_application_cancelled_page_url, mock_context):
    pass


def test_page_has_message_if_not_empty(get_dom_parser, test_licence_application_cancelled_page_url, mock_context):
    pass


def test_page_has_department_contact_details(get_dom_parser, test_licence_application_cancelled_page_url, mock_context):
    pass


def test_page_displays_licence_finder_url_under_next_steps(
    get_dom_parser, test_licence_application_cancelled_page_url, mock_context
):
    pass
