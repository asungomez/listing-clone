from typing import Optional

from core.indexer import ModelIndexer
from core.models import User


class UserIndexer(ModelIndexer[User]):
    """
    Indexer class for managing the Solr index for the User model.
    """

    def __init__(self) -> None:
        from user.serializers import UserSerializer
        super().__init__(UserSerializer)

    def search_by_email(self, email: str) -> Optional[User]:
        """
        Search the Solr index for a user by email.

        :param email: The email to search for.
        :return: The user if found, None otherwise.
        """
        results = self.search({"email": email})
        if len(results) == 0:
            return None
        return results[0]
