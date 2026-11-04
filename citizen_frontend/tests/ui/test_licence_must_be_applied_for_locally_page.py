from copy import deepcopy

import pytest
from conftest import LICENCE_INTERACTION_CONTEXT


@pytest.fixture
def mock_lookup_service(mocker):
    service = mocker.MagicMock()
    mocker.patch("citizen_frontend.controllers.begin_application.LicenceLookupService", return_value=service)
    yield service


modified_context = deepcopy(LICENCE_INTERACTION_CONTEXT)
modified_context[3].using_gov_uk = False

context_licence_details_with_no_authority_url = deepcopy(modified_context)
context_licence_details_with_no_authority_url[3].authority_url = False


def test_licence_must_be_applied_for_locally_when_url_available_displays_link(
    get_dom_parser, test_introduction_page_url, mock_lookup_service
):

    mock_lookup_service.get_licence_interaction_context.return_value = modified_context

    dom = get_dom_parser(test_introduction_page_url)
    anchor_tag = dom.get_by_test_id("authority_url")
    assert anchor_tag["href"] == modified_context[3].authority_url


def test_licence_must_be_applied_for_locally_when_url_available_hides_no_authority_url_text(
    get_dom_parser, test_introduction_page_url, mock_lookup_service
):

    mock_lookup_service.get_licence_interaction_context.return_value = modified_context

    dom = get_dom_parser(test_introduction_page_url)
    no_authority = dom.get_by_test_id("no_authority_link")
    assert not no_authority


def test_licence_must_be_applied_for_locally_when_url_not_available_hides_url(
    get_dom_parser, test_introduction_page_url, mock_lookup_service
):
    mock_lookup_service.get_licence_interaction_context.return_value = context_licence_details_with_no_authority_url

    dom = get_dom_parser(test_introduction_page_url)
    anchor_tag = dom.get_by_test_id("authority_url")
    assert not anchor_tag


def test_licence_must_be_applied_for_locally_when_url_not_available_has_correct_text(
    get_dom_parser, test_introduction_page_url, mock_lookup_service
):
    mock_lookup_service.get_licence_interaction_context.return_value = context_licence_details_with_no_authority_url

    dom = get_dom_parser(test_introduction_page_url)
    no_authority_text = dom.get_by_test_id("no_authority_link").get_text()
    no_authority_text_normalised = " ".join(no_authority_text.split())
    assert (
        no_authority_text_normalised
        == "Unfortunately, we don't have a direct link for this Authority, try searching for it on your favourite"
        " search engine"
    )
