from playwright.sync_api import Page, expect
from src.factories.listing import ListingFactory
from src.factories.user import UserFactory
from src.utils import Helper


def test_my_listings_unauthenticated(
    page: Page,
) -> None:
    """
    Test that visiting the /my-listings page without authentication redirects
    to the login page.
    """
    page.goto("/my-listings")
    expect(
        page.get_by_text("Log in to this wonderfully useful site")
    ).to_be_visible()


def test_no_listings(
    page: Page,
    tests_helper: Helper,
    user_factory: UserFactory
) -> None:
    """
    Test that the /my-listings page shows a message when the user has no
    listings.
    """
    user = user_factory.generate()
    tests_helper.insert_user(user)
    with tests_helper.authenticated_context(
        page=page,
        email=user.email
    ):
        page.goto("/my-listings")
        expect(page.get_by_text("No listings yet")).to_be_visible()


def test_my_listings(
    page: Page,
    tests_helper: Helper,
    user_factory: UserFactory,
    listing_factory: ListingFactory
) -> None:
    """
    Test that the /my-listings page shows the user's listings.
    """
    user = user_factory.generate()
    tests_helper.insert_user(user)
    listing = listing_factory.generate(
        coordinators=[user],
        updated_by=user.id,
    )
    tests_helper.insert_listing(listing)
    with tests_helper.authenticated_context(
        page=page,
        email=user.email
    ):
        page.goto("/my-listings")
        expect(page.get_by_text(listing.title)).to_be_visible()
