import json
import logging
from typing import (
    Any, Callable, Dict, Literal, Mapping, Optional, Sequence, Tuple,
)

import psycopg2
import requests
from cryptography.fernet import Fernet

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CUSTOM_SOLR_TRANSFORMATIONS: Dict[
    str,
    Callable[[Dict[str, Any]], Dict[str, Any]]
    ] = {
    "user": lambda document: {
        **document,
        "email_ngram_ng": document.get("email_s")
    },
    "listing": lambda document: {
        **document,
        "doc_type_s": "listing",
    },
}

CUSTOM_SOLR_REVERSE_TRANSFORMATIONS: Dict[
    str,
    Callable[[Dict[str, Any]], Dict[str, Any]]
    ] = {
        "listing": lambda document: {
            **document,
            "coordinators": (
                [document.get("coordinators")]
                if isinstance(document.get("coordinators"), dict)
                else document.get("coordinators")
            )
        }
    }


class Helper:
    """
    Helper class with utilities for tests: requests to the API, creating
    mocks, etc.
    """

    api_url: str
    mockserver_url: str
    db_connection: psycopg2.extensions.connection
    encryption_key: str
    solr_url: str

    def __init__(
            self,
            api_url: str,
            mockserver_url: str,
            db_port: int,
            encryption_key: str,
            solr_url: str,
            ):
        """
        Initialize the Helper class.

        :param api_url: The URL of the API
        :param mockserver_url: The URL of the MockServer
        :param db_port: The port of the database
        :param encryption_key: The encryption key to use for the crypto
        :param solr_url: The URL of the SOLR
        :param solr_core: The core of the SOLR
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
        self.solr_url = solr_url

    def authenticate(
        self,
        email: str,
        method: Literal["header", "cookie"] = "cookie",
        omit_auth_mocking: bool = False,
    ) -> Tuple[Dict[str, str], Dict[str, str]]:
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
            "core_user",
            "core_listing",
            "core_listingcoordinator",
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

    def clean_up_solr(self) -> None:
        """
        Clean up the SOLR index.
        """
        response = requests.post(
            f"{self.solr_url}/update",
            params={"commit": "true"},
            json={"delete": {"query": "*:*"}},
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()

    def encrypt(self, value: str) -> str:
        """
        Encrypt a value using the same encryption key as the one used
        in the API.
        """
        cipher = Fernet(self.encryption_key.encode())
        encrypted = cipher.encrypt(value.encode())
        return encrypted.decode()

    def find_listing_by_id(self, listing_id: int) -> Optional[dict[str, Any]]:
        """
        Find a listing by id.

        :param id: The id of the listing to find
        :return: The listing object if found, None otherwise
        """
        result = self.search_solr(
            document_type="listing",
            query={"id": listing_id},
        )
        if result is None or len(result) == 0:
            return None
        first_result = result[0]
        return first_result

    def find_user_by_email(self, email: str) -> Optional[dict[str, Any]]:
        """
        Find a user by email.

        :param email: The email of the user to find
        :return: The user object
        """
        lower_email = email.lower()
        result = self.search_solr(
            document_type="user",
            query={"email": lower_email},
        )
        if result is None or len(result) == 0:
            return None
        first_result = result[0]
        return first_result

    def get_request(
            self,
            path: str,
            authenticated_as: Optional[str] = None,
            authentication_method: Literal["header", "cookie"] = "cookie",
            mock_session_user_id: Optional[int] = None,
            omit_auth_mocking: bool = False,
            query_params: Optional[Dict[str, Any]] = None,
            ) -> requests.Response:
        """
        Make a request to the API.

        :param path: The path to request
        :param authenticated_as: The email of the user to authenticate as
        :param authentication_method: The method to authenticate with.
        The options are:
        - "header": Authenticate with a header
        - "cookie": Authenticate with a cookie
        :param mock_session_user_id: The id of the user to impersonate
        :param omit_auth_mocking: If True, the authentication mocking will be
        omitted
        :param query_params: The query parameters to pass to the request
        :return: The response object
        """
        url = f"{self.api_url}{path}"
        headers: Dict[str, str] = {
            "Accept": "application/json",
        }
        if mock_session_user_id:
            headers["Mock-Session-User-Id"] = str(mock_session_user_id)
        cookies: Dict[str, Any] = {}
        if authenticated_as is not None:
            auth_headers, auth_cookies = self.authenticate(
                authenticated_as,
                authentication_method,
                omit_auth_mocking
            )
            headers.update(auth_headers)
            cookies.update(auth_cookies)

        response = requests.get(
            url,
            allow_redirects=False,
            headers=headers,
            cookies=cookies,
            params=query_params
            )
        return response

    def index_solr_document(
        self,
        document_type: str,
        document: dict[str, Any]
    ) -> None:
        """
        Index a document into the SOLR.

        :param document_type: The type of the document
        :param document: The document to index
        """
        transformed_document = self.transform_solr_document(
            document_type,
            document
            )
        response = requests.post(
            f"{self.solr_url}/update?commit=true",
            json=[transformed_document],
            headers={"Content-Type": "application/json"}
            )
        response.raise_for_status()

    def insert_listing(self, listing: dict[str, Any]) -> None:
        """
        Insert a listing into the database.

        :param listing: The listing object to insert
        """
        if self.db_connection is None:
            raise Exception("Database connection is not established")
        cursor = self.db_connection.cursor()
        query = """
            INSERT INTO core_listing (
                title,
                description,
                updated_by_id,
                updated_at
            )
            VALUES (
                %(title)s,
                %(description)s,
                %(updated_by)s,
                NOW()
            )
            RETURNING id
        """
        cursor.execute(query, listing)
        returned_element = cursor.fetchone()
        if returned_element is None:
            raise Exception("Error inserting listing into the database")
        listing["id"] = returned_element[0]
        coordinators = listing.get("coordinators")
        if isinstance(coordinators, list):
            for i, coordinator in enumerate[Dict[str, Any]](coordinators):
                coord_query = """
                    INSERT INTO core_listingcoordinator (
                        listing_id,
                        coordinator_id
                    )
                    VALUES (
                        %(listing_id)s,
                        %(coordinator_id)s
                    )
                    RETURNING id
                """
                cursor.execute(coord_query, {
                    "listing_id": listing["id"],
                    "coordinator_id": coordinator["coordinator_id"],
                })
                returned_element = cursor.fetchone()
                if returned_element is None:
                    raise Exception(
                        "Error inserting listing coordinator into the database"
                    )
                listing["coordinators"][i]["id"] = (
                    f"coordinator:{returned_element[0]}"
                    f":{listing['id']}"
                )
                listing["coordinators"][i]["doc_type"] = "coordinator"
        self.db_connection.commit()
        cursor.close()
        self.index_solr_document(
            document_type="listing",
            document=listing
        )

    def insert_user(self, user: dict[str, Any]) -> None:
        """
        Insert a user into the database.

        :param user: The user object to insert
        """
        if self.db_connection is None:
            raise Exception("Database connection is not established")

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
            RETURNING id
        """
        cursor.execute(query, user)
        returned_element = cursor.fetchone()
        if returned_element is None:
            raise Exception("Error inserting user into the database")
        user["id"] = returned_element[0]
        self.db_connection.commit()
        cursor.close()
        self.index_solr_document(
            document_type="user",
            document=user
        )

    def mock_okta_revoke_response(
            self,
            response_body: Any,
            response_status: int = 200,
            ) -> None:
        """
        Mock Okta's revoke endpoint.

        :param response_body: The response body to return
        :param response_status: The response status code to return
        """
        self.mock_response(
            request_path="/okta/oauth/revoke",
            request_method="POST",
            response_body=response_body,
            response_status=response_status,
        )

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

    def post_request(
            self,
            path: str,
            body: Any = None,
            authenticated_as: Optional[str] = None,
            authentication_method: Literal["header", "cookie"] = "cookie",
            omit_auth_mocking: bool = False,
            ) -> requests.Response:
        """
        Make a POST request to the API.
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
        response = requests.post(
            url,
            json=body,
            headers=headers,
            cookies=cookies
        )
        return response

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

    def reverse_transform_solr_document(
        self,
        document: dict[str, Any],
        document_type: str
    ) -> dict[str, Any]:
        """
        Reverse transform a document to get it ready for the database.

        :param document_type: The type of the document
        :param document: The document to reverse transform
        :return: The reverse transformed document
        """
        transformed_document: Dict[str, Any] = {}
        for key, value in document.items():
            if key == "id":
                try:
                    id_value = value.split(":")[-1]
                    numeric_value = int(id_value)
                    transformed_document[key] = numeric_value
                except Exception as e:
                    raise e
            elif isinstance(value, list):
                transformed_document[key] = [
                    self.reverse_transform_solr_document(item, "child")
                    if isinstance(item, dict)
                    else item
                    for item in value
                ]
            elif isinstance(value, dict):
                transformed_document[key] = (
                    self.reverse_transform_solr_document(value, "child")
                )
            elif key.endswith("_s"):
                transformed_document[key[:-2]] = value
            elif key.endswith("_i"):
                transformed_document[key[:-2]] = int(value)
            elif key.endswith("_f"):
                transformed_document[key[:-2]] = float(value)
            elif key.endswith("_b"):
                transformed_document[key[:-2]] = bool(value)
        if document_type in CUSTOM_SOLR_REVERSE_TRANSFORMATIONS:
            transformer_function = CUSTOM_SOLR_REVERSE_TRANSFORMATIONS[
                document_type
            ]
            transformed_document = transformer_function(transformed_document)
        return transformed_document

    def search_solr(
        self,
        document_type: str,
        query: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """
        Search the SOLR index.

        :param document_type: The type of the document
        :param query: The query to search for
        :return: The result of the search
        """
        transformed_query = self.transform_solr_document(document_type, query)

        def escape_value(value: Any) -> str:
            if isinstance(value, str):
                return value.replace(":", r"\:")
            return str(value)

        query_parts = [
            f"{key}:{escape_value(value)}"
            for key, value in transformed_query.items()
        ]
        query_string = " AND ".join(query_parts)
        params: Dict[str, Any] = {
            "q": query_string,
            "wt": "json",
            "fl": "*,[child childFilter=*:*]"
        }

        response = requests.get(
            f"{self.solr_url}/select",
            params=params
            )
        response.raise_for_status()
        response_body = response.json()
        docs = response_body.get("response", {}).get("docs", [])
        return [
            self.reverse_transform_solr_document(doc, document_type)
            for doc in docs
        ]

    def transform_solr_document(
        self,
        document_type: str,
        document: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Transform a document to get it ready for SOLR.

        :param document_type: The type of the document
        :param document: The document to transform
        :return: The transformed document
        """
        transformed_document: Dict[str, Any] = {}
        for key, value in document.items():
            if key == "id":
                transformed_document[key] = f"{document_type}:{value}"
            elif isinstance(value, list):
                transformed_document[key] = [
                    self.transform_solr_document("child", item)
                    if isinstance(item, dict)
                    else item
                    for item in value
                ]
            elif isinstance(value, dict):
                transformed_document[key] = self.transform_solr_document(
                    "child",
                    value
                )
            elif isinstance(value, str):
                transformed_document[f"{key}_s"] = value
            elif isinstance(value, bool):
                transformed_document[f"{key}_b"] = value
            elif isinstance(value, int):
                transformed_document[f"{key}_i"] = value
            elif isinstance(value, float):
                transformed_document[f"{key}_f"] = value
        if document_type in CUSTOM_SOLR_TRANSFORMATIONS:
            transformed_document = CUSTOM_SOLR_TRANSFORMATIONS[document_type](
                transformed_document
            )

        return transformed_document
