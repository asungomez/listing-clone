from test.factories.listing import listing_factory
from test.factories.user import user_factory
from test.utils import Helper


def test_create_listing_not_authenticated(tests_helper: Helper) -> None:
    """
    Test that the create listing endpoint returns 401 if the user is not
    authenticated
    """
    response = tests_helper.post_request("/listings/", {})
    assert response.status_code == 403


def test_create_listing(tests_helper: Helper) -> None:
    """
    Test that an authenticated user can create a listing,
    and it automatically adds the user as a coordinator
    """
    email = "existing.email@email.net"
    user = user_factory({
        "email": email,
    })
    tests_helper.insert_user(user)
    listing = listing_factory()
    response = tests_helper.post_request(
      "/listings/",
      listing,
      authenticated_as=email
    )
    response_body = response.json()
    assert response.status_code == 201
    assert response_body["title"] == listing["title"]
    assert response_body["description"] == listing["description"]
    assert response_body["coordinators"] == [
        {
            "id": user["id"],
            "email": user["email"]
        }
    ]
    listing_id = int(response_body["id"])
    found_listing = tests_helper.find_listing_by_id(listing_id)
    assert found_listing is not None
    print("found listing", found_listing)
    assert found_listing["title"] == listing["title"]
    assert found_listing["description"] == listing["description"]
    assert found_listing["coordinators"] == [
        {
            "id": user["id"],
            "email": user["email"]
        }
    ]
