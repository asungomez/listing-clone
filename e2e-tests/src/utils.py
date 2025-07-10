import logging
import time
from typing import Optional

import psycopg2

logger = logging.getLogger(__name__)


class Helper:
    """
    Helper class with utilities for tests: DB seeding, mocks, etc.
    """
    db_connection: psycopg2.extensions.connection
    mockserver_url: str
    back_end_url: str

    def __init__(
            self,
            db_port: int,
            mockserver_url: str,
            back_end_url: str
            ):
        """
        Initialize the Helper class.

        :param db_port: The port of the database
        :param mockserver_url: The URL of the MockServer
        :param back_end_url: The URL of the back-end service
        """
        self.mockserver_url = mockserver_url
        self.back_end_url = back_end_url

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
