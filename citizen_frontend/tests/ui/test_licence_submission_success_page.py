from copy import deepcopy

import pytest
from conftest import (
    TEST_AUTHORITY,
    TEST_CUSTOMISATION_FIXED_FEE,
    TEST_CUSTOMISATION_VARIABLE_FEE,
    TEST_LICENCE,
    TEST_LICENCE_APPLICATION,
    TEST_PAYMENT,
)


@pytest.fixture
def test_licence_submission_success_page_url(live_server):
    return f"{live_server.url}/apply-for-a-licence/payment/licenceCallback?id=gds-test-1813030"


@pytest.fixture
def mock_context(mocker):
    yield mocker.patch("citizen_frontend.views.mock_payment_licence_callback_context")


def test_page_has_correct_headings(get_dom_parser, test_licence_submission_success_page_url, mock_context):
    mock_context.return_value = {"licence_name": TEST_LICENCE.name, "authority_name": TEST_AUTHORITY.full_name}
    dom = get_dom_parser(test_licence_submission_success_page_url)
    heading_text = dom.get_by_test_id("page-heading").get_text()

    assert heading_text == f"{TEST_LICENCE.name} from {TEST_AUTHORITY.full_name}"


def test_page_has_4_steps_when_licence_has_a_fee(
    get_dom_parser, test_licence_submission_success_page_url, mock_context
):
    pass


def test_page_has_3_steps_when_licence_has_no_fee():
    pass


def test_page_application_confirmation_when_licence_fee_defined(
    get_dom_parser, test_licence_submission_success_page_url, mock_context
):
    mock_context.return_value = {
        "customisation": TEST_CUSTOMISATION_FIXED_FEE,
        "is_paid": True,
    }
    dom = get_dom_parser(test_licence_submission_success_page_url)
    text = dom.get_by_test_id("application-confirmation").get_text()

    assert "fee has been paid" in text
    assert "We have received your application" in text


def test_page_application_confirmation_when_no_licence_fee_defined(
    get_dom_parser, test_licence_submission_success_page_url, mock_context
):
    customisation_no_fee = deepcopy(TEST_CUSTOMISATION_VARIABLE_FEE)
    customisation_no_fee.is_fee_required = False
    mock_context.return_value = {
        "customisation": customisation_no_fee,
        "is_paid": False,
    }
    dom = get_dom_parser(test_licence_submission_success_page_url)
    text = dom.get_by_test_id("application-confirmation").get_text()

    assert "fee has been paid" not in text
    assert "We have received your application" in text


def test_page_has_correct_email_for_confirmation(
    get_dom_parser, test_licence_submission_success_page_url, mock_context
):
    mock_context.return_value = {
        "licence_application": TEST_LICENCE_APPLICATION,
    }
    dom = get_dom_parser(test_licence_submission_success_page_url)
    email_text = dom.get_by_test_id("email-confirmation").get_text()

    assert "test@email.com" in email_text


def test_page_has_payment_reference_for_provider_when_licence_has_a_paid_fee(
    get_dom_parser, test_licence_submission_success_page_url, mock_context
):
    mock_context.return_value = {
        "customisation": TEST_CUSTOMISATION_FIXED_FEE,
        "is_paid": True,
        "payment": TEST_PAYMENT,
        "transaction_id_exists": True,
        "payment_provider_exists": True,
    }
    dom = get_dom_parser(test_licence_submission_success_page_url)
    payment_reference_text = dom.get_by_test_id("payment-reference").get_text()

    assert "WorldPay" in payment_reference_text
    assert "test transaction id" in payment_reference_text


def test_page_has_no_payment_reference_when_licence_has_no_fee(
    get_dom_parser, test_licence_submission_success_page_url, mock_context
):
    customisation_no_fee = deepcopy(TEST_CUSTOMISATION_VARIABLE_FEE)
    customisation_no_fee.is_fee_required = False
    mock_context.return_value = {
        "customisation": customisation_no_fee,
        "is_paid": False,
        "transaction_id_exists": False,
        "payment_provider_exists": False,
    }
    dom = get_dom_parser(test_licence_submission_success_page_url)
    payment_reference_text = dom.get_by_test_id("payment-reference").get_text()

    assert "WorldPay" not in payment_reference_text
    assert "test transaction id" not in payment_reference_text


def test_page_has_application_reference(get_dom_parser, test_licence_submission_success_page_url, mock_context):
    mock_context.return_value = {
        "licence_application": TEST_LICENCE_APPLICATION,
    }
    dom = get_dom_parser(test_licence_submission_success_page_url)
    application_reference_text = dom.get_by_test_id("application-reference").get_text()

    assert "test application reference number" in application_reference_text


def test_page_has_notified_authority(get_dom_parser, test_licence_submission_success_page_url, mock_context):
    mock_context.return_value = {
        "licence_application": TEST_LICENCE_APPLICATION,
    }
    dom = get_dom_parser(test_licence_submission_success_page_url)
    what_next_text = dom.get_by_test_id("what-next").get_text()

    assert TEST_AUTHORITY.name in what_next_text


def test_page_references_online_supporting_documents_when_not_all_are_required():
    pass


def test_page_does_not_reference_online_supporting_documents_when_none_provided():
    pass


def test_page_has_expected_processing_date_in_correct_format_when_one_exists():
    pass


def test_page_has_30_day_processing_date_when_no_expected_processing_date_exists():
    pass


def test_page_refers_to_tacit_consent_when_applicable():
    pass


def test_page_has_instructions_for_posting_supporting_documents_when_not_provided_online():
    pass


def test_page_has_processing_time_for_when_posting_supporting_documents_when_not_provided_online():
    pass


def test_page_displays_department_contact_details():
    pass


def test_page_displays_licence_finder_url_under_next_steps():
    pass
