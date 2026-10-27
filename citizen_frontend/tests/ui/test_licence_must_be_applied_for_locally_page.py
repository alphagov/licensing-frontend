import pytest


@pytest.fixture
def mock_get_licence_interaction_context_not_using_gov_uk(mock_get_licence_interaction_context):
    _, _, _, licence_details = mock_get_licence_interaction_context.return_value
    licence_details.using_gov_uk = False
    return mock_get_licence_interaction_context


def test_licence_must_be_applied_for_locally_when_url_available_displays_link(
    get_dom_parser, test_introduction_page_url, mock_get_licence_interaction_context_not_using_gov_uk
):
    _, _, _, licence_details = mock_get_licence_interaction_context_not_using_gov_uk.return_value
    dom = get_dom_parser(test_introduction_page_url)
    anchor_tag = dom.get_by_test_id("authority_url")
    assert anchor_tag["href"] == licence_details.authority_url


def test_licence_must_be_applied_for_locally_when_url_available_hides_no_authority_url_text(
    get_dom_parser, test_introduction_page_url, mock_get_licence_interaction_context_not_using_gov_uk
):
    dom = get_dom_parser(test_introduction_page_url)
    no_authority = dom.get_by_test_id("no_authority_link")
    assert not no_authority


def test_licence_must_be_applied_for_locally_when_url_not_available_hides_url(
    get_dom_parser, test_introduction_page_url, mock_get_licence_interaction_context_not_using_gov_uk
):
    _, _, _, licence_details = mock_get_licence_interaction_context_not_using_gov_uk.return_value
    licence_details.authority_url = None
    dom = get_dom_parser(test_introduction_page_url)
    anchor_tag = dom.get_by_test_id("authority_url")
    assert not anchor_tag


def test_licence_must_be_applied_for_locally_when_url_not_available_has_correct_text(
    get_dom_parser, test_introduction_page_url, mock_get_licence_interaction_context_not_using_gov_uk
):
    _, _, _, licence_details = mock_get_licence_interaction_context_not_using_gov_uk.return_value
    licence_details.authority_url = None
    dom = get_dom_parser(test_introduction_page_url)
    no_authority_text = dom.get_by_test_id("no_authority_link").get_text()
    no_authority_text_normalised = " ".join(no_authority_text.split())
    assert (
        no_authority_text_normalised
        == "Unfortunately, we don't have a direct link for this Authority, try searching for it on your favourite"
        " search engine"
    )
