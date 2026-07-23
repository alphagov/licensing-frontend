from playwright.sync_api import Page, expect


def test_page_has_correct_header(page: Page):
    page.goto("127.0.0.1:8000/apply-for-a-licence/temporary-event-notice/winchester/apply-1")

    expect(page.get_by_test_id("licence_heading")).to_contain_text("temporary event notice")
    expect(page.get_by_test_id("licence_heading")).to_contain_text("winchester")
