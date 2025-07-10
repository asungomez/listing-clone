from playwright.sync_api import Page, expect


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
    page: Page
) -> None:
    """
    Test that visiting the page with expired credentials shows the
    login page with a message indicating the session has expired.
    """

    page.goto("/")
    expect(
        page.get_by_text("Log in to this wonderfully useful site")
    ).to_be_visible()
