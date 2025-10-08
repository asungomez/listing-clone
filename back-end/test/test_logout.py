from .factories.user import user_factory
from .utils import Helper


def test_logout_unauthenticated(tests_helper: Helper) -> None:
    """
    Test that the logout endpoint returns 200 if the user is not authenticated.
    """
    path = "/users/logout"
    response = tests_helper.post_request(path)
    assert response.status_code == 200


def test_logout_inexistent_user(tests_helper: Helper) -> None:
    """
    Test that the logout endpoint returns 200 if the user does not exist.
    """
    tests_helper.mock_okta_revoke_response(
        response_body={
            "message": "Token revoked"
        },
        response_status=200,
    )
    response = tests_helper.post_request(
      path="/users/logout",
      authenticated_as="inexistent.email@email.net"
      )
    assert response.status_code == 200


def test_logout_expired_token(tests_helper: Helper) -> None:
    """
    Test that the logout endpoint returns 200 if the token is expired.
    """
    tests_helper.mock_okta_revoke_response(
        response_body={
            "message": "Token revoked"
        },
        response_status=200,
    )
    email = "existing.email@email.net"
    user = user_factory({
        "email": email,
    })
    tests_helper.insert_user(user)
    response = tests_helper.post_request(
      path="/users/logout",
      authenticated_as=email,
    )
    assert response.status_code == 200


def test_logout_valid_token(tests_helper: Helper) -> None:
    """
    Test that the logout endpoint returns 200 if the token is valid.
    """
    tests_helper.mock_okta_revoke_response(
        response_body={
            "message": "Token revoked"
        },
        response_status=200,
    )
    email = "existing.email@email.net"
    user = user_factory({
        "email": email,
    })
    tests_helper.insert_user(user)
    response = tests_helper.post_request(
      path="/users/logout",
      authenticated_as=email,
    )
    assert response.status_code == 200


def test_logout_failing_okta_revoke(tests_helper: Helper) -> None:
    """
    Test that the logout endpoint returns 500 if the Okta revoke endpoint
    fails.
    """
    tests_helper.mock_okta_revoke_response(
        response_body={
            "message": "Token revoked"
        },
        response_status=500,
    )
    email = "existing.email@email.net"
    user = user_factory({
        "email": email,
    })
    tests_helper.insert_user(user)
    response = tests_helper.post_request(
      path="/users/logout",
      authenticated_as=email,
    )
    assert response.status_code == 500
