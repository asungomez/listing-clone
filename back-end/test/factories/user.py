from typing import Any, Dict


def user_factory(overrides: Dict[str, Any] = {}) -> Dict[str, Any]:
    user: dict[str, Any] = {
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
