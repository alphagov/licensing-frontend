import pytest
from conftest import TEST_AUTHORITY, TEST_CUSTOMISATION_FIXED_FEE, TEST_LICENCE, TEST_PAYMENT


@pytest.fixture
def test_licence_application_prepayment_page_url(live_server):
    return f"{live_server}/apply-for-a-licence/uploaded"


@pytest.fixture
def mock_context(mocker):
    yield mocker.patch("citizen_frontend.controllers.prepayment.mock_prepayment_context")


def test_page_has_correct_headings(get_dom_parser, test_licence_application_prepayment_page_url, mock_context):
    mock_context.return_value = {"licence_name": TEST_LICENCE.name, "authority": TEST_AUTHORITY}
    dom = get_dom_parser(test_licence_application_prepayment_page_url)
    heading_text = dom.get_by_test_id("page-heading").get_text()

    assert heading_text == f"{TEST_LICENCE.name} from {TEST_AUTHORITY.full_name}"


def test_page_is_step_3_of_4(get_dom_parser, test_licence_application_prepayment_page_url, mock_context):
    mock_context.return_value = {"published_customisation": TEST_CUSTOMISATION_FIXED_FEE, "step": "3"}
    dom = get_dom_parser(test_licence_application_prepayment_page_url)
    steps_text = dom.get_by_test_id("steps").get_text()

    assert "Step 3 of 4" in steps_text


def test_page_has_correct_fee_amount(get_dom_parser, test_licence_application_prepayment_page_url, mock_context):
    mock_context.return_value = {"payment": TEST_PAYMENT}
    dom = get_dom_parser(test_licence_application_prepayment_page_url)
    fee_text = dom.get_by_test_id("fee-info").get_text()

    assert "£5.00" in fee_text


def test_page_references_correct_payment_provider(
    get_dom_parser, test_licence_application_prepayment_page_url, mock_context
):
    mock_context.return_value = {"payment": TEST_PAYMENT}
    dom = get_dom_parser(test_licence_application_prepayment_page_url)
    fee_text = dom.get_by_test_id("fee-info").get_text()

    assert "WorldPay" in fee_text


def test_page_has_button_to_continue_to_provider(
    get_dom_parser, test_licence_application_prepayment_page_url, mock_context
):
    mock_context.return_value = {"payment": TEST_PAYMENT}
    dom = get_dom_parser(test_licence_application_prepayment_page_url)
    button_text = dom.get_by_test_id("pay-button").get_text()

    assert "Continue to WorldPay website" in button_text
