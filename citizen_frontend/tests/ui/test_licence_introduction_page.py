import os

import pytest
from conftest import (
    SERVICE_SLUG,
    TEMP_EVENT_SLUG,
    TEST_AUTH_SLUG,
    TEST_FOOD_PREMISES_APPLY_URL,
    TEST_INTERACTION,
    TEST_INTERACTION_SUB_ID,
    TEST_TEMP_EVENT_APPLY_FORM_URL,
    TEST_TEMP_EVENT_APPLY_URL,
)
from playwright.sync_api import Page, expect

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"


@pytest.fixture
def base_context(mocker):
    mock_context = mocker.patch(
        "citizen_frontend.views.get_mocked_context",
    )
    mock_context.return_value = {
        "authority": f"{TEST_AUTH_SLUG}".capitalize(),
        "licence": f"{TEMP_EVENT_SLUG}".replace("-", " ").title(),
        "interation_sub_id": f"{TEST_INTERACTION_SUB_ID}",
        "interaction": f"{TEST_INTERACTION}",
        "steps": 4,
        "authority_slug": f"{TEST_AUTH_SLUG}",
        "licence_slug": f"{TEMP_EVENT_SLUG}",
        "supporting_documents": None,
        "default_declarations": None,
    }
    yield mock_context


def test_page_has_correct_headings(page: Page):
    page.goto(TEST_TEMP_EVENT_APPLY_URL)

    expect(page.get_by_test_id("page-heading")).to_contain_text("Temporary Event Notice")
    expect(page.get_by_test_id("page-heading")).to_contain_text("Winchester")
    expect(page.get_by_test_id("action-heading")).to_have_text("Complete the application form")
    expect(page.get_by_test_id("download-heading")).to_have_text("First, download the form")
    expect(page.get_by_test_id("fill-in-heading")).to_have_text("Next, fill in the form on your computer")
    expect(page.get_by_test_id("before-apply-heading")).to_have_text("Before you apply...")
    expect(page.get_by_test_id("submit-heading")).to_have_text("Now, submit the application")


def test_page_has_4_steps_when_licence_has_fee(page: Page):
    page.goto(TEST_TEMP_EVENT_APPLY_URL)

    expect(page.get_by_test_id("steps")).to_contain_text("1 of 4")


def test_page_has_3_steps_when_licence_has_no_fee(page: Page):
    page.goto(TEST_FOOD_PREMISES_APPLY_URL)

    expect(page.get_by_test_id("steps")).to_contain_text("1 of 3")


def test_page_has_fee_amount_when_licence_has_fixed_fee_required(page: Page):
    page.goto(TEST_TEMP_EVENT_APPLY_URL)

    expect(page.get_by_test_id("fee-amount")).to_contain_text("£21.00")


def test_page_has_no_fee_amount_when_licence_has_no_fee_required(page: Page):
    page.goto(TEST_FOOD_PREMISES_APPLY_URL)

    expect(page.get_by_test_id("fee-amount")).not_to_be_visible()


@pytest.mark.django_db
def test_page_has_no_fee_amount_when_licence_fee_is_required(live_server, page: Page, base_context):
    base_context.return_value.update(
        {
            "is_fee_required": True,
            "fee_amount": None,
        }
    )

    page.goto(
        f"{live_server.url}/{SERVICE_SLUG}/{TEMP_EVENT_SLUG}/{TEST_AUTH_SLUG}/{TEST_INTERACTION}-{TEST_INTERACTION_SUB_ID}"
    )

    expect(page.get_by_test_id("fee-amount")).not_to_be_visible()
    expect(page.get_by_test_id("fee")).to_be_visible()
    expect(page.get_by_test_id("fee")).to_contain_text("There's a fee you'll need to pay for this submission.")


def test_page_has_download_pdf_inset(page: Page):
    page.goto(TEST_TEMP_EVENT_APPLY_URL)

    adobe_download_link = page.get_by_test_id("adobe-download")
    pdf_download_link = page.get_by_test_id("pdf-download")

    expect(page.get_by_test_id("pdf-inset")).to_contain_class("govuk-inset-text")
    expect(adobe_download_link).to_have_role("link")
    expect(adobe_download_link).to_have_attribute("href", "https://get.adobe.com/uk/reader/")
    expect(pdf_download_link).to_have_role("link")
    expect(pdf_download_link).to_have_attribute("href", "#")


def test_page_has_additional_information_inset_when_both_legislation_and_general_info_urls_available(page: Page):
    page.goto(TEST_TEMP_EVENT_APPLY_URL)

    general_info_link = page.get_by_test_id("general-information")
    legislation_info_link = page.get_by_test_id("legislation-information")

    expect(page.get_by_test_id("additional-information")).to_contain_text(
        "There is additional information available for this licence that you might find useful"
    )
    expect(general_info_link).to_have_role("link")
    expect(general_info_link).to_have_attribute("href", "#")
    expect(legislation_info_link).to_have_role("link")
    expect(legislation_info_link).to_have_attribute("href", "#")


