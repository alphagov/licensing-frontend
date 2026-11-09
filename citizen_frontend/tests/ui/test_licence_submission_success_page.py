from copy import deepcopy

import pytest
from conftest import (
    TEST_AUTHORITY,
    TEST_CUSTOMISATION_FIXED_FEE,
    TEST_CUSTOMISATION_NO_FEE,
    TEST_DEPARTMENT,
    TEST_LICENCE,
    TEST_LICENCE_APPLICATION,
    TEST_PAYMENT,
)


@pytest.fixture
def test_licence_submission_success_page_url(live_server):
    return f"{live_server.url}/apply-for-a-licence/payment/licenceCallback?id=gds-test-1813030"


@pytest.fixture
def mock_context(mocker):
    yield mocker.patch("citizen_frontend.controllers.payment_licence_callback.mock_payment_licence_callback_context")


def test_page_has_correct_headings(get_dom_parser, test_licence_submission_success_page_url, mock_context):
    mock_context.return_value = {"licence_name": TEST_LICENCE.name, "authority": TEST_AUTHORITY}
    dom = get_dom_parser(test_licence_submission_success_page_url)
    heading_text = dom.get_by_test_id("page-heading").get_text()

    assert heading_text == f"{TEST_LICENCE.name} from {TEST_AUTHORITY.full_name}"


def test_page_has_4_steps_when_licence_has_a_fee(
    get_dom_parser, test_licence_submission_success_page_url, mock_context
):
    mock_context.return_value = {
        "published_customisation": TEST_CUSTOMISATION_FIXED_FEE,
        "is_paid": True,
        "step": "4",
    }
    dom = get_dom_parser(test_licence_submission_success_page_url)
    steps_text = dom.get_by_test_id("steps").get_text()

    assert "Step 4 of 4" in steps_text


def test_page_has_3_steps_when_licence_has_no_fee(
    get_dom_parser, test_licence_submission_success_page_url, mock_context
):
    mock_context.return_value = {
        "published_customisation": TEST_CUSTOMISATION_NO_FEE,
        "is_paid": False,
        "step": "3",
    }
    dom = get_dom_parser(test_licence_submission_success_page_url)
    steps_text = dom.get_by_test_id("steps").get_text()

    assert "Step 3 of 3" in steps_text


def test_page_application_confirmation_when_licence_fee_defined(
    get_dom_parser, test_licence_submission_success_page_url, mock_context
):
    mock_context.return_value = {
        "published_customisation": TEST_CUSTOMISATION_FIXED_FEE,
        "is_paid": True,
    }
    dom = get_dom_parser(test_licence_submission_success_page_url)
    text = dom.get_by_test_id("application-confirmation").get_text()

    assert "fee has been paid" in text
    assert "We have received your application" in text


def test_page_application_confirmation_when_no_licence_fee_defined(
    get_dom_parser, test_licence_submission_success_page_url, mock_context
):
    mock_context.return_value = {
        "published_customisation": TEST_CUSTOMISATION_NO_FEE,
        "is_paid": False,
    }
    dom = get_dom_parser(test_licence_submission_success_page_url)
    text = dom.get_by_test_id("application-confirmation").get_text()

    assert "fee has been paid" not in text
    assert "We have received your application" in text


def test_page_has_correct_email_for_confirmation(
    get_dom_parser, test_licence_submission_success_page_url, mock_context
):
    mock_context.return_value = {"application": TEST_LICENCE_APPLICATION}
    dom = get_dom_parser(test_licence_submission_success_page_url)
    email_text = dom.get_by_test_id("email-confirmation").get_text()

    assert "test@email.com" in email_text


def test_page_has_payment_reference_for_provider_when_licence_has_a_paid_fee(
    get_dom_parser, test_licence_submission_success_page_url, mock_context
):
    mock_context.return_value = {
        "fee_required": True,
        "is_paid": True,
        "payment": TEST_PAYMENT,
    }
    dom = get_dom_parser(test_licence_submission_success_page_url)
    payment_reference_text = dom.get_by_test_id("payment-reference").get_text()

    assert "WorldPay" in payment_reference_text
    assert "test transaction id" in payment_reference_text


def test_page_has_no_payment_reference_when_licence_has_no_fee(
    get_dom_parser, test_licence_submission_success_page_url, mock_context
):
    mock_context.return_value = {
        "published_customisation": TEST_CUSTOMISATION_NO_FEE,
        "is_paid": False,
        "payment": None,
    }
    dom = get_dom_parser(test_licence_submission_success_page_url)
    payment_reference_text = dom.get_by_test_id("payment-reference").get_text()

    assert "WorldPay" not in payment_reference_text
    assert "test transaction id" not in payment_reference_text


def test_page_has_application_reference(get_dom_parser, test_licence_submission_success_page_url, mock_context):
    mock_context.return_value = {"application": TEST_LICENCE_APPLICATION}
    dom = get_dom_parser(test_licence_submission_success_page_url)
    application_reference_text = dom.get_by_test_id("application-reference").get_text()

    assert TEST_LICENCE_APPLICATION.application_reference_number in application_reference_text


def test_page_has_notified_authority(get_dom_parser, test_licence_submission_success_page_url, mock_context):
    mock_context.return_value = {
        "application": TEST_LICENCE_APPLICATION,
    }
    dom = get_dom_parser(test_licence_submission_success_page_url)
    what_next_text = dom.get_by_test_id("what-next").get_text()

    assert TEST_LICENCE_APPLICATION.authority in what_next_text


def test_page_references_online_supporting_documents_when_all_are_required(
    get_dom_parser, test_licence_submission_success_page_url, mock_context
):
    mock_context.return_value = {
        "application": TEST_LICENCE_APPLICATION,
        "all_supporting_documents_required": True,
        "has_supporting_documents": True,
    }
    dom = get_dom_parser(test_licence_submission_success_page_url)
    what_next_text = dom.get_by_test_id("what-next").get_text()

    assert "and supporting documents" in what_next_text
    assert "where applicable" not in what_next_text


