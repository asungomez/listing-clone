"""
This file contains the database models for the core app.
"""

from __future__ import annotations

from typing import Any

from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin,
)
from django.db import models


class UserManager(BaseUserManager['User']):
    """Manager for users"""

    def create_user(self, email: str, **extra_fields: dict[str, Any]) -> User:
        """Create, save and return a new user"""
        lowercased_email = email.lower()
        email_parts = lowercased_email.split("@")
        if len(email_parts) != 2:
            raise ValueError("Invalid email")
        username = email_parts[0]
        user: User = self.model(
            email=lowercased_email,
            username=username,
            **extra_fields
            )
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system"""

    """The email field is unique and comes from the Okta token"""
    email = models.EmailField(
        max_length=255,
        unique=True
        )

    """The username is unique and is derived from the email"""
    username = models.CharField(
        max_length=255,
        unique=True
        )

    """The first name of the user"""
    first_name = models.CharField(max_length=255, null=True)

    """The last name of the user"""
    last_name = models.CharField(max_length=255, null=True)

    """When the user last logged in"""
    last_login = models.DateTimeField(
        auto_now=True
        )

    """When the user was created"""
    date_joined = models.DateTimeField(
        auto_now_add=True
        )

    """Whether the user is active or not"""
    is_active = models.BooleanField(default=True)

    """Manager for users"""
    objects = UserManager()

    USERNAME_FIELD = "username"


class UpdatedBy(models.Model):
    """Updated by"""

    """The user that updated the model"""
    updated_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    """The date and time the model was updated"""
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Listing(UpdatedBy):
    """Listing in the system"""

    """The title of the listing"""
    title = models.CharField(max_length=255)

    """The description of the listing"""
    description = models.TextField()


class ListingCoordinator(models.Model):
    """Listing coordinator in the system"""

    """The listing that the coordinator is for"""
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)

    """The user that is the coordinator"""
    coordinator = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    class Meta:
        unique_together = ("listing", "coordinator")
