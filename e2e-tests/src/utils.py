import datetime
import logging
from contextlib import contextmanager
from typing import Any, Generator

import requests
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
        **auth_config: Any
    ) -> Generator[None, None, None]:
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
        :param auth_config: Additional key-value pairs to configure the
        authentication.
        - is_expired: If True, simulates an expired session.
        - is_invalid: If True, simulates an invalid session.
        :return: A context manager that sets the authentication headers
        """
        page.set_extra_http_headers({
            "Authorization": "Bearer fake-access-token",
        })
        is_expired = auth_config.get("is_expired", False)
        is_invalid = auth_config.get("is_invalid", False)
        if is_expired:
            self.mock_okta_userinfo_response(
                response_body={"error": "expired_token"},
                response_status=401,
            )
        elif is_invalid:
            self.mock_okta_userinfo_response(
                response_body={"error": "invalid_response"},
                response_status=200,
            )
        else:
            self.mock_okta_userinfo_response(
                response_body={"email": email},
                response_status=200,
            )
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

    def clean_up_mocks(self) -> None:
        """
        Clean up the mocks in the MockServer.
        """
        url = f"{self.mockserver_url}/mockserver/reset"
        requests.put(url)

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

    def mock_okta_userinfo_response(
            self,
            response_body: Any,
            response_status: int = 200
            ) -> None:
        """
        Mock Okta's userinfo endpoint.

        :param response_body: The response body to return
        :param response_status: The response status code to return
        """
        self.mock_response(
            request_path="/okta/userinfo",
            request_method="GET",
            response_body=response_body,
            response_status=response_status,
        )

    def mock_response(
            self,
            request_path: str,
            request_method: str = "GET",
            response_body: Any = {},
            response_status: int = 200,
            ) -> None:
        """
        Mock a response from the Mockserver

        :param request_path: The path to match
        :param request_method: The method to match
        :param response_body: The response body to return
        :param response_status: The response status code
        """

        url = f"{self.mockserver_url}/mockserver/expectation"
        mock = {
            "httpRequest": {
                "path": request_path,
                "method": request_method,
            },
            "httpResponse": {
                "body": response_body,
                "statusCode": response_status,
            },
        }

        # Send a PUT request to the MockServer to create the expectation
        requests.put(
            url,
            json=mock,
            headers={"Content-Type": "application/json"},
        )
