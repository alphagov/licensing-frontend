from conftest import BASE_URL, TEST_FOOD_PREMISES_APPLY_FORM_URL, TEST_TEMP_EVENT_APPLY_FORM_URL
from playwright.sync_api import Page, expect


def test_page_has_correct_headings(page: Page):
    page.goto(f"{BASE_URL}{TEST_TEMP_EVENT_APPLY_FORM_URL}")

    expect(page.get_by_test_id("page-heading")).to_contain_text("Temporary Event Notice")
    expect(page.get_by_test_id("page-heading")).to_contain_text("Winchester")
    expect(page.get_by_test_id("action-heading")).to_have_text("Submit the application")


def test_page_has_emails_field(page: Page):
    page.goto(f"{BASE_URL}{TEST_TEMP_EVENT_APPLY_FORM_URL}")

    expect(page.get_by_test_id("email-field")).to_be_visible()


def test_page_has_confirmation_email_field(page: Page):
    page.goto(f"{BASE_URL}{TEST_TEMP_EVENT_APPLY_FORM_URL}")

    expect(page.get_by_test_id("confirmation-email-field")).to_be_visible()


def test_page_has_application_form_upload_field(page: Page):
    page.goto(f"{BASE_URL}{TEST_TEMP_EVENT_APPLY_FORM_URL}")

    expect(page.get_by_test_id("application-upload")).to_be_visible()


def test_page_has_additional_file_upload_fields_supporting_documents_required(page: Page):
    page.goto(f"{BASE_URL}{TEST_FOOD_PREMISES_APPLY_FORM_URL}")

    (
        expect(page.get_by_test_id("supporting-documents-statement")).to_contain_text(
            "All documents are required, unless stated otherwise. "
            "Photos of documents are acceptable, as long as all the relevant information is clear. "
            "We'll only share these documents with the licensing authority."
        )
    )
