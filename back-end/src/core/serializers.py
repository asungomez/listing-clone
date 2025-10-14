from typing import Generic, TypeVar

from app import settings
from rest_framework import serializers

T = TypeVar("T")


class PaginationSerializer(serializers.Serializer[T], Generic[T]):
    """Serializer for pagination"""

    offset = serializers.IntegerField(min_value=0, default=0, error_messages={
        "min_value": "offset must be greater than or equal to 0",
        "invalid": "offset and page_size must be integers",
    })
    page_size = serializers.IntegerField(
        min_value=1,
        max_value=settings.MAX_PAGE_SIZE,
        default=settings.DEFAULT_PAGE_SIZE,
        error_messages={
            "min_value": "page_size must be greater than 0",
            "max_value": (
                "page_size must be less than or equal to "
                f"{settings.MAX_PAGE_SIZE}"
            ),
            "invalid": "offset and page_size must be integers",
        },
    )
