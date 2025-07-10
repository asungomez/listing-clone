from utils import Helper
from playwright.sync_api import Page, expect


def test_visit_page_without_authentication(
    tests_helper: Helper,
    page: Page
) -> None:
    """
    Test that visiting the page without stored credentials shows the
    login page.
    """
    page.goto("/")
    expect(
        page.get_by_text("Log in to this wonderfully useful site")
    ).to_be_visible()
