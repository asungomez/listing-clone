from test.factories.user import user_factory
from test.utils import Helper


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


def test_default_page_size(tests_helper: Helper) -> None:
    """
    Test that when page_size is not provided, the default page size is used
    """
    email = "admin.email@email.net"
    user = user_factory({
        "email": email,
        "is_superuser": True,
    })
    tests_helper.insert_user(user)
    users_count = 100
    for i in range(1, users_count):
        user = user_factory({
            "email": f"user{i}.email@email.net",
        })
        tests_helper.insert_user(user)
    response = tests_helper.get_request(
        "/users/",
        authenticated_as=email,
    )
    assert response.status_code == 200
    response_body = response.json()
    users_response = response_body.get("users")
    assert users_response is not None
    assert len(users_response) == 25
    total_count = response_body.get("total_count")
    assert total_count is not None
    assert total_count == users_count


def test_page_size_defined(tests_helper: Helper) -> None:
    """
    Test that when page_size is provided, the number of users returned is the
    page size and the total count is the number of users
    """
    email = "admin.email@email.net"
    user = user_factory({
        "email": email,
        "is_superuser": True,
    })
    tests_helper.insert_user(user)
    users_count = 100
    for i in range(1, users_count):
        user = user_factory({
            "email": f"user{i}.email@email.net",
        })
        tests_helper.insert_user(user)
    response = tests_helper.get_request(
        "/users/",
        authenticated_as=email,
        query_params={"page_size": 10},
    )
    assert response.status_code == 200
    response_body = response.json()
    users_response = response_body.get("users")
    assert users_response is not None
    assert len(users_response) == 10
    total_count = response_body.get("total_count")
    assert total_count is not None
    assert total_count == users_count


def test_page_size_bigger_than_users_count(tests_helper: Helper) -> None:
    """
    Test that when page_size is bigger than the number of users, it
    returns all users
    """
    email = "admin.email@email.net"
    user = user_factory({
        "email": email,
        "is_superuser": True,
    })
    tests_helper.insert_user(user)
    users_count = 10
    for i in range(1, users_count):
        user = user_factory({
            "email": f"user{i}.email@email.net",
        })
        tests_helper.insert_user(user)
    response = tests_helper.get_request(
        "/users/",
        authenticated_as=email,
        query_params={"page_size": 30},
    )
    assert response.status_code == 200
    response_body = response.json()
    users_response = response_body.get("users")
    assert users_response is not None
    assert len(users_response) == users_count
    total_count = response_body.get("total_count")
    assert total_count is not None
    assert total_count == users_count


def test_negative_page_size(tests_helper: Helper) -> None:
    """
    Test that when page_size is negative, it returns 400
    """
    email = "admin.email@email.net"
    user = user_factory({
        "email": email,
        "is_superuser": True,
    })
    tests_helper.insert_user(user)
    response = tests_helper.get_request(
        "/users/",
        authenticated_as=email,
        query_params={"page_size": -1},
    )
    assert response.status_code == 400
    response_body = response.json()
    page_size_error = response_body.get("page_size")
    assert page_size_error is not None
    assert "page_size must be greater than 0" in page_size_error


def test_page_size_zero(tests_helper: Helper) -> None:
    """
    Test that when page_size is zero, it returns 400
    """
    email = "admin.email@email.net"
    user = user_factory({
        "email": email,
        "is_superuser": True,
    })
    tests_helper.insert_user(user)
    response = tests_helper.get_request(
        "/users/",
        authenticated_as=email,
        query_params={"page_size": 0},
    )
    assert response.status_code == 400
    response_body = response.json()
    page_size_error = response_body.get("page_size")
    assert page_size_error is not None
    assert "page_size must be greater than 0" in page_size_error


def test_max_page_size(tests_helper: Helper) -> None:
    """
    Test that the maximum page size is respected
    """
    email = "admin.email@email.net"
    user = user_factory({
        "email": email,
        "is_superuser": True,
    })
    tests_helper.insert_user(user)
    response = tests_helper.get_request(
        "/users/",
        authenticated_as=email,
        query_params={"page_size": 101},
    )
    assert response.status_code == 400
    response_body = response.json()
    page_size_error = response_body.get("page_size")
    assert page_size_error is not None
    assert "page_size must be less than or equal to 100" in page_size_error


def test_offset_defined(tests_helper: Helper) -> None:
    """
    Test that when offset is provided, the users list starts at the offset
    """
    email = "admin.email@email.net"
    user = user_factory({
        "email": email,
        "is_superuser": True,
    })
    tests_helper.insert_user(user)
    non_returned_users = [
        user_factory({
            "email": f"returned_user_{i}.email@email.net",
        })
        for i in range(1, 5)
    ]
    for user in non_returned_users:
        tests_helper.insert_user(user)
    non_returned_users = [user] + non_returned_users
    returned_users = [
        user_factory({
            "email": f"non_returned_user_{i}.email@email.net",
        })
        for i in range(1, 5)
    ]
    for user in returned_users:
        tests_helper.insert_user(user)
    response = tests_helper.get_request(
        "/users/",
        authenticated_as=email,
        query_params={"offset": 5},
    )
    assert response.status_code == 200
    response_body = response.json()
    users_response = response_body.get("users")
    assert users_response is not None
    users_response_emails = [u["email"] for u in users_response]
    for user in returned_users:
        assert user["email"] in users_response_emails
    for user in non_returned_users:
        assert user["email"] not in users_response_emails


def test_offset_not_defined(tests_helper: Helper) -> None:
    """
    Test that when offset is not provided, the users list starts at 0
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
        })
        for i in range(1, 5)
    ]
    for user in returned_users:
        tests_helper.insert_user(user)
    returned_users = [user] + returned_users
    response = tests_helper.get_request(
        "/users/",
        authenticated_as=email,
    )
    assert response.status_code == 200
    response_body = response.json()
    users_response = response_body.get("users")
    assert users_response is not None
    users_response_emails = [u["email"] for u in users_response]
    for user in returned_users:
        assert user["email"] in users_response_emails


def test_negative_offset(tests_helper: Helper) -> None:
    """
    Test that when offset is negative, it returns 400
    """
    email = "admin.email@email.net"
    user = user_factory({
        "email": email,
        "is_superuser": True,
    })
    tests_helper.insert_user(user)
    response = tests_helper.get_request(
        "/users/",
        authenticated_as=email,
        query_params={"offset": -1},
    )
    assert response.status_code == 400
    response_body = response.json()
    offset_error = response_body.get("offset")
    assert offset_error is not None
    assert "offset must be greater than or equal to 0" in offset_error


def test_offset_bigger_than_users_count(tests_helper: Helper) -> None:
    """
    Test that when offset is bigger than the number of users, it returns
    an empty list
    """
    email = "admin.email@email.net"
    user = user_factory({
        "email": email,
        "is_superuser": True,
    })
    tests_helper.insert_user(user)
    users_count = 10
    for i in range(1, users_count):
        user = user_factory({
            "email": f"user{i}.email@email.net",
        })
        tests_helper.insert_user(user)
    response = tests_helper.get_request(
        "/users/",
        authenticated_as=email,
        query_params={"offset": 20},
    )
    assert response.status_code == 200
    response_body = response.json()
    users_response = response_body.get("users")
    assert users_response is not None
    assert len(users_response) == 0
    total_count = response_body.get("total_count")
    assert total_count is not None
    assert total_count == users_count
