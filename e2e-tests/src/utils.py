import datetime
import json
import logging
from contextlib import contextmanager
from typing import Any, Dict

from playwright.sync_api import Page
from sqlalchemy import MetaData, Table, create_engine, inspect, text
from sqlalchemy.engine import Engine

from .factories.user import User

logger = logging.getLogger(__name__)


class Helper:
    """
    Helper class with utilities for tests: DB seeding, mocks, etc.
    """
    mockserver_url: str
    back_end_url: str
    front_end_url: str
    db_engine: Engine
    db_metadata: MetaData

    def __init__(
            self,
            db_port: int,
            mockserver_url: str,
            back_end_url: str,
            front_end_url: str
            ):
        """
        Initialize the Helper class.

        :param db_port: The port of the database
        :param mockserver_url: The URL of the MockServer
        :param back_end_url: The URL of the back-end service
        :param front_end_url: The URL of the front-end service
        """
        self.db_engine = create_engine(
            f"postgresql+psycopg2://test:test@localhost:{db_port}/test"
        )
        self.db_metadata = MetaData()

        self.mockserver_url = mockserver_url
        self.back_end_url = back_end_url
        self.front_end_url = front_end_url

    def __del__(self) -> None:
        """Close the database connection when the object is destroyed."""
        if self.db_engine:
            self.db_engine.dispose()

    @contextmanager
    def authenticated_context(
        self,
        page: Page,
        email: str,
        **token_extras: Dict[str, Any]
    ):
        """
        Context manager for authentication that automatically cleans up.

        Usage:
        with tests_helper.authenticated_context(
            page,
            "user@example.com",
            is_expired=True
        ):
            page.goto("/")
            # Test with authentication
        # Headers are automatically cleared when exiting the context

        :param page: The Playwright Page object to set headers on.
        :param email: The email address to use for authentication.
        :param token_extras: Additional key-value pairs to include in
        the token.
        - is_expired: If True, simulates an expired session.
        - is_invalid: If True, simulates an invalid session.
        :return: A context manager that sets the authentication headers
        """
        token_payload = {"sub": email, **token_extras}
        token_json = json.dumps(token_payload)
        page.set_extra_http_headers({
            "Authorization": f"Bearer {token_json}",
        })
        try:
            yield
        finally:
            page.set_extra_http_headers({})

    def clean_up_db(self) -> None:
        """
        Clean up the test database by deleting all data from tables
        except those starting with 'django_'.
        This is useful for resetting the database state between tests.
        """
        inspector = inspect(self.db_engine)
        tables = inspector.get_table_names()

        with self.db_engine.begin() as connection:
            # Temporarily disable foreign key constraints
            connection.execute(text("SET CONSTRAINTS ALL DEFERRED"))

            # Process each table individually
            for table in tables:
                if not table.startswith("django_"):
                    preparer = self.db_engine.dialect.identifier_preparer
                    quoted_table = preparer.quote_identifier(table)

                    # Use TRUNCATE for faster deletion
                    connection.execute(text(
                        f"TRUNCATE TABLE {quoted_table} CASCADE"
                        ))

            # Re-enable foreign key constraints
            connection.execute(text("SET CONSTRAINTS ALL IMMEDIATE"))

    def db_table(self, table_name: str) -> Table:
        """
        Get a SQLAlchemy Table object for the specified table name.

        :param table_name: The name of the table to get.
        :return: A SQLAlchemy Table object.
        """
        return Table(
            table_name,
            self.db_metadata,
            autoload_with=self.db_engine
        )

    def insert_user(self, user: User) -> None:
        """
        Insert a user into the test database.

        :param user: The User instance to insert.
        """
        with self.db_engine.begin() as connection:
            users_table = self.db_table("core_user")
            insert_stmt = users_table.insert().values(
                password='',
                last_login=datetime.datetime.now(),
                email=user.email,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                date_joined=user.date_joined,
                is_active=user.is_active,
                is_superuser=user.is_superuser
            )
            result = connection.execute(insert_stmt)
            id = result.inserted_primary_key[0]
            user.id = id
