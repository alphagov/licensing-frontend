import os
from urllib.parse import urlparse

import pytest
from bs4 import BeautifulSoup

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"


@pytest.fixture
def get_dom(client):
    def _get(url):
        res = client.get(url)
        soup = BeautifulSoup(res.content, "html.parser")
        soup.get_by_test_id = lambda tid: soup.find(attrs={"data-testid": tid})
        return soup

    return _get


def test_page_has_correct_headings(
    get_dom,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_fixed_fee,
    test_introduction_page_url,
):
    dom = get_dom(test_introduction_page_url)
    heading_text = dom.get_by_test_id("page-heading").get_text()
    assert "Test Licence" in heading_text
    assert "Test Authority" in heading_text
    assert dom.get_by_test_id("action-heading").get_text() == "Complete the application form"
    assert dom.get_by_test_id("download-heading").get_text() == "First, download the form"
    assert dom.get_by_test_id("fill-in-heading").get_text() == "Next, fill in the application form on your computer"
    assert dom.get_by_test_id("before-apply-heading").get_text() == "Before you apply..."
    assert dom.get_by_test_id("submit-heading").get_text() == "Now, submit the application"


def test_page_has_4_steps_when_licence_has_fee(
    get_dom,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_fixed_fee,
    test_introduction_page_url,
):
    dom = get_dom(test_introduction_page_url)

    assert "1 of 4" in dom.get_by_test_id("steps").get_text()


def test_page_has_3_steps_when_licence_has_no_fee(
    get_dom,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_no_fee,
    test_introduction_page_url,
):
    dom = get_dom(test_introduction_page_url)

    assert "1 of 3" in dom.get_by_test_id("steps").get_text()


def test_page_has_fee_amount_when_licence_has_fixed_fee_required(
    get_dom,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_fixed_fee,
    test_introduction_page_url,
):
    dom = get_dom(test_introduction_page_url)

    assert dom.get_by_test_id("fee-amount").get_text() == "£5.00"


def test_page_has_no_fee_amount_when_licence_has_no_fee_required(
    get_dom,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_no_fee,
    test_introduction_page_url,
):
    dom = get_dom(test_introduction_page_url)

    assert dom.get_by_test_id("fee-amount") is None


def test_page_has_no_fee_amount_when_licence_fee_is_required(
    get_dom,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_variable_fee,
    test_introduction_page_url,
):

    dom = get_dom(test_introduction_page_url)

    assert dom.get_by_test_id("fee-amount") is None
    assert dom.get_by_test_id("fee") is not None
    assert "There's a fee you'll need to pay for this submission." in dom.get_by_test_id("fee").get_text()


def test_page_has_download_pdf_inset(
    get_dom,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_fixed_fee,
    test_introduction_page_url,
):
    dom = get_dom(test_introduction_page_url)

    adobe_download_link = dom.get_by_test_id("adobe-download")
    pdf_download_link = dom.get_by_test_id("pdf-download")

    assert "govuk-inset-text" in dom.get_by_test_id("pdf-inset").get("class", [])
    assert adobe_download_link.name == "a"
    assert adobe_download_link["href"] == "https://get.adobe.com/uk/reader/"
    assert pdf_download_link.name == "a"
    assert pdf_download_link["href"] == "#"


def test_page_has_additional_information_inset_when_both_legislation_and_general_info_urls_available(
    get_dom,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_fixed_fee,
    test_introduction_page_url,
):
    dom = get_dom(test_introduction_page_url)

    general_info_link = dom.get_by_test_id("general-information")
    legislation_info_link = dom.get_by_test_id("legislation-information")

    assert (
        "There is additional information available for this licence that you might find useful"
        in dom.get_by_test_id("additional-information").get_text()
    )
    assert general_info_link.name == "a"
    assert general_info_link["href"] == "https://test-guidance.com"
    assert legislation_info_link.name == "a"
    assert legislation_info_link["href"] == "https://test-information.com"


