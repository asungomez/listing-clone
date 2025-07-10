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

    with tests_helper.authenticated_context(
        page=page,
        email="made-up-email@email.net",
        is_expired=True
    ):
        page.goto("/")
        expect(
            page.get_by_text("Your session has expired. Please log in again.")
        ).to_be_visible()


def test_visit_page_with_invalid_credentials(
    page: Page,
    tests_helper: Helper
) -> None:
    """
    Test that visiting the page with invalid credentials shows the
    login page with a message indicating the session is invalid.
    """

    with tests_helper.authenticated_context(
        page=page,
        email="made-up-email@email.net",
        is_invalid=True
    ):
        page.goto("/")
        expect(
            page.get_by_text(
                "Your credentials are invalid. Please log in again."
            )
        ).to_be_visible()
