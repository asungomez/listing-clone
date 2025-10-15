from typing import Any

from core.auth import (
    AuthenticatedAPIView, AuthenticatedRequest, AuthenticatedViewSet,
)
from core.swagger import swagger_authenticated_schema
from listing.serializers import (
    CreateListingSerializer, ListingSerializer, ListingsListResponseSerializer,
)
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response


class ListingViewSet(AuthenticatedViewSet, CreateModelMixin):
    """View set for the listing model"""

    serializer_class = ListingSerializer

    @swagger_authenticated_schema(
        responses={
            201: ListingSerializer(),
        },
        request_body=CreateListingSerializer(),
    )
    def create(
        self,
        request: AuthenticatedRequest,
        *args: Any,
        **kwargs: Any
    ) -> Response:
        """
        Create a new listing

        :param request: The request object
        :param args: The arguments
        :param kwargs: The keyword arguments
        :return: The response object
        """
        coordinator = {
            "id": request.user.id,
            "email": request.user.email
        }
        request.data["coordinators"] = [coordinator]
        return super().create(request, *args, **kwargs)

    def get_serializer_context(self) -> dict[str, Any]:
        """
        Provide serializer context with request, format and view

        :return: The serializer context
        """
        return {
            "request": self.request,
            "format": getattr(self, "format_kwarg", None),
            "view": self,
        }

    def get_serializer(
        self,
        *args: Any,
        **kwargs: Any
    ) -> ListingSerializer:
        """
        Get the serializer for the view

        :param args: The arguments
        :param kwargs: The keyword arguments
        :return: The serializer
        """
        kwargs.setdefault("context", self.get_serializer_context())
        return ListingSerializer(*args, **kwargs)


class MyListingsView(AuthenticatedAPIView):
    """View for the my listings endpoint"""

    serializer = ListingsListResponseSerializer()

    @swagger_authenticated_schema(
        responses={200: ListingsListResponseSerializer()},
        operation_id="my_listings"
    )
    def get(self, request: AuthenticatedRequest) -> Response:
        listings, total_count = self.serializer.search_by_coordinator_id(
            request.user.id,
            0,
            10
        )
        return Response({
            "listings": listings,
            "total_count": total_count,
        })
