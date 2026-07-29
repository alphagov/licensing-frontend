import pytest
from conftest import BASE_URL, TEST_FOOD_PREMISES_APPLY_FORM_URL, TEST_TEMP_EVENT_APPLY_FORM_URL
from playwright.sync_api import Page, expect


def test_page_has_correct_headings(page: Page):
    page.goto(f"{BASE_URL}{TEST_TEMP_EVENT_APPLY_FORM_URL}")

    expect(page.get_by_test_id("page-heading")).to_contain_text("Temporary Event Notice")
    expect(page.get_by_test_id("page-heading")).to_contain_text("Winchester")
    expect(page.get_by_test_id("action-heading")).to_have_text("Submit the application")


@pytest.mark.parametrize(
    "url, expected_total_steps",
    [
        (TEST_TEMP_EVENT_APPLY_FORM_URL, "4"),
        (TEST_FOOD_PREMISES_APPLY_FORM_URL, "3"),
    ],
)
def test_page_has_correct_number_of_steps(page: Page, url, expected_total_steps):
    page.goto(f"{BASE_URL}{url}")

    expect(page.get_by_test_id("steps")).to_contain_text(f"2 of {expected_total_steps}")


def test_page_form_has_correct_elements_no_supporting_documents_required(page: Page):
    page.goto(f"{BASE_URL}{TEST_TEMP_EVENT_APPLY_FORM_URL}")

    application_upload = page.get_by_test_id("application-upload")

    expect(page.get_by_test_id("email-field")).to_be_visible()
    expect(page.get_by_test_id("confirmation-email-field")).to_be_visible()

    expect(application_upload).to_be_visible()
    expect(application_upload).to_have_role("button")

    expect(page.get_by_test_id("supporting-documents-statement")).not_to_be_visible()

    expect(page.get_by_test_id("declarations")).to_be_visible()

    declarations = page.get_by_role("listitem").all()
    assert len(declarations) == 4

    expect(page.get_by_test_id("declaration-checkbox")).to_be_visible()


def test_page_has_correct_elements_supporting_documents_required(page: Page):
    page.goto(f"{BASE_URL}{TEST_FOOD_PREMISES_APPLY_FORM_URL}")

    application_upload = page.get_by_test_id("application-upload")
    supporting_document_upload = page.get_by_test_id("supporting-document-upload-0")

    expect(page.get_by_test_id("email-field")).to_be_visible()
    expect(page.get_by_test_id("confirmation-email-field")).to_be_visible()

    expect(application_upload).to_be_visible()
    expect(application_upload).to_have_role("button")

    expect(page.get_by_test_id("supporting-documents-statement")).to_be_visible()
    expect(page.get_by_test_id("supporting-documents-inset")).to_be_visible()
    expect(page.get_by_test_id("supporting-documents-details")).to_be_visible()
    expect(supporting_document_upload).to_be_visible()
    expect(supporting_document_upload).to_have_role("button")

    expect(page.get_by_test_id("declarations")).to_be_visible()

    declarations = page.get_by_role("listitem").all()
    assert len(declarations) == 1

    expect(page.get_by_test_id("declaration-checkbox")).to_be_visible()
