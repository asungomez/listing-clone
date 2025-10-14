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


def test_switch_user_when_authenticated_as_admin(
    page: Page,
    tests_helper: Helper,
    user_factory: UserFactory
) -> None:
    """
    Test that admins can switch users
    """
    admin_user = user_factory.generate(
        is_superuser=True,
        email="admin.email@email.net"
    )
    tests_helper.insert_user(admin_user)
    impersonated_user = user_factory.generate(
        email="impersonated.email@email.net"
    )
    tests_helper.insert_user(impersonated_user)
    with tests_helper.authenticated_context(
        page=page,
        email=admin_user.email
    ):
        page.goto("/")
        page.get_by_label("User menu").click()
        expect(page.get_by_text("Switch user")).to_be_visible()
        page.get_by_placeholder("Type an email...").fill(
            impersonated_user.email
        )
        page.get_by_text(impersonated_user.email).click()
        expect(page.get_by_text(impersonated_user.email)).to_be_visible()
        expect(page.get_by_text(admin_user.email)).not_to_be_visible()
