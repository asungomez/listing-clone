from playwright.sync_api import Page, expect
from src.factories.user import UserFactory
from src.utils import Helper


def test_user_email(
    page: Page,
    tests_helper: Helper,
    user_factory: UserFactory
) -> None:
    """
    Test that the user email is displayed in the navbar after logging in.
    """
    user = user_factory.generate()
    tests_helper.insert_user(user)
    with tests_helper.authenticated_context(
        page=page,
        email=user.email
    ):
        page.goto("/")
        page.get_by_label("User menu").click()
        expect(page.get_by_text(user.email)).to_be_visible()


def test_successful_log_out(
    page: Page,
    tests_helper: Helper,
    user_factory: UserFactory
) -> None:
    """
    Test that the user can log out successfully.
    """
    user = user_factory.generate()
    tests_helper.insert_user(user)
    tests_helper.mock_okta_revoke_response(
        response_body={
            "message": "Token revoked"
        },
        response_status=200,
    )
    with tests_helper.authenticated_context(
        page=page,
        email=user.email
    ):
        page.goto("/")
        page.get_by_label("User menu").click()
        page.get_by_text("Log Out").click()
        expect(
            page.get_by_text("Log in to this wonderfully useful site")
            ).to_be_visible()


def test_failed_log_out(
    page: Page,
    tests_helper: Helper,
    user_factory: UserFactory
) -> None:
    """
    Test that there's an error message if the log out fails.
    """
    user = user_factory.generate()
    tests_helper.insert_user(user)
    tests_helper.mock_okta_revoke_response(
        response_body={
            "message": "Error"
        },
        response_status=500,
    )
    with tests_helper.authenticated_context(
        page=page,
        email=user.email
    ):
        page.goto("/")
        page.get_by_label("User menu").click()
        page.get_by_text("Log Out").click()
        expect(
            page.get_by_text("Failed to log out. Please try again.")
            ).to_be_visible()
