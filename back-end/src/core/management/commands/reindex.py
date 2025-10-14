from typing import Any

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from user.indexer import UserIndexer

User = get_user_model()


class Command(BaseCommand):
    help = "Updates the SOLR index for the User model"

    def handle(self, *args: Any, **options: Any) -> None:
        all_users = User.objects.all()
        user_indexer = UserIndexer()
        for user in all_users:
            user_indexer.add(user)
        self.stdout.write(
            self.style.SUCCESS("Successfully reindexed users")
        )
