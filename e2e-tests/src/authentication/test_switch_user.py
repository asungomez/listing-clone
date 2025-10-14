from playwright.sync_api import Page, expect
from src.factories.user import UserFactory
from src.utils import Helper


def test_switch_user_as_non_admin(
    page: Page,
    tests_helper: Helper,
    user_factory: UserFactory
) -> None:
    """
    Test that the switch user form doesn't appear for non-admin users
    """
    user = user_factory.generate(is_superuser=False)
    tests_helper.insert_user(user)
    with tests_helper.authenticated_context(
        page=page,
        email=user.email
    ):
        page.goto("/")
        page.get_by_label("User menu").click()
        expect(page.get_by_text("Switch user")).not_to_be_visible()
