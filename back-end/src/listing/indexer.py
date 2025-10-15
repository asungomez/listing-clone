from typing import List, Tuple

from core.indexer import ModelIndexer
from core.models import Listing


class ListingIndexer(ModelIndexer[Listing]):
    """Indexer for the Listing model"""

    override_types = {}

    def __init__(self):
        from listing.serializers import ListingSerializer
        super().__init__(ListingSerializer)

    def add(self, instance: Listing) -> None:
        """Add a listing to the index"""
        serializer = self.serializer_class(instance)
        data = serializer.data
        coordinators = data.pop("coordinators")
        data["_childDocuments_"] = [
            {
                "doc_type": "coordinator",
                "id": f"coordinator:{result.get('id')}:{instance.id}",
                "coordinator_id": result.get('id'),
                "coordinator_email": result.get('email'),
            }
            for result in coordinators
        ]
        self.update(data)

    def search_by_coordinator_id(
        self,
        coordinator_id: int,
        offset: int,
        page_size: int,
    ) -> Tuple[List[Listing], int]:
        """Search for listings by coordinator id"""
        return self.search(
            {"coordinators": coordinator_id},
            offset,
            page_size
        )
