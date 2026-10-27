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


def test_page_has_payment_reference_when_licence_has_a_fee():
    pass


def test_page_has_no_payment_reference_when_licence_has_no_fee():
    pass


def test_page_has_correct_email_for_confirmation():
    pass


def test_page_has_application_reference():
    pass


def test_page_has_decision_date():
    pass
