from typing import Any, Dict, List, Tuple

from core.indexer import ModelIndexer
from core.models import Listing


class ListingIndexer(ModelIndexer[Listing]):
    """Indexer for the Listing model"""

    override_types = {
        "coordinators": "children"
    }

    def __init__(self):
        from listing.serializers import ListingSerializer
        super().__init__(ListingSerializer)

    def add(self, instance: Listing) -> None:
        """Add a listing to the index"""
        serializer = self.serializer_class(instance)
        data = serializer.data
        coordinators = data.pop("coordinators")
        data["coordinators"] = [
            {
                "doc_type": "coordinator",
                "id": f"coordinator:{result.get('id')}:{instance.id}",
                "coordinator_id": result.get('id'),
                "coordinator_email": result.get('email'),
            }
            for result in coordinators
        ]
        data["doc_type"] = "listing"
        self.update(data)

    def search_by_coordinator_id(
        self,
        coordinator_id: int,
        offset: int,
        page_size: int,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Search for listings by coordinator id"""
        return self.search(
            query={"coordinator_id": coordinator_id},
            offset=offset,
            page_size=page_size,
            query_prefix="{!parent which=doc_type_s:listing}",
            fl=(
                "*,[child childFilter=*:*]"
            )
        )

    def reverse_transform_data(self, data: dict) -> dict:
        """Map Solr listing + children to serializer shape.

        - Remove doc_type from parent/children
        - Normalize coordinators to a list of {id, email}
        - Derive coordinator id from coordinator_id or parse from child id
        """
        decoded = super().reverse_transform_data(data)

        # Drop type hint on parent if present
        decoded.pop("doc_type", None)

        coordinators = decoded.get("coordinators")
        if coordinators is not None:
            # Ensure we iterate a list
            if isinstance(coordinators, dict):
                children_iter = [coordinators]
            else:
                children_iter = coordinators

            normalized: list[dict] = []
            for child in children_iter:
                if not isinstance(child, dict):
                    continue
                child = dict(child)  # shallow copy
                child.pop("doc_type", None)

                coord_id = child.get("coordinator_id")
                email = child.get("coordinator_email")

                if coord_id is None:
                    # Fallback: try to parse from composite id
                    child_id = child.get("id")
                    if isinstance(child_id, str):
                        parts = child_id.split(":")
                        try:
                            if len(parts) >= 2 and parts[-2].isdigit():
                                coord_id = int(parts[-2])
                            else:
                                # last numeric token
                                for p in reversed(parts):
                                    if p.isdigit():
                                        coord_id = int(p)
                                        break
                        except Exception:
                            coord_id = None

                if coord_id is not None and email is not None:
                    normalized.append({
                        "id": int(coord_id),
                        "email": email,
                    })

            decoded["coordinators"] = normalized

        if "updated_by" in decoded:
            updated_by = decoded.pop("updated_by")
            decoded["updated_by_id"] = updated_by
        return decoded
