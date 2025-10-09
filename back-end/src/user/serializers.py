"""
Serializers for the User API view
"""
from typing import Any, List, Tuple

from core.models import User
from django.contrib.auth import get_user_model
from rest_framework import serializers
from user.indexer import UserIndexer


class UserSerializer(serializers.ModelSerializer[User]):
    """Serializer for the user object"""

    indexer: UserIndexer

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the serializer

        :param args: The arguments to initialize the serializer.
        :param kwargs: The keyword arguments to initialize the serializer.
        """
        super().__init__(*args, **kwargs)
        self.indexer = UserIndexer()

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_superuser",
            )
        read_only_fields = ("id", "email", "username")

    def create(self, validated_data: dict[str, Any]) -> User:
        """Create and return a new user"""
        try:
            user = get_user_model().objects.create_user(**validated_data)
            self.indexer.add(user)
            return user
        except Exception as e:
            raise e

    def find_by_email(self, email: str) -> User:
        """Find a user by email"""
        lower_email = email.lower()
        user = self.indexer.find_by_email(lower_email)
        if not user:
            raise User.DoesNotExist("User not found")
        return user

    def all_users(
        self,
        offset: int,
        page_size: int
    ) -> Tuple[List[User], int]:
        """Get paginated users and total count from the Solr index"""
        users, total = self.indexer.all_users(offset, page_size)
        return users, total


class CurrentUserResponseSerializer(serializers.Serializer):
    """Response serializer for the current user endpoint."""

    user = UserSerializer()


class ListUsersResponseSerializer(serializers.Serializer):
    """Response serializer for the list users endpoint."""

    users = UserSerializer(many=True)
    total_count = serializers.IntegerField()

    def search_by_email(
        self,
        email: str,
        offset: int,
        page_size: int
    ) -> Tuple[List[User], int]:
        """Search users by email with pagination and get total count"""
        lower_email = email.lower()
        users, total = self.indexer.search_by_email(
            lower_email,
            offset,
            page_size
            )
        return users, total
