from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from faker import Faker

from .user import User


@dataclass
class Listing:
    """Listing model for testing purposes."""
    id: Optional[int]
    title: str
    description: str
    coordinators: List[User]


class ListingFactory:
    """Factory for creating Listing instances for testing."""
    faker: Faker

    def __init__(self) -> None:
        self.faker = Faker()

    def generate(self, **kwargs: Any) -> Listing:
        """
        Generate a listing with realistic fake data for unspecified fields.
        """
        listing_values: Dict[str, Any] = {
            "id": None,
            "title": self.faker.sentence(),
            "description": self.faker.text(),
        }
        listing_values.update(kwargs)

        return Listing(**listing_values)
