from playwright.sync_api import Page, expect
from src.utils import Helper


def test_visit_page_without_authentication(
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


def test_visit_page_with_expired_credentials(
    page: Page,
    tests_helper: Helper
) -> None:
    """
    Test that visiting the page with expired credentials shows the
    login page with a message indicating the session has expired.
    """

    page = tests_helper.authenticate_as(
        page=page,
        email="made-up-email@email.net",
        is_expired=True  # Simulate expired credentials
        )
    page.goto("/")
    expect(
        page.get_by_text("Your session has expired. Please log in again.")
    ).to_be_visible()
