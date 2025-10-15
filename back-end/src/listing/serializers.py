from typing import Any, Dict, List, Tuple

from core.models import Listing, ListingCoordinator
from listing.indexer import ListingIndexer
from rest_framework import serializers


class CoordinatorSerializer(serializers.Serializer[Dict[str, Any]]):
    """Serializer for the coordinator object"""

    id = serializers.IntegerField(required=True)
    email = serializers.EmailField(required=True)


class ListingSerializer(serializers.ModelSerializer[Listing]):
    """Serializer for the listing object"""

    indexer = ListingIndexer

    coordinators = serializers.ListField(
        child=CoordinatorSerializer()
    )

    class Meta:
        model = Listing
        fields = (
            "id",
            "title",
            "description",
            "updated_by",
            "updated_at",
            "coordinators"
        )
        read_only_fields = ("id", "updated_by", "updated_at")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the serializer

        :param args: The arguments to initialize the serializer.
        :param kwargs: The keyword arguments to initialize the serializer.
        """
        super().__init__(*args, **kwargs)
        self.indexer = ListingIndexer()

    def to_representation(
        self,
        instance: Listing | Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Represent the listing object

        :param instance: The listing object
        :return: The representation of the listing object
        """
        if isinstance(instance, Listing):
            coordinators = ListingCoordinator.objects.filter(listing=instance)
            coordinators = [
                {
                    "id": coordinator.coordinator.id,
                    "email": coordinator.coordinator.email
                }
                for coordinator in coordinators
            ]
            setattr(instance, "coordinators", coordinators)
        return super().to_representation(instance)

    def save(
        self,
    ) -> None:
        """Create and new listing"""
        try:
            current_user = self.context.get("request").user
            coordinators = self.validated_data.pop("coordinators")
            listing = Listing.objects.create(
                **self.validated_data,
                updated_by_id=current_user.id
            )
            for coordinator in coordinators:
                ListingCoordinator.objects.create(
                    listing=listing,
                    coordinator_id=coordinator.get("id")
                )
            self.indexer.add(listing)
            self._data = self.to_representation(listing)
        except Exception as e:
            raise e

    def search_by_coordinator_id(
        self,
        coordinator_id: int,
        offset: int,
        page_size: int,
    ) -> Tuple[List[Listing], int]:
        """Search for listings by coordinator id"""
        return self.indexer.search_by_coordinator_id(
            coordinator_id,
            offset,
            page_size
        )


class CreateListingSerializer(serializers.Serializer[Dict[str, Any]]):
    """Serializer for the create listing endpoint"""

    title = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
