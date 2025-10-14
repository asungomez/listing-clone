from test.factories.user import user_factory
from test.utils import Helper


def test_mock_session_when_not_authenticated(tests_helper: Helper) -> None:
    """
    Test that the mock session is ignored when the request is
    not authenticated
    """
    impersonated_user = user_factory()
    tests_helper.insert_user(impersonated_user)
    response = tests_helper.get_request(
        "/users/me",
        mock_session_user_id=impersonated_user["id"],
    )
    assert response.status_code == 403


def test_mock_session_when_authenticated_as_non_admin(
    tests_helper: Helper
) -> None:
    """
    Test that the request returns a 403 if the user includes
    the mock session user id but is not an admin
    """
    impersonated_user = user_factory({
        "email": "impersonated.email@email.net",
    })
    tests_helper.insert_user(impersonated_user)
    authenticated_user = user_factory({
        "is_superuser": False,
        "email": "authenticated.email@email.net",
    })
    tests_helper.insert_user(authenticated_user)
    response = tests_helper.get_request(
        "/users/me",
        mock_session_user_id=impersonated_user["id"],
        authenticated_as=authenticated_user["email"],
    )
    assert response.status_code == 403
