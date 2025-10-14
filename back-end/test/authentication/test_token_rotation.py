from test.factories.user import user_factory
from test.utils import Helper


def test_access_token_valid_in_cookie(tests_helper: Helper) -> None:
    """
    Test that the response is 200 if the access token is valid,
    not expired and in the cookie.
    """
    path = "/users/me"
    email = "existing.email@email.net"
    user = user_factory({
        "email": email,
    })
    tests_helper.insert_user(user)
    response = tests_helper.get_request(
        path,
        authenticated_as=email,
        authentication_method="cookie",
    )
    assert response.status_code == 200


def test_access_token_valid_in_header(tests_helper: Helper) -> None:
    """
    Test that the response is 200 if the access token is valid,
    not expired and in the header.
    """
    path = "/users/me"
    email = "existing.email@email.net"
    user = user_factory({
        "email": email,
    })
    tests_helper.insert_user(user)
    response = tests_helper.get_request(
        path,
        authenticated_as=email,
        authentication_method="header",
    )
    assert response.status_code == 200


def test_access_token_invalid_in_cookie(tests_helper: Helper) -> None:
    """
    Test that the response is 403 if the access token is invalid,
    not expired and in the cookie.
    """
    path = "/users/me"
    email = "existing.email@email.net"
    user = user_factory({
        "email": email,
    })
    tests_helper.insert_user(user)
    tests_helper.mock_okta_userinfo_response(
        response_body={
            "error": "invalid_token"
        },
        response_status=400,
    )
    response = tests_helper.get_request(
        path,
        authenticated_as=email,
        authentication_method="cookie",
        omit_auth_mocking=True,
    )
    assert response.status_code == 403
    response_body = response.json()
    assert response_body["message"] == "The credentials are invalid"
    assert response_body["code"] == "session_invalid"


def test_access_token_invalid_in_header(tests_helper: Helper) -> None:
    """
    Test that the response is 403 if the access token is invalid,
    not expired and in the header.
    """
    path = "/users/me"
    email = "existing.email@email.net"
    user = user_factory({
        "email": email,
    })
    tests_helper.insert_user(user)
    tests_helper.mock_okta_userinfo_response(
        response_body={
            "error": "invalid_token"
        },
        response_status=400,
    )
    response = tests_helper.get_request(
        path,
        authenticated_as=email,
        authentication_method="header",
        omit_auth_mocking=True,
    )
    assert response.status_code == 403
    response_body = response.json()
    assert response_body["message"] == "The credentials are invalid"
    assert response_body["code"] == "session_invalid"


def test_access_token_and_refresh_token_expired_in_cookie(
  tests_helper: Helper
  ) -> None:
    """
    Test that the response is 403 if the cookie contains:
    - an access token that is valid but expired
    - a refresh token that is valid but expired
    """
    path = "/users/me"
    email = "existing.email@email.net"
    user = user_factory({
        "email": email,
    })
    tests_helper.insert_user(user)
    tests_helper.mock_okta_userinfo_response(
        response_body={
            "error": "expired_token"
        },
        response_status=401,
    )
    tests_helper.mock_okta_token_response(
        response_body={
            "error": "expired_token"
        },
        response_status=401,
        grant_type="refresh_token",
    )
    response = tests_helper.get_request(
        path,
        authenticated_as=email,
        authentication_method="cookie",
        omit_auth_mocking=True
    )
    assert response.status_code == 403
    response_body = response.json()
    assert response_body["message"] == "The credentials are expired"
    assert response_body["code"] == "session_expired"


def test_valid_refresh_token_in_cookie(tests_helper: Helper) -> None:
    """
    Test that the response is 200 if the cookie contains:
    - an access token that is valid but expired
    - a refresh token that is valid and not expired
    """
    path = "/users/me"
    email = "existing.email@email.net"
    user = user_factory({
        "email": email,
    })
    tests_helper.insert_user(user)
    # first, the access token is invalid so the userinfo
    # endpoint returns a 401 (note the times=1, so this happens only once)
    tests_helper.mock_okta_userinfo_response(
        response_body={
            "error": "expired_token"
        },
        response_status=401,
        times=1,
    )

    # then, the refresh token is used to get a new access token
    tests_helper.mock_okta_token_response(
        response_body={
            "access_token": "valid-access-token"
        },
        response_status=200,
        grant_type="refresh_token",
    )
    # finally, the userinfo endpoint returns the user's email
    tests_helper.mock_okta_userinfo_response(
        response_body={
            "email": email
        }
    )
    response = tests_helper.get_request(
        path,
        authenticated_as=email,
        authentication_method="cookie",
        omit_auth_mocking=True,
    )
    assert response.status_code == 200


def test_invalid_refresh_token_in_cookie(tests_helper: Helper) -> None:
    """
    Test that the response is 403 if the cookie contains:
    - an access token that is valid but expired
    - a refresh token that is invalid
    """
    path = "/users/me"
    email = "existing.email@email.net"
    user = user_factory({
        "email": email,
    })
    tests_helper.insert_user(user)
    tests_helper.mock_okta_userinfo_response(
        response_body={
            "error": "expired_token"
        },
        response_status=401,
    )
    tests_helper.mock_okta_token_response(
        response_body={
            "error": "invalid_grant"
        },
        response_status=400,
        grant_type="refresh_token",
    )
    response = tests_helper.get_request(
        path,
        authenticated_as=email,
        authentication_method="cookie",
        omit_auth_mocking=True,
    )
    assert response.status_code == 403
    response_body = response.json()
    assert response_body["message"] == "The credentials are invalid"
    assert response_body["code"] == "session_invalid"