def test_page_references_online_supporting_documents_when_not_all_are_required(
    get_dom_parser, test_licence_submission_success_page_url, mock_context
):
    mock_context.return_value = {
        "application": TEST_LICENCE_APPLICATION,
        "all_supporting_documents_required": False,
        "has_supporting_documents": True,
    }
    dom = get_dom_parser(test_licence_submission_success_page_url)
    what_next_text = dom.get_by_test_id("what-next").get_text()

    assert "and supporting documents, where applicable," in what_next_text


def test_page_does_not_reference_online_supporting_documents_when_none_provided(
    get_dom_parser, test_licence_submission_success_page_url, mock_context
):
    mock_context.return_value = {
        "application": TEST_LICENCE_APPLICATION,
        "all_supporting_documents_required": False,
        "has_supporting_documents": False,
    }
    dom = get_dom_parser(test_licence_submission_success_page_url)
    what_next_text = dom.get_by_test_id("what-next").get_text()

    assert "and supporting documents, where applicable," not in what_next_text


def test_page_has_expected_processing_date_in_correct_format_when_one_exists(
    get_dom_parser, test_licence_submission_success_page_url, mock_context
):
    formatted_date = TEST_LICENCE_APPLICATION.expected_processing_date.strftime("%d %B %Y")
    mock_context.return_value = {
        "application": TEST_LICENCE_APPLICATION,
        "expected_processing_date": TEST_LICENCE_APPLICATION.expected_processing_date.strftime("%d %B %Y"),
    }
    dom = get_dom_parser(test_licence_submission_success_page_url)
    what_next_text = dom.get_by_test_id("what-next").get_text()

    assert formatted_date in what_next_text
    assert "within 30 days." not in what_next_text


def test_page_has_30_day_processing_date_when_no_expected_processing_date_exists(
    get_dom_parser, test_licence_submission_success_page_url, mock_context
):
    application_without_expected_processing_date = deepcopy(TEST_LICENCE_APPLICATION)
    application_without_expected_processing_date.expected_processing_date = None
    mock_context.return_value = {"application": application_without_expected_processing_date}
    dom = get_dom_parser(test_licence_submission_success_page_url)
    what_next_text = dom.get_by_test_id("what-next").get_text()

    assert "within 30 days." in what_next_text


def test_page_refers_to_tacit_consent_when_applicable(
    get_dom_parser, test_licence_submission_success_page_url, mock_context
):
    mock_context.return_value = {
        "application": TEST_LICENCE_APPLICATION,
        "expected_processing_date": TEST_LICENCE_APPLICATION.expected_processing_date.strftime("%d %B %Y"),
    }
    dom = get_dom_parser(test_licence_submission_success_page_url)
    what_next_text = dom.get_by_test_id("what-next").get_text()

    assert "tacit consent applies" in what_next_text


def test_page_does_not_refer_to_tacit_consent_when_not_applicable(
    get_dom_parser, test_licence_submission_success_page_url, mock_context
):
    application_without_tacit_consent = deepcopy(TEST_LICENCE_APPLICATION)
    application_without_tacit_consent.has_tacit_consent = False
    mock_context.return_value = {
        "application": application_without_tacit_consent,
        "expected_processing_date": application_without_tacit_consent.expected_processing_date.strftime("%d %B %Y"),
    }
    dom = get_dom_parser(test_licence_submission_success_page_url)
    what_next_text = dom.get_by_test_id("what-next").get_text()

    assert "tacit consent applies" not in what_next_text


def test_page_has_instructions_for_posting_supporting_documents_when_not_provided_online(
    get_dom_parser, test_licence_submission_success_page_url, mock_context
):
    application_with_posted_docs = deepcopy(TEST_LICENCE_APPLICATION)
    application_with_posted_docs.has_supporting_documents_online = False
    mock_context.return_value = {
        "application": application_with_posted_docs,
    }
    dom = get_dom_parser(test_licence_submission_success_page_url)
    what_next_text = dom.get_by_test_id("what-next").get_text()

    assert application_with_posted_docs.authority in what_next_text
    assert "You must now send in any supporting documentation to the address below." in what_next_text


def test_page_has_processing_time_for_when_posting_supporting_documents_when_not_provided_online(
    get_dom_parser, test_licence_submission_success_page_url, mock_context
):
    mock_context.return_value = {
        "processing_days": "30 working days",
    }
    dom = get_dom_parser(test_licence_submission_success_page_url)
    what_next_text = dom.get_by_test_id("what-next").get_text()

    assert "30 working days" in what_next_text


# TODO: Add mock for this logic


def test_page_displays_department_contact_details(
    get_dom_parser, test_licence_submission_success_page_url, mock_context
):
    mock_context.return_value = {"department": TEST_DEPARTMENT}
    dom = get_dom_parser(test_licence_submission_success_page_url)
    department_contact = dom.get_by_test_id("department-contact").get_text()

    assert TEST_AUTHORITY.contact_details.phone_number in department_contact
    assert TEST_AUTHORITY.contact_details.email in department_contact
    assert TEST_AUTHORITY.contact_details.post_code in department_contact
    assert TEST_AUTHORITY.contact_details.city in department_contact


def test_page_displays_licence_finder_url_under_next_steps(get_dom_parser, test_licence_submission_success_page_url):
    url = "https://www.gov.uk/licence-finder"
    dom = get_dom_parser(test_licence_submission_success_page_url)
    next_steps = dom.get_by_test_id("next-steps")
    link = next_steps.find("a")

    assert link["href"] == url
