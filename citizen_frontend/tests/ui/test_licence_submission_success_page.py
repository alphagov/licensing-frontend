import pytest


@pytest.fixture
def test_licence_submission_success_page_url(live_server):
    return f"{live_server.url}/apply-for-a-licence/payment/licenceCallback?id=gds-test-1813030"


def test_page_has_correct_headings(get_dom_parser, test_licence_submission_success_page_url):
    dom = get_dom_parser(test_licence_submission_success_page_url)
    heading_text = dom.get_by_test_id("page-heading").get_text()

    assert heading_text == "A test licence interaction from GDS which requires a small fee. from GDS Test Authority"


def test_page_has_4_steps_when_licence_has_a_fee():
    pass


def test_page_has_3_steps_when_licence_has_no_fee():
    pass


def test_page_has_payment_confirmation_when_licence_fee_defined():
    pass


def test_page_has_correct_email_for_confirmation():
    pass


def test_page_has_payment_reference_when_licence_has_a_fee():
    pass


def test_page_has_no_payment_reference_when_licence_has_no_fee():
    pass


def test_page_has_application_reference():
    pass


def test_page_references_online_supporting_documents_when_all_are_required():
    pass


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