def test_page_has_additional_information_inset_when_general_info_url_available(
    get_dom,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_fixed_fee,
    test_introduction_page_url,
):
    mock_find_published_customisation_with_fixed_fee.return_value.guidance_url = "test_url"
    mock_find_published_customisation_with_fixed_fee.return_value.information_url = None
    _, _, _, licence_details = mock_get_licence_interaction_context.return_value
    licence_details.authority_url = None

    dom = get_dom(test_introduction_page_url)

    assert dom.get_by_test_id("additional-information") is not None
    assert dom.get_by_test_id("general-information") is not None
    assert dom.get_by_test_id("legislation-information") is None


def test_page_has_additional_information_inset_when_legislation_info_url_available(
    get_dom,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_fixed_fee,
    test_introduction_page_url,
):
    mock_find_published_customisation_with_fixed_fee.return_value.information_url = "info_url"
    mock_find_published_customisation_with_fixed_fee.return_value.guidance_url = None

    dom = get_dom(test_introduction_page_url)

    assert dom.get_by_test_id("additional-information") is not None
    assert dom.get_by_test_id("general-information") is None
    assert dom.get_by_test_id("legislation-information") is not None


def test_page_does_not_have_additional_information_inset_when_no_general_info_nor_legislation_info_urls_available(
    get_dom,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_fixed_fee,
    test_introduction_page_url,
):
    mock_find_published_customisation_with_fixed_fee.return_value.information_url = None
    mock_find_published_customisation_with_fixed_fee.return_value.guidance_url = None
    _, _, _, licence_details = mock_get_licence_interaction_context.return_value
    licence_details.authority_url = None
    dom = get_dom(test_introduction_page_url)

    assert dom.get_by_test_id("additional-information") is None
    assert dom.get_by_test_id("general-information") is None
    assert dom.get_by_test_id("legislation-information") is None


def test_page_has_submit_button(
    get_dom,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_fixed_fee,
    test_introduction_page_url,
):
    dom = get_dom(test_introduction_page_url)
    expected_url = f"{urlparse(test_introduction_page_url).path}/form"
    submit_button = dom.get_by_test_id("submit-button")
    assert submit_button is not None
    assert submit_button["href"] == expected_url


def test_page_has_supporting_documents_list_when_licence_requires_supporting_documents(
    get_dom,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_fixed_fee,
    test_introduction_page_url,
):
    dom = get_dom(test_introduction_page_url)

    details = dom.get_by_test_id("electronic-copies-detail")
    details_text = dom.get_by_test_id("electronic-copies-detail-text")

    assert dom.get_by_test_id("supporting-documents") is not None
    assert details is not None
    assert details_text is not None


def test_page_marks_non_mandatory_supporting_documents_optional(
    get_dom,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_fixed_fee,
    test_introduction_page_url,
):
    dom = get_dom(test_introduction_page_url)

    mandatory_document = dom.get_by_test_id("support-document-1")
    optional_document = dom.get_by_test_id("support-document-3")

    assert "(optional)" not in mandatory_document.get_text()
    assert "(optional)" in optional_document.get_text()


def test_page_handles_conditional_rendering_of_supporting_documents_when_postal_not_allowed(
    get_dom,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_fixed_fee,
    test_introduction_page_url,
):
    mock_find_published_customisation_with_fixed_fee.return_value.is_postal_allowed = False

    dom = get_dom(test_introduction_page_url)

    assert "you cannot make an online application" in dom.get_by_test_id("electronic-copies-detail-text").get_text()


def test_page_handles_conditional_rendering_of_supporting_documents_when_postal_allowed(
    get_dom,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_fixed_fee,
    test_introduction_page_url,
):
    mock_find_published_customisation_with_fixed_fee.return_value.is_postal_allowed = True

    dom = get_dom(test_introduction_page_url)

    assert "you can still apply online" in dom.get_by_test_id("electronic-copies-detail-text").get_text()
