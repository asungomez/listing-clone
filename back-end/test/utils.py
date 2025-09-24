import json
from typing import Any, Dict, Literal, Mapping, Optional, Sequence, Tuple

import psycopg2
import requests
from cryptography.fernet import Fernet


class Helper:
    """
    Helper class with utilities for tests: requests to the API, creating
    mocks, etc.
    """

    api_url: str
    mockserver_url: str
    db_connection: psycopg2.extensions.connection
    encryption_key: str

    def __init__(
            self,
            api_url: str,
            mockserver_url: str,
            db_port: int,
            encryption_key: str,
            ):
        """
        Initialize the Helper class.

        :param api_url: The URL of the API
        :param mockserver_url: The URL of the MockServer
        :param db_port: The port of the database
        :param encryption_key: The encryption key to use for the crypto
        """
        self.api_url = api_url
        self.mockserver_url = mockserver_url
        self.db_connection = psycopg2.connect(
            database="test",
            user="test",
            host="localhost",
            password="test",
            port=db_port
        )
        self.encryption_key = encryption_key

    def authenticate(
        self,
        email: str,
        method: Literal["header", "cookie"] = "cookie",
        omit_auth_mocking: bool = False,
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Authenticate a user in a request.

        :param email: The email of the user to authenticate as
        :param method: The method to authenticate with. The options are:
        - "header": Authenticate with a header
        - "cookie": Authenticate with a cookie
        :param omit_auth_mocking: If True, the authentication mocking will be
        omitted
        :return: The headers and the cookies
        """
        if not omit_auth_mocking:
            self.mock_okta_userinfo_response(
                response_body={
                    "email": email
                }
            )
        if method == "header":
            return {
                "Authorization": "Bearer fake-access-token"
            }, {}
        else:
            credentials_map = {
                "access_token": "fake-access-token",
                "refresh_token": "fake-refresh-token",
            }
            credentials = json.dumps(credentials_map)
            encrypted_credentials = self.encrypt(credentials)
            return {}, {
                "credentials": encrypted_credentials
            }

    def clean_up_db(self) -> None:
        """
        Clean up the database.
        This is used to remove all data from the db.
        """
        tables_to_clean = [
            "core_user"
        ]
        for table in tables_to_clean:
            query = f"DELETE FROM {table}"
            self.query_db(query)

    def clean_up_mocks(self) -> None:
        """
        Clean up the mocks in the MockServer.
        """
        url = f"{self.mockserver_url}/mockserver/reset"
        requests.put(url)

    def encrypt(self, value: str) -> str:
        """
        Encrypt a value using the same encryption key as the one used
        in the API.
        """
        cipher = Fernet(self.encryption_key.encode())
        encrypted = cipher.encrypt(value.encode())
        return encrypted.decode()

    def find_user_by_email(self, email: str) -> Optional[dict[str, Any]]:
        """
        Find a user by email.

        :param email: The email of the user to find
        :return: The user object
        """
        lower_email = email.lower()
        query = """
        SELECT
            id, email, username, first_name, last_name
        FROM core_user
        WHERE email = %s
        """
        params = (lower_email,)
        result = self.query_db(query, params)
        if result is None or len(result) == 0:
            return None
        first_result = result[0]
        if len(first_result) < 5:
            raise ValueError(
                "The result of the user query does not contain all the fields"
            )
        user_dict = {
            "id": first_result[0],
            "email": first_result[1],
            "username": first_result[2],
            "first_name": first_result[3],
            "last_name": first_result[4],
        }
        return user_dict

    def get_request(
            self,
            path: str,
            authenticated_as: Optional[str] = None,
            authentication_method: Literal["header", "cookie"] = "cookie",
            omit_auth_mocking: bool = False,
            ) -> requests.Response:
        """
        Make a request to the API.

        :param path: The path to request
        :param authenticated_as: The email of the user to authenticate as
        :param authentication_method: The method to authenticate with.
        The options are:
        - "header": Authenticate with a header
        - "cookie": Authenticate with a cookie
        :param omit_auth_mocking: If True, the authentication mocking will be
        omitted
        :return: The response object
        """
        url = f"{self.api_url}{path}"
        headers = {
            "Accept": "application/json",
        }
        cookies: Dict[str, Any] = {}
        if authenticated_as is not None:
            headers, cookies = self.authenticate(
                authenticated_as,
                authentication_method,
                omit_auth_mocking
            )
            headers.update(headers)
            cookies.update(cookies)
        response = requests.get(
            url,
            allow_redirects=False,
            headers=headers,
            cookies=cookies
            )
        return response

    def insert_user(self, user: dict[str, Any]) -> None:
        """
        Insert a user into the database.

        :param user: The user object to insert
        """
        if self.db_connection is None:
            return None

        cursor = self.db_connection.cursor()
        query = """
            INSERT INTO core_user (
                email,
                first_name,
                last_name,
                username,
                is_active,
                is_superuser,
                password,
                last_login,
                date_joined
            )
            VALUES (
                %(email)s,
                %(first_name)s,
                %(last_name)s,
                %(username)s,
                %(is_active)s,
                %(is_superuser)s,
                'password',
                NOW(),
                NOW()
            )
        """
        cursor.execute(query, user)
        self.db_connection.commit()
        cursor.close()

    def mock_okta_token_response(
            self,
            response_body: Any,
            response_status: int = 200,
            grant_type: Literal[
                "authorization_code",
                "refresh_token"
                ] = "authorization_code"
            ) -> None:
        """
        Mock Okta's token endpoint.

        :param response_body: The response body to return
        :param response_status: The response status code to return
        :param grant_type: The grant type to match
        """

        self.mock_response(
            request_path="/okta/oauth/token",
            request_method="POST",
            response_body=response_body,
            response_status=response_status,
            request_body={
                "grant_type": grant_type
            },
        )

    def mock_okta_userinfo_response(
            self,
            response_body: Any,
            response_status: int = 200,
            times: Optional[int] = None
            ) -> None:
        """
        Mock Okta's userinfo endpoint.

        :param response_body: The response body to return
        :param response_status: The response status code to return
        :param times: The number of times to match the request.
        None means infinite
        """
        self.mock_response(
            request_path="/okta/userinfo",
            request_method="GET",
            response_body=response_body,
            response_status=response_status,
            times=times,
        )

    def mock_response(
            self,
            request_path: str,
            request_method: str = "GET",
            response_body: Any = {},
            response_status: int = 200,
            request_body: Any = None,
            times: Optional[int] = None
            ) -> None:
        """
        Mock a response from the Mockserver

        :param request_path: The path to match
        :param request_method: The method to match
        :param response_body: The response body to return
        :param response_status: The response status code
        :param request_body: The request body to match
        :param times: The number of times to match the request.
        None means infinite
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

        if request_body:
            mock["httpRequest"]["body"] = {
                "type": "JSON",
                "json": request_body,
                "matchType": "ONLY_MATCHING_FIELDS"
            }

        if times:
            mock["times"] = {
                "remainingTimes": times,
                "unlimited": False,
            }

        # Send a PUT request to the MockServer to create the expectation
        requests.put(
            url,
            json=mock,
            headers={"Content-Type": "application/json"},
        )

    def query_db(
            self,
            query: str,
            params: Sequence[Any] | Mapping[str, Any] | None = None
            ) -> Optional[list[tuple[Any, Any]]]:
        """
        Query the database.

        :param query: The SQL query to execute
        :param params: The parameters to pass to the query

        :return: The result of the query
        """
        if self.db_connection is None:
            return None
        cursor = self.db_connection.cursor()
        cursor.execute(query, params)
        result = None
        try:
            result = cursor.fetchall()
        except psycopg2.ProgrammingError:
            pass
        cursor.close()
        return result
