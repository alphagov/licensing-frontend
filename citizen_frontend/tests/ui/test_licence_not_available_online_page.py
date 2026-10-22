def test_email_visible_when_authority_has_email(
    get_dom_parser,
    test_introduction_page_url,
    mock_find_published_customisation_returns_none,
    mock_get_licence_interaction_context,
):
    _, authority, _, _ = mock_get_licence_interaction_context.return_value
    dom = get_dom_parser(test_introduction_page_url)
    email_anchor_tag = dom.get_by_test_id("email_link")
    assert authority.contact_details.email in email_anchor_tag["href"]


def test_email_not_visible_when_authority_doesnt_have_email(
    get_dom_parser,
    test_introduction_page_url,
    mock_find_published_customisation_returns_none,
    mock_get_licence_interaction_context,
):
    _, authority, _, _ = mock_get_licence_interaction_context.return_value
    authority.contact_details.email = ""
    dom = get_dom_parser(test_introduction_page_url)
    anchor_tag = dom.get_by_test_id("email_link")
    assert not anchor_tag


def test_expected_data_displayed(
    get_dom_parser,
    test_introduction_page_url,
    mock_find_published_customisation_returns_none,
    mock_get_licence_interaction_context,
):
    _, authority, _, _ = mock_get_licence_interaction_context.return_value
    dom = get_dom_parser(test_introduction_page_url)
    page_text = dom.get_text()
    assert authority.contact_details.line_one in page_text
    assert authority.contact_details.line_two in page_text
    assert authority.contact_details.line_three in page_text
    assert authority.contact_details.city in page_text
    assert authority.contact_details.phone_number in page_text


def test_page_displays_when_only_partial_details_available(
    get_dom_parser,
    test_introduction_page_url,
    mock_find_published_customisation_returns_none,
    mock_get_licence_interaction_context,
):
    _, authority, _, _ = mock_get_licence_interaction_context.return_value
    authority.contact_details.line_two = ""
    authority.contact_details.city = None
    dom = get_dom_parser(test_introduction_page_url)
    page_text = dom.get_text()
    assert authority.contact_details.line_one in page_text
    assert authority.contact_details.line_three in page_text
