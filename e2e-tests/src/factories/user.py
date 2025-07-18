from dataclasses import dataclass
from typing import Any, Dict, Optional

from faker import Faker


@dataclass
class User:
    """User model for testing purposes."""
    id: Optional[int]
    is_superuser: bool
    email: str
    username: str
    first_name: str
    last_name: str
    date_joined: str
    is_active: bool


class UserFactory:
    """Factory for creating User instances for testing."""
    faker: Faker

    def __init__(self) -> None:
        self.faker = Faker()

    def generate(self, **kwargs: Any) -> User:
        """
        Generate a user with realistic fake data for unspecified fields.

        :param kwargs: Specific attribute values to override random generation
        :return: A User instance
        """

        fake_email = self.faker.email()
        fake_username = fake_email.split('@')[0]
        user_values: Dict[str, Any] = {
          'id': None,
          'is_superuser': False,
          'email': fake_email,
          'username': fake_username,
          'first_name': self.faker.first_name(),
          'last_name': self.faker.last_name(),
          'date_joined': self.faker.date_time_this_decade().isoformat(),
          'is_active': True,
        }
        user_values.update(kwargs)

        return User(**user_values)
