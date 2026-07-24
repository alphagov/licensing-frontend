from playwright.sync_api import Page, expect


def test_page_has_correct_headings(page: Page):
    page.goto("127.0.0.1:8000/apply-for-a-licence/temporary-event-notice/winchester/apply-1")

    expect(page.get_by_test_id("licence-heading")).to_contain_text("Temporary Event Notice")
    expect(page.get_by_test_id("licence-heading")).to_contain_text("Winchester")
    expect(page.get_by_test_id("action-heading")).to_have_text("Complete the application form")
    expect(page.get_by_test_id("download-heading")).to_have_text("First, download the form")
    expect(page.get_by_test_id("fill-in-heading")).to_have_text("Next, fill in the form on your computer")
    expect(page.get_by_test_id("before-apply-heading")).to_have_text("Before you apply...")
    expect(page.get_by_test_id("submit-heading")).to_have_text("Now, submit the application")


def test_page_has_4_steps_licence_has_fee(page: Page):
    page.goto("127.0.0.1:8000/apply-for-a-licence/temporary-event-notice/winchester/apply-1")

    expect(page.get_by_test_id("steps")).to_contain_text("1 of 4")


def test_page_has_3_steps_licence_has_no_fee(page: Page):
    page.goto("127.0.0.1:8000/apply-for-a-licence/food-premises-approval-6/winchester/apply-1")

    expect(page.get_by_test_id("steps")).to_contain_text("1 of 3")


def test_page_has_fee_amount_licence_has_fee(page: Page):
    page.goto("127.0.0.1:8000/apply-for-a-licence/temporary-event-notice/winchester/apply-1")

    expect(page.get_by_test_id("fee-amount")).to_contain_text("£21.00")


def test_page_has_no_fee_amount_licence_has_no_fee(page: Page):
    page.goto("127.0.0.1:8000/apply-for-a-licence/food-premises-approval-6/winchester/apply-1")

    expect(page.get_by_test_id("fee-amount")).not_to_be_visible()


def test_page_has_download_pdf_inset(page: Page):
    page.goto("127.0.0.1:8000/apply-for-a-licence/temporary-event-notice/winchester/apply-1")

    adobe_download_link = page.get_by_test_id("adobe-download")
    pdf_download_link = page.get_by_test_id("pdf-download")

    expect(page.get_by_test_id("pdf-inset")).to_contain_class("govuk-inset-text")
    expect(adobe_download_link).to_have_role("link")
    expect(adobe_download_link).to_have_attribute("href", "https://get.adobe.com/uk/reader/")
    expect(pdf_download_link).to_have_role("link")
    expect(pdf_download_link).to_have_attribute("href", "#")


def test_page_has_additional_information_inset(page: Page):
    page.goto("127.0.0.1:8000/apply-for-a-licence/temporary-event-notice/winchester/apply-1")

    general_info_link = page.get_by_test_id("general-information")
    legislation_info_link = page.get_by_test_id("legislation-information")

    expect(page.get_by_test_id("additional-information")).to_contain_text(
        "There is additional information available for this licence that you might find useful"
    )
    expect(general_info_link).to_have_role("link")
    expect(general_info_link).to_have_attribute("href", "#")
    expect(legislation_info_link).to_have_role("link")
    expect(legislation_info_link).to_have_attribute("href", "#")


def test_page_has_submit_button(page: Page):
    page.goto("127.0.0.1:8000/apply-for-a-licence/temporary-event-notice/winchester/apply-1")

    submit_button = page.get_by_test_id("submit-button")
    expect(submit_button).to_be_visible()
    expect(submit_button).to_have_attribute("href", "#")
