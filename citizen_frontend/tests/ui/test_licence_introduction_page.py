import os
from urllib.parse import urlparse

from playwright.sync_api import Page, expect

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"


def test_page_has_correct_headings(
    page: Page,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_fixed_fee,
    test_introduction_page_url,
):
    page.goto(test_introduction_page_url)

    expect(page.get_by_test_id("page-heading")).to_contain_text("Test Licence")
    expect(page.get_by_test_id("page-heading")).to_contain_text("Test Authority")
    expect(page.get_by_test_id("action-heading")).to_have_text("Complete the application form")
    expect(page.get_by_test_id("download-heading")).to_have_text("First, download the form")
    expect(page.get_by_test_id("fill-in-heading")).to_have_text("Next, fill in the application form on your computer")
    expect(page.get_by_test_id("before-apply-heading")).to_have_text("Before you apply...")
    expect(page.get_by_test_id("submit-heading")).to_have_text("Now, submit the application")


def test_page_has_4_steps_when_licence_has_fee(
    page: Page,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_fixed_fee,
    test_introduction_page_url,
):
    page.goto(test_introduction_page_url)

    expect(page.get_by_test_id("steps")).to_contain_text("1 of 4")


def test_page_has_3_steps_when_licence_has_no_fee(
    page: Page,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_no_fee,
    test_introduction_page_url,
):
    page.goto(test_introduction_page_url)

    expect(page.get_by_test_id("steps")).to_contain_text("1 of 3")


def test_page_has_fee_amount_when_licence_has_fixed_fee_required(
    page: Page,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_fixed_fee,
    test_introduction_page_url,
):
    page.goto(test_introduction_page_url)

    expect(page.get_by_test_id("fee-amount")).to_contain_text("£5.00")


def test_page_has_no_fee_amount_when_licence_has_no_fee_required(
    page: Page,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_no_fee,
    test_introduction_page_url,
):
    page.goto(test_introduction_page_url)

    expect(page.get_by_test_id("fee-amount")).not_to_be_visible()


def test_page_has_no_fee_amount_when_licence_fee_is_required(
    page: Page,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_variable_fee,
    test_introduction_page_url,
):

    page.goto(test_introduction_page_url)

    expect(page.get_by_test_id("fee-amount")).not_to_be_visible()
    expect(page.get_by_test_id("fee")).to_be_visible()
    expect(page.get_by_test_id("fee")).to_contain_text("There's a fee you'll need to pay for this submission.")


def test_page_has_download_pdf_inset(
    page: Page,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_fixed_fee,
    test_introduction_page_url,
):
    page.goto(test_introduction_page_url)

    adobe_download_link = page.get_by_test_id("adobe-download")
    pdf_download_link = page.get_by_test_id("pdf-download")

    expect(page.get_by_test_id("pdf-inset")).to_contain_class("govuk-inset-text")
    expect(adobe_download_link).to_have_role("link")
    expect(adobe_download_link).to_have_attribute("href", "https://get.adobe.com/uk/reader/")
    expect(pdf_download_link).to_have_role("link")
    expect(pdf_download_link).to_have_attribute("href", "#")


def test_page_has_additional_information_inset_when_both_legislation_and_general_info_urls_available(
    page: Page,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_fixed_fee,
    test_introduction_page_url,
):
    page.goto(test_introduction_page_url)

    general_info_link = page.get_by_test_id("general-information")
    legislation_info_link = page.get_by_test_id("legislation-information")

    expect(page.get_by_test_id("additional-information")).to_contain_text(
        "There is additional information available for this licence that you might find useful"
    )
    # url expected to be the same for both in this specific case
    expect(general_info_link).to_have_role("link")
    expect(general_info_link).to_have_attribute("href", "https://test-guidance.com")
    expect(legislation_info_link).to_have_role("link")
    expect(legislation_info_link).to_have_attribute("href", "https://test-information.com")


