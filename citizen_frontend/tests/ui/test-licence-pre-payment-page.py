import pytest
from conftest import TEST_AUTHORITY, TEST_LICENCE


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


def test_page_is_step_3_of_4():
    pass


def test_page_has_correct_fee_amount():
    pass


def test_page_references_correct_payment_provider():
    pass


def test_page_has_button_to_continue_to_provider():
    pass
