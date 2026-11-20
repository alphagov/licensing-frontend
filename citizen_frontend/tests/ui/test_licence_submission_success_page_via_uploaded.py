from copy import deepcopy

import pytest
from common.models.shared_models import SupportingDocumentDefinition
from conftest import (
    TEST_AUTHORITY,
    TEST_CUSTOMISATION_NO_FEE,
    TEST_DEPARTMENT,
    TEST_INTERACTION,
    TEST_LICENCE,
    TEST_LICENCE_APPLICATION,
)


@pytest.fixture(autouse=True)
def setup_success_page(session_client, mock_get_department):
    pass


@pytest.fixture
def test_uploaded_success_url(live_server):
    return f"{live_server.url}/apply-for-a-licence/uploaded?id=ApplicationRef1"


@pytest.fixture
def mock_get_details_return_values(mock_get_details):
    mock_get_details.return_value = (
        TEST_LICENCE_APPLICATION,
        TEST_LICENCE,
        TEST_AUTHORITY,
        TEST_INTERACTION,
        TEST_CUSTOMISATION_NO_FEE,
    )
    return mock_get_details


@pytest.fixture
def mock_uploaded_context(mocker):
    yield mocker.patch("citizen_frontend.controllers.application_uploaded.licence_submission_success_page")


@pytest.fixture
def mock_get_department(mocker):
    yield mocker.patch("citizen_frontend.services.page_context_builder.get_department", return_value=TEST_DEPARTMENT)


def test_page_has_correct_headings(get_dom_parser, test_uploaded_success_url, mock_get_details_return_values):
    dom = get_dom_parser(test_uploaded_success_url)
    heading_text = dom.get_by_test_id("page-heading").get_text()

    assert heading_text == f"{TEST_LICENCE.name} from {TEST_AUTHORITY.full_name}"


def test_page_is_step_3_of_3(get_dom_parser, test_uploaded_success_url, mock_get_details_return_values):
    dom = get_dom_parser(test_uploaded_success_url)
    steps_text = dom.get_by_test_id("steps").get_text()

    assert "Step 3 of 3" in steps_text


def test_page_application_confirmation_when_no_licence_fee_defined(
    get_dom_parser, test_uploaded_success_url, mock_get_details_return_values
):
    dom = get_dom_parser(test_uploaded_success_url)
    text = dom.get_by_test_id("application-confirmation").get_text()

    assert "fee has been paid" not in text
    assert "We have received your application" in text


def test_page_has_correct_email_for_confirmation(
    get_dom_parser, test_uploaded_success_url, mock_get_details_return_values
):
    dom = get_dom_parser(test_uploaded_success_url)
    email_text = dom.get_by_test_id("email-confirmation").get_text()

    assert "test@email.com" in email_text


def test_page_has_no_payment_reference_when_licence_has_no_fee(
    get_dom_parser, test_uploaded_success_url, mock_get_details_return_values
):
    dom = get_dom_parser(test_uploaded_success_url)
    payment_reference_text = dom.get_by_test_id("payment-reference").get_text()

    assert "WorldPay" not in payment_reference_text
    assert "test transaction id" not in payment_reference_text


def test_page_has_application_reference(get_dom_parser, test_uploaded_success_url, mock_get_details_return_values):
    dom = get_dom_parser(test_uploaded_success_url)
    application_reference_text = dom.get_by_test_id("application-reference").get_text()

    assert TEST_LICENCE_APPLICATION.application_reference_number in application_reference_text


def test_page_has_notified_authority(get_dom_parser, test_uploaded_success_url, mock_get_details_return_values):
    dom = get_dom_parser(test_uploaded_success_url)
    what_next_text = dom.get_by_test_id("what-next").get_text()

    assert TEST_LICENCE_APPLICATION.authority in what_next_text


def test_page_references_online_supporting_documents_when_all_are_required(
    get_dom_parser, test_uploaded_success_url, mock_get_details
):
    customisation_mandatory_docs = deepcopy(TEST_CUSTOMISATION_NO_FEE)
    customisation_mandatory_docs.supporting_document_definitions = [
        SupportingDocumentDefinition(name="test", is_mandatory=True),
        SupportingDocumentDefinition(name="test2", is_mandatory=True),
        SupportingDocumentDefinition(name="test3", is_mandatory=True),
    ]
    mock_get_details.return_value = (
        TEST_LICENCE_APPLICATION,
        TEST_LICENCE,
        TEST_AUTHORITY,
        TEST_INTERACTION,
        customisation_mandatory_docs,
    )
    dom = get_dom_parser(test_uploaded_success_url)
    what_next_text = dom.get_by_test_id("what-next").get_text()

    assert "and supporting documents" in what_next_text
    assert "where applicable" not in what_next_text


def test_page_references_online_supporting_documents_when_not_all_are_required(
    get_dom_parser, test_uploaded_success_url, mock_get_details_return_values
):
    dom = get_dom_parser(test_uploaded_success_url)
    what_next_text = dom.get_by_test_id("what-next").get_text()

    assert "and supporting documents, where applicable," in what_next_text


