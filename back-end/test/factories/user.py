from typing import Any, Optional


def user_factory(overrides: Optional[dict[str, Any]] = {}) -> dict[str, Any]:
    user = {
        "email": "fake-user@email.net",
        "username": "fake-user",
        "first_name": "Fake",
        "last_name": "User",
        "is_active": True,
        "is_superuser": False,
    }
    user.update(overrides)

    overrides_email = overrides.get("email")
    if overrides_email is not None:
        lower_email = overrides_email.lower()
        username = lower_email.split("@")[0]
        user["email"] = lower_email
        user["username"] = username

    return user
