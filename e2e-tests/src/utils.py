import json
import logging
import time
from contextlib import contextmanager
from typing import Any, Dict, Optional

import psycopg2
from playwright.sync_api import Page

logger = logging.getLogger(__name__)


class Helper:
    """
    Helper class with utilities for tests: DB seeding, mocks, etc.
    """
    db_connection: psycopg2.extensions.connection
    mockserver_url: str
    back_end_url: str
    front_end_url: str

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
        self.mockserver_url = mockserver_url
        self.back_end_url = back_end_url
        self.front_end_url = front_end_url

        max_retries = 3
        retry_delay = 1
        last_exception: Optional[Exception] = None

        for attempt in range(max_retries):
            try:
                self.db_connection = psycopg2.connect(
                    database="test",
                    user="test",
                    host="localhost",
                    password="test",
                    port=db_port,
                    connect_timeout=10  # Add a connection timeout
                )
                logger.info(
                  "Successfully connected to the PostgreSQL database"
                  )
                return
            except Exception as e:
                last_exception = e
                if attempt < max_retries - 1:
                    logger.warning(f"Database connection failed: {str(e)}."
                                   f" Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff

        if last_exception:
            logger.error(
                "All database connection attempts failed:"
                f" {str(last_exception)}"
            )
            raise last_exception

    def __del__(self) -> None:
        """Close the database connection when the object is destroyed."""
        if self.db_connection:
            self.db_connection.close()

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