def test_page_does_not_reference_online_supporting_documents_when_none_provided(
    get_dom_parser, test_uploaded_success_url, mock_get_details
):
    customisation_no_mandatory_docs = deepcopy(TEST_CUSTOMISATION_NO_FEE)
    customisation_no_mandatory_docs.supporting_document_definitions = []
    mock_get_details.return_value = (
        TEST_LICENCE_APPLICATION,
        TEST_LICENCE,
        TEST_AUTHORITY,
        TEST_INTERACTION,
        customisation_no_mandatory_docs,
    )
    dom = get_dom_parser(test_uploaded_success_url)
    what_next_text = dom.get_by_test_id("what-next").get_text()

    assert "and supporting documents, where applicable," not in what_next_text


def test_page_has_expected_processing_date_in_correct_format_when_one_exists(
    get_dom_parser, test_uploaded_success_url, mock_get_details_return_values
):
    formatted_date = TEST_LICENCE_APPLICATION.expected_processing_date.strftime("%d %B %Y")
    dom = get_dom_parser(test_uploaded_success_url)
    what_next_text = dom.get_by_test_id("what-next").get_text()

    assert formatted_date in what_next_text
    assert "within 30 days." not in what_next_text


def test_page_has_30_day_processing_date_when_no_expected_processing_date_exists(
    get_dom_parser, test_uploaded_success_url, mock_get_details
):
    application_without_expected_processing_date = deepcopy(TEST_LICENCE_APPLICATION)
    application_without_expected_processing_date.expected_processing_date = None
    mock_get_details.return_value = (
        application_without_expected_processing_date,
        TEST_LICENCE,
        TEST_AUTHORITY,
        TEST_INTERACTION,
        TEST_CUSTOMISATION_NO_FEE,
    )
    dom = get_dom_parser(test_uploaded_success_url)
    what_next_text = dom.get_by_test_id("what-next").get_text()

    assert "within 30 days." in what_next_text


def test_page_refers_to_tacit_consent_when_applicable(
    get_dom_parser, test_uploaded_success_url, mock_get_details_return_values
):
    dom = get_dom_parser(test_uploaded_success_url)
    what_next_text = dom.get_by_test_id("what-next").get_text()

    assert "tacit consent applies" in what_next_text


def test_page_does_not_refer_to_tacit_consent_when_not_applicable(
    get_dom_parser, test_uploaded_success_url, mock_get_details
):
    application_without_tacit_consent = deepcopy(TEST_LICENCE_APPLICATION)
    application_without_tacit_consent.has_tacit_consent = False
    mock_get_details.return_value = (
        application_without_tacit_consent,
        TEST_LICENCE,
        TEST_AUTHORITY,
        TEST_INTERACTION,
        TEST_CUSTOMISATION_NO_FEE,
    )
    dom = get_dom_parser(test_uploaded_success_url)
    what_next_text = dom.get_by_test_id("what-next").get_text()

    assert "tacit consent applies" not in what_next_text


def test_page_has_instructions_for_posting_supporting_documents_when_not_provided_online(
    get_dom_parser, test_uploaded_success_url, mock_get_details
):
    application_with_posted_docs = deepcopy(TEST_LICENCE_APPLICATION)
    application_with_posted_docs.has_supporting_documents_online = False
    mock_get_details.return_value = (
        application_with_posted_docs,
        TEST_LICENCE,
        TEST_AUTHORITY,
        TEST_INTERACTION,
        TEST_CUSTOMISATION_NO_FEE,
    )
    dom = get_dom_parser(test_uploaded_success_url)
    what_next_text = dom.get_by_test_id("what-next").get_text()

    assert application_with_posted_docs.authority in what_next_text
    assert "You must now send in any supporting documentation to the address below." in what_next_text


def test_page_has_processing_time_for_when_posting_supporting_documents_when_not_provided_online(
    get_dom_parser, test_uploaded_success_url, mock_get_details
):
    application_with_posted_docs = deepcopy(TEST_LICENCE_APPLICATION)
    application_with_posted_docs.has_supporting_documents_online = False
    mock_get_details.return_value = (
        application_with_posted_docs,
        TEST_LICENCE,
        TEST_AUTHORITY,
        TEST_INTERACTION,
        TEST_CUSTOMISATION_NO_FEE,
    )
    dom = get_dom_parser(test_uploaded_success_url)
    what_next_text = dom.get_by_test_id("what-next").get_text()

    assert "30 working days" in what_next_text


def test_page_displays_department_contact_details(
    get_dom_parser, test_uploaded_success_url, mock_get_details_return_values
):
    dom = get_dom_parser(test_uploaded_success_url)
    department_contact = dom.get_by_test_id("department-contact").get_text()

    assert TEST_AUTHORITY.contact_details.phone_number in department_contact
    assert TEST_AUTHORITY.contact_details.email in department_contact
    assert TEST_AUTHORITY.contact_details.post_code in department_contact
    assert TEST_AUTHORITY.contact_details.city in department_contact


def test_page_displays_licence_finder_url_under_next_steps(
    get_dom_parser, test_uploaded_success_url, mock_get_details_return_values
):
    url = "https://www.gov.uk/licence-finder"
    dom = get_dom_parser(test_uploaded_success_url)
    next_steps = dom.get_by_test_id("next-steps")
    link = next_steps.find("a")

    assert link["href"] == url