def test_page_has_additional_information_inset_when_general_info_url_available(live_server, page: Page, base_context):
    base_context.return_value.update({"general_info_url": "testurl"})

    page.goto(
        f"{live_server.url}/{SERVICE_SLUG}/{TEMP_EVENT_SLUG}/{TEST_AUTH_SLUG}/{TEST_INTERACTION}-{TEST_INTERACTION_SUB_ID}"
    )

    expect(page.get_by_test_id("additional-information")).to_be_visible()
    expect(page.get_by_test_id("general-information")).to_be_visible()
    expect(page.get_by_test_id("legislation-information")).not_to_be_visible()


def test_page_has_additional_information_inset_when_legislation_info_url_available(
    live_server, page: Page, base_context
):
    base_context.return_value.update({"legislation_info_url": "testurl"})

    page.goto(
        f"{live_server.url}/{SERVICE_SLUG}/{TEMP_EVENT_SLUG}/{TEST_AUTH_SLUG}/{TEST_INTERACTION}-{TEST_INTERACTION_SUB_ID}"
    )

    expect(page.get_by_test_id("additional-information")).to_be_visible()
    expect(page.get_by_test_id("general-information")).not_to_be_visible()
    expect(page.get_by_test_id("legislation-information")).to_be_visible()


def test_page_does_not_have_additional_information_inset_when_no_general_info_nor_legislation_info_urls_available(
    live_server, page: Page, base_context
):
    page.goto(
        f"{live_server.url}/{SERVICE_SLUG}/{TEMP_EVENT_SLUG}/{TEST_AUTH_SLUG}/{TEST_INTERACTION}-{TEST_INTERACTION_SUB_ID}"
    )

    expect(page.get_by_test_id("additional-information")).not_to_be_visible()
    expect(page.get_by_test_id("general-information")).not_to_be_visible()
    expect(page.get_by_test_id("legislation-information")).not_to_be_visible()


def test_page_has_submit_button(page: Page):
    page.goto(TEST_TEMP_EVENT_APPLY_URL)

    submit_button = page.get_by_test_id("submit-button")
    expect(submit_button).to_be_visible()
    expect(submit_button).to_have_attribute("href", TEST_TEMP_EVENT_APPLY_FORM_URL)


def test_page_has_supporting_documents_list_when_licence_requires_supporting_documents(page: Page):
    page.goto(TEST_FOOD_PREMISES_APPLY_URL)

    details = page.get_by_test_id("electronic-copies-detail")
    details_text = page.get_by_test_id("electronic-copies-detail-text")

    expect(page.get_by_test_id("supporting-documents")).to_be_visible()
    expect(details).to_be_visible()
    expect(details_text).not_to_be_visible()

    details.click()
    expect(details_text).to_be_visible()


def test_page_marks_non_mandatory_supporting_documents_optional(page: Page):
    page.goto(TEST_FOOD_PREMISES_APPLY_URL)

    mandatory_document = page.get_by_test_id("support-document-1")
    optional_document = page.get_by_test_id("support-document-3")

    expect(mandatory_document).not_to_contain_text("(optional)")
    expect(optional_document).to_contain_text("(optional)")


def test_page_handles_conditional_rendering_of_supporting_documents_when_postal_not_allowed(
    live_server, page: Page, base_context
):
    base_context.return_value.update(
        {
            "supporting_documents": [{"name": "test", "is_mandatory": True}],
            "is_postal_allowed": False,
        }
    )

    page.goto(
        f"{live_server.url}/{SERVICE_SLUG}/{TEMP_EVENT_SLUG}/{TEST_AUTH_SLUG}/{TEST_INTERACTION}-{TEST_INTERACTION_SUB_ID}"
    )

    details = page.get_by_test_id("electronic-copies-detail")
    details.click()

    expect(page.get_by_test_id("electronic-copies-detail-text")).to_contain_text(
        "you cannot make an online application"
    )


def test_page_handles_conditional_rendering_of_supporting_documents_when_postal_allowed(
    live_server, page: Page, base_context
):
    base_context.return_value.update(
        {
            "supporting_documents": [{"name": "test", "is_mandatory": True}],
            "is_postal_allowed": True,
        }
    )

    page.goto(
        f"{live_server.url}/{SERVICE_SLUG}/{TEMP_EVENT_SLUG}/{TEST_AUTH_SLUG}/{TEST_INTERACTION}-{TEST_INTERACTION_SUB_ID}"
    )

    details = page.get_by_test_id("electronic-copies-detail")
    details.click()

    expect(page.get_by_test_id("electronic-copies-detail-text")).to_contain_text("you can still apply online")
