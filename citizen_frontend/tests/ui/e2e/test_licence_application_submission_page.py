import os
from urllib.parse import parse_qs, urlparse

import boto3
import pytest
from common.models.licence_application import LicenceApplication
from conftest import BASE_URL, TEST_FOOD_PREMISES_APPLY_FORM_URL, TEST_TEMP_EVENT_APPLY_FORM_URL
from playwright.sync_api import Page, expect

"""
This requires a seeded_db to run
"""


@pytest.fixture
def ministack_s3():
    s3 = boto3.client(
        "s3",
        endpoint_url="http://localhost:4566",
        region_name="us-east-1",
        aws_access_key_id="testing",
        aws_secret_access_key="testing",
    )
    s3.create_bucket(Bucket="test-bucket")

    yield

    content = s3.list_objects(Bucket="test-bucket")["Contents"]

    for object in content:
        s3.delete_object(Bucket="test-bucket", Key=object["Key"])

    s3.delete_bucket(Bucket="test-bucket")


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

    declarations = page.get_by_test_id("declarations")
    expect(declarations).to_be_visible()
    children = declarations.locator("li")
    assert children.count() == 4

    expect(page.get_by_test_id("declaration-checkbox")).to_be_visible()

    expect(page.get_by_test_id("submit-button")).to_be_visible()


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

    declarations = page.get_by_test_id("declarations")
    expect(declarations).to_be_visible()
    children = declarations.locator("li")
    assert children.count() == 1
    expect(page.get_by_test_id("declaration-checkbox")).to_be_visible()

    expect(page.get_by_test_id("submit-button")).to_be_visible()


def test_optional_supporting_documents_are_marked_optional(page: Page):
    page.goto(f"{BASE_URL}{TEST_FOOD_PREMISES_APPLY_FORM_URL}")

    optional_upload = page.get_by_label("Additonal information for section 9 of the form(optional)")
    expect(optional_upload).to_be_visible()
    expect(optional_upload).to_have_role("button")


def test_user_notified_required_inputs_missing_on_submission(page: Page):
    page.goto(f"{BASE_URL}{TEST_TEMP_EVENT_APPLY_FORM_URL}")

    page.get_by_test_id("submit-button").click()
    error_summary = page.locator(".govuk-error-summary")

    expect(error_summary).to_be_visible()


def test_email_fields_show_error_email_do_not_match(page: Page):
    page.goto(f"{BASE_URL}{TEST_TEMP_EVENT_APPLY_FORM_URL}")

    email_field = page.get_by_test_id("email-field")
    confirmation_email_field = page.get_by_test_id("confirmation-email-field")

    email_field.fill("example@email.com")
    confirmation_email_field.fill("not_matching@email.com")

    page.get_by_test_id("submit-button").click()

    expect(email_field).to_have_attribute("class", "govuk-input govuk-input--error")


def test_form_submission(page: Page, ministack_s3):
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
    page.goto(f"{BASE_URL}/apply-for-a-licence/temporary-event-notice/york/apply-1/form")

    page.get_by_test_id("email-field").fill("example@email.com")
    page.get_by_test_id("confirmation-email-field").fill("example@email.com")

    application_upload = page.get_by_test_id("application-upload")
    application_upload.set_input_files("citizen_frontend/tests/resources/Fish_Dealers_Licence.pdf")

    declaration_checkbox = page.get_by_test_id("declaration-checkbox")
    declaration_checkbox.click()

    page.get_by_test_id("submit-button").click()

    page.wait_for_url("**/uploaded?**")

    # Pull newly created object id out of the url
    redirect_url = page.url
    parsed_url = urlparse(redirect_url)
    query_params = parse_qs(parsed_url.query)
    application_id = query_params.get("id", [None])[0]

    # Check the newly created object against what has been filled in form
    application = LicenceApplication.objects.get(_id=application_id)
    assert application.applicant_email == "example@email.com"
    application.delete()


def test_redirect_after_submission_customisation_has_fee():
    # TODO Page does not exist yet, user should be directed to pre-payment page
    #   entry for application and payment should be created in relevant collections
    pass
