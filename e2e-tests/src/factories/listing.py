import datetime
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
    updated_by: int
    updated_at: datetime.datetime


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
            "coordinators": [],
            "updated_by": 0,
            "updated_at": datetime.datetime.now(),
        }
        listing_values.update(kwargs)

        # If coordinators provided and updated_by not set, default to first
        # coordinator id
        if (
            listing_values.get("coordinators")
            and not listing_values.get("updated_by")
        ):
            first = listing_values["coordinators"][0]
            listing_values["updated_by"] = getattr(first, "id", 0) or 0

        return Listing(**listing_values)
