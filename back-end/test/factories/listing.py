from typing import Any, Dict


def listing_factory(overrides: Dict[str, Any] = {}) -> Dict[str, Any]:
    listing: dict[str, Any] = {
        "title": "Fake Listing",
        "description": "Fake Description",
    }
    listing.update(overrides)
    return listing
