from typing import Any, Dict, List, Optional

from core.indexer import ModelIndexer
from core.models import User


class UserIndexer(ModelIndexer[User]):
    """
    Indexer class for managing the Solr index for the User model.
    """

    override_types: Optional[Dict[str, str]] = {
        "email_ngram": "ng"
    }

    def __init__(self) -> None:
        from user.serializers import UserSerializer
        super().__init__(UserSerializer)

    def add(self, instance: User) -> None:
        """
        Index a new user into the Solr index.
        """
        serializer = self.serializer_class(instance)
        data = serializer.data
        # duplicate the field to use as ngram search matcher
        if "email" in data:
            data["email_ngram"] = data["email"]
        self.update(data)

    def find_by_email(self, email: str) -> Optional[User]:
        """
        Search the Solr index for a user by email.

        :param email: The email to search for.
        :return: The user if found, None otherwise.
        """
        results = self.search({"email": email})
        if len(results) == 0:
            return None
        return results[0]

    def reverse_transform_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reverse transform the data from the Solr index.
        Remove the duplicate email text field.

        :param data: The data to reverse transform.
        :return: The reverse transformed data.
        """
        data = super().reverse_transform_data(data)
        if "email_ngram" in data:
            del data["email_ngram"]
        return data

    def search_by_email(
        self,
        email: str,
        offset: int,
        page_size: int,
    ) -> tuple[List[User], int]:
        """
        Search users by email with pagination.

        :param email: The email text to search within.
        :param offset: The starting offset in the result set.
        :param page_size: The number of results per page.
        :return: A tuple (results, total_count).
        """
        return self.search_paginated(
            {"email_ngram": email},
            offset,
            page_size
            )

    def all_users(
        self,
        offset: int,
        page_size: int,
    ) -> tuple[List[User], int]:
        """
        Get all users with pagination.

        :param offset: The starting offset in the result set.
        :param page_size: The number of results per page.
        :return: A tuple (results, total_count).
        """
        return self.search_paginated({}, offset, page_size)