def test_page_has_additional_information_inset_when_general_info_url_available(
    page: Page,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_fixed_fee,
    test_introduction_page_url,
):
    mock_find_published_customisation_with_fixed_fee.return_value.guidance_url = "test_url"
    mock_find_published_customisation_with_fixed_fee.return_value.information_url = None
    mock_get_licence_interaction_context.return_value.licence_detail.authority_url = None

    page.goto(test_introduction_page_url)

    expect(page.get_by_test_id("additional-information")).to_be_visible()
    expect(page.get_by_test_id("general-information")).to_be_visible()
    expect(page.get_by_test_id("legislation-information")).not_to_be_visible()


def test_page_has_additional_information_inset_when_legislation_info_url_available(
    page: Page,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_fixed_fee,
    test_introduction_page_url,
):
    mock_find_published_customisation_with_fixed_fee.return_value.information_url = "info_url"
    mock_find_published_customisation_with_fixed_fee.return_value.guidance_url = None

    page.goto(test_introduction_page_url)

    expect(page.get_by_test_id("additional-information")).to_be_visible()
    expect(page.get_by_test_id("general-information")).not_to_be_visible()
    expect(page.get_by_test_id("legislation-information")).to_be_visible()


def test_page_does_not_have_additional_information_inset_when_no_general_info_nor_legislation_info_urls_available(
    page: Page,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_fixed_fee,
    test_introduction_page_url,
):
    mock_find_published_customisation_with_fixed_fee.return_value.information_url = None
    mock_find_published_customisation_with_fixed_fee.return_value.guidance_url = None
    mock_get_licence_interaction_context.return_value.licence_detail.authority_url = None
    page.goto(test_introduction_page_url)

    expect(page.get_by_test_id("additional-information")).not_to_be_visible()
    expect(page.get_by_test_id("general-information")).not_to_be_visible()
    expect(page.get_by_test_id("legislation-information")).not_to_be_visible()


def test_page_has_submit_button(
    page: Page,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_fixed_fee,
    test_introduction_page_url,
):
    page.goto(test_introduction_page_url)
    expected_url = f"{urlparse(test_introduction_page_url).path}/form"
    submit_button = page.get_by_test_id("submit-button")
    expect(submit_button).to_be_visible()
    expect(submit_button).to_have_attribute("href", expected_url)


def test_page_has_supporting_documents_list_when_licence_requires_supporting_documents(
    page: Page,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_fixed_fee,
    test_introduction_page_url,
):
    page.goto(test_introduction_page_url)

    details = page.get_by_test_id("electronic-copies-detail")
    details_text = page.get_by_test_id("electronic-copies-detail-text")

    expect(page.get_by_test_id("supporting-documents")).to_be_visible()
    expect(details).to_be_visible()
    expect(details_text).not_to_be_visible()

    details.click()
    expect(details_text).to_be_visible()


def test_page_marks_non_mandatory_supporting_documents_optional(
    page: Page,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_fixed_fee,
    test_introduction_page_url,
):
    page.goto(test_introduction_page_url)

    mandatory_document = page.get_by_test_id("support-document-1")
    optional_document = page.get_by_test_id("support-document-3")

    expect(mandatory_document).not_to_contain_text("(optional)")
    expect(optional_document).to_contain_text("(optional)")


def test_page_handles_conditional_rendering_of_supporting_documents_when_postal_not_allowed(
    page: Page,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_fixed_fee,
    test_introduction_page_url,
):
    mock_find_published_customisation_with_fixed_fee.return_value.is_postal_allowed = False

    page.goto(test_introduction_page_url)

    details = page.get_by_test_id("electronic-copies-detail")
    details.click()

    expect(page.get_by_test_id("electronic-copies-detail-text")).to_contain_text(
        "you cannot make an online application"
    )


def test_page_handles_conditional_rendering_of_supporting_documents_when_postal_allowed(
    page: Page,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_fixed_fee,
    test_introduction_page_url,
):
    mock_find_published_customisation_with_fixed_fee.return_value.is_postal_allowed = True

    page.goto(test_introduction_page_url)

    details = page.get_by_test_id("electronic-copies-detail")
    details.click()

    expect(page.get_by_test_id("electronic-copies-detail-text")).to_contain_text("you can still apply online")
