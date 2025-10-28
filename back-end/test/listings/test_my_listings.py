from test.factories.listing import listing_factory
from test.factories.user import user_factory
from test.utils import Helper


def test_my_listings_not_authenticated(tests_helper: Helper) -> None:
    """
    Test that the my listings endpoint returns 401 if the user is not
    authenticated
    """
    response = tests_helper.get_request("/listings/my-listings")
    assert response.status_code == 403


def test_when_the_user_has_no_listings(tests_helper: Helper) -> None:
    """
    Test that the my listings endpoint returns 200 if the user has no listings
    """
    email = "existing.email@email.net"
    user = user_factory({
        "email": email,
    })
    tests_helper.insert_user(user)
    response = tests_helper.get_request(
      "/listings/my-listings",
      authenticated_as=email
    )
    assert response.status_code == 200
    response_body = response.json()
    assert response_body["listings"] == []
    assert response_body["total_count"] == 0


def test_my_listings(tests_helper: Helper) -> None:
    """
    Test that the my listings endpoint returns the listings
    where the user is a coordinator
    """
    email = "existing.email@email.net"
    user = user_factory({
        "email": email,
    })
    tests_helper.insert_user(user)
    listing = listing_factory({
      "updated_by": user["id"],
      "coordinators": [
        {
          "coordinator_id": user["id"],
          "coordinator_email": user["email"],
        }
      ]
    })
    tests_helper.insert_listing(listing)
    response = tests_helper.get_request(
      "/listings/my-listings",
      authenticated_as=email
    )
    assert response.status_code == 200
    response_body = response.json()
    assert response_body["total_count"] == 1
    found_listing = response_body["listings"][0]
    assert found_listing["id"] == listing["id"]
    assert found_listing["title"] == listing["title"]
    assert found_listing["description"] == listing["description"]
    coordinators = found_listing["coordinators"]
    assert len(coordinators) == 1
    assert coordinators[0]["id"] == user["id"]
    assert coordinators[0]["email"] == user["email"]
