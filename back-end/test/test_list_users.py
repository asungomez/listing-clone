from .factories.user import user_factory
from .utils import Helper


def test_list_users_not_authenticated(tests_helper: Helper) -> None:
    """
    Test that the list users endpoint returns 403 if the user is
    not authenticated
    """
    response = tests_helper.get_request("/users/")
    assert response.status_code == 403


def test_list_users_as_non_admin(tests_helper: Helper) -> None:
    """
    Test that the list users endpoint returns 403 if the user is not an admin
    """
    email = "existing.email@email.net"
    user = user_factory({
        "email": email,
    })
    tests_helper.insert_user(user)
    response = tests_helper.get_request(
        "/users/",
        authenticated_as=email,
    )
    assert response.status_code == 403


def test_returns_all_users_when_no_email_is_provided(
  tests_helper: Helper
  ) -> None:
    """
    Test that the list users endpoint returns 200 and all users when
    no email is provided
    """
    email = "admin.email@email.net"
    user = user_factory({
        "email": email,
        "is_superuser": True,
    })
    tests_helper.insert_user(user)
    more_users = [
        user_factory({
            "email": f"user{i}.email@email.net",
            "is_superuser": False,
        })
        for i in range(1, 5)
    ]
    for user in more_users:
        tests_helper.insert_user(user)
    response = tests_helper.get_request(
        "/users/",
        authenticated_as=email,
    )
    assert response.status_code == 200
    response_body = response.json()
    users_response = response_body.get("users")
    assert users_response is not None
    assert len(users_response) == 5
    all_users = more_users + [user]
    users_response_emails = [u["email"] for u in users_response]
    for user in all_users:
        assert user["email"] in users_response_emails


def test_filters_users_by_email(tests_helper: Helper) -> None:
    """
    Test that the list users endpoint returns 200 and the users that match
    the email filter
    """
    email = "admin.email@email.net"
    user = user_factory({
        "email": email,
        "is_superuser": True,
    })
    tests_helper.insert_user(user)
    returned_users = [
        user_factory({
            "email": f"returned_user_{i}.email@email.net",
            "is_superuser": False,
        })
        for i in range(1, 5)
    ]
    for user in returned_users:
        tests_helper.insert_user(user)
    non_returned_users = [
        user_factory({
            "email": f"omitted_user_{i}.email@email.net",
            "is_superuser": False,
        })
        for i in range(1, 5)
    ]
    for user in non_returned_users:
        tests_helper.insert_user(user)

    response = tests_helper.get_request(
        "/users/",
        authenticated_as=email,
        query_params={"email": "returned_user"},
    )
    assert response.status_code == 200
    response_body = response.json()
    users_response = response_body.get("users")
    assert users_response is not None
    users_response_emails = [u["email"] for u in users_response]
    assert len(users_response) == 4
    for user in returned_users:
        assert user["email"] in users_response_emails
    for user in non_returned_users:
        assert user["email"] not in users_response_emails
