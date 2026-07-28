from conftest import BASE_URL, TEST_TEMP_EVENT_APPLY_FORM_URL
from playwright.sync_api import Page, expect


def test_page_has_correct_headings(page: Page):
    page.goto(f"{BASE_URL}{TEST_TEMP_EVENT_APPLY_FORM_URL}")

    expect(page.get_by_test_id("page-heading")).to_contain_text("Temporary Event Notice")
    expect(page.get_by_test_id("page-heading")).to_contain_text("Winchester")
    expect(page.get_by_test_id("action-heading")).to_have_text("Submit the application")


def test_page_has_emails_fields(page: Page):
    page.goto(f"{BASE_URL}{TEST_TEMP_EVENT_APPLY_FORM_URL}")

    expect(page.get_by_test_id("email-field")).to_be_visible()
