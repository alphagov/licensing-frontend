import pytest
from conftest import BASE_URL, TEST_AUTHORITY, TEST_DEPARTMENT, TEST_LICENCE


@pytest.fixture
def test_licence_application_cancelled_page_url(live_server):
    return f"{live_server.url}/apply-for-a-licence/payment/licenceCallback?id=gds-test-1816200"


@pytest.fixture
def mock_context(mocker):
    yield mocker.patch("citizen_frontend.controllers.payment_licence_callback.mock_payment_licence_callback_context")


@pytest.fixture
def mock_payment_status(mocker):
    yield mocker.patch("citizen_frontend.controllers.payment_licence_callback.mock_payment_response_status")


def test_page_has_correct_headings(
    get_dom_parser, test_licence_application_cancelled_page_url, mock_context, mock_payment_status
):
    mock_payment_status.return_value = "cancelled"
    mock_context.return_value = {"licence": TEST_LICENCE, "authority": TEST_AUTHORITY}
    dom = get_dom_parser(test_licence_application_cancelled_page_url)
    heading_text = dom.get_by_test_id("page-heading").get_text()

    assert heading_text == f"{TEST_LICENCE.name} from {TEST_AUTHORITY.full_name}"


def test_page_has_4_steps(
    get_dom_parser, test_licence_application_cancelled_page_url, mock_context, mock_payment_status
):
    mock_payment_status.return_value = "cancelled"
    mock_context.return_value = {
        "step": "4",
        "steps": "4",
    }
    dom = get_dom_parser(test_licence_application_cancelled_page_url)
    steps_text = dom.get_by_test_id("steps").get_text()

    assert "Step 4 of 4" in steps_text


def test_page_has_licence_name(
    get_dom_parser, test_licence_application_cancelled_page_url, mock_context, mock_payment_status
):
    mock_payment_status.return_value = "cancelled"
    mock_context.return_value = {"licence": TEST_LICENCE}
    dom = get_dom_parser(test_licence_application_cancelled_page_url)
    licence_text = dom.get_by_test_id("cancelled-licence").get_text()

    assert TEST_LICENCE.name in licence_text


def test_page_has_no_message_if_empty(
    get_dom_parser, test_licence_application_cancelled_page_url, mock_context, mock_payment_status
):
    mock_payment_status.return_value = "cancelled"
    mock_context.return_value = {"message": ""}
    dom = get_dom_parser(test_licence_application_cancelled_page_url)
    licence_text = dom.get_by_test_id("cancelled-licence").get_text()

    assert "Message:" not in licence_text


def test_page_has_message_if_not_empty(
    get_dom_parser, test_licence_application_cancelled_page_url, mock_context, mock_payment_status
):
    mock_payment_status.return_value = "cancelled"
    mock_context.return_value = {"message": "hello world"}
    dom = get_dom_parser(test_licence_application_cancelled_page_url)
    licence_text = dom.get_by_test_id("cancelled-licence").get_text()

    assert "Message: hello world" in licence_text


def test_page_has_department_contact_details(
    get_dom_parser, test_licence_application_cancelled_page_url, mock_context, mock_payment_status
):
    mock_context.return_value = {"department": TEST_DEPARTMENT}
    dom = get_dom_parser(test_licence_application_cancelled_page_url)

    department_contact = dom.get_by_test_id("department-contact").get_text()

    assert TEST_AUTHORITY.contact_details.phone_number in department_contact
    assert TEST_AUTHORITY.contact_details.email in department_contact
    assert TEST_AUTHORITY.contact_details.post_code in department_contact
    assert TEST_AUTHORITY.contact_details.city in department_contact


def test_page_displays_licence_finder_url_under_next_steps(
    get_dom_parser, test_licence_application_cancelled_page_url, mock_context, mock_payment_status
):
    url = f"{BASE_URL}/apply-for-a-licence"
    mock_context.return_value = {"licence_finder_url": url}
    dom = get_dom_parser(test_licence_application_cancelled_page_url)
    next_steps = dom.get_by_test_id("next-steps")
    link = next_steps.find("a")

    assert link["href"] == url
