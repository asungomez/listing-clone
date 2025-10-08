import json
from typing import Callable, Optional, Tuple

import requests
from core.crypto import Crypto
from core.models import User
from django.conf import settings
from django.http import HttpRequest
from django.http.response import HttpResponseBase
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.views import APIView
from user.serializers import UserSerializer


class SessionExpiredException(Exception):
    """Raised when the credentials are expired"""
    pass


class SessionInvalidException(Exception):
    """Raised when the credentials are invalid"""
    pass


class InactiveUserException(Exception):
    """Raised when the user is inactive"""
    pass


class TokenManager:
    """
    Class to manage Okta authentication and token handling
    """

    def authenticate(
        self,
        access_token: str,
        refresh_token: Optional[str]
    ) -> Tuple[str, str]:
        """
        Get the email from the token. If the access token is invalid or
        expired, it will use the refresh token to get a new access token.

        :param token: The JWT token received from Okta

        :return: The email address from the token, the access token, and the
        refresh token
        """
        url = f"{settings.OKTA['DOMAIN']}/userinfo"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 401:
            if refresh_token:
                access_token = self.get_access_token_from_refresh_token(
                    refresh_token
                    )
                headers["Authorization"] = f"Bearer {access_token}"
                response = requests.get(url, headers=headers)
                if response.status_code == 401:
                    raise SessionExpiredException(
                        "The credentials are expired"
                    )
            else:
                raise SessionExpiredException(
                    "The credentials are expired"
                )
        elif response.status_code/100 == 4:
            raise SessionInvalidException(
                "The credentials are invalid"
            )
        response.raise_for_status()
        userinfo = response.json()
        email: str = userinfo.get("email")
        if not email:
            raise SessionInvalidException("Email not found in the token")
        return email, access_token

    def get_tokens_from_provider(self, code: str) -> Tuple[str, str]:
        """
        Make a request to Okta to retrieve the access token based on the
        code

        :param code: The authorization code received from Okta

        :return: The access token and refresh token
        """
        url = f"{settings.OKTA['DOMAIN']}/oauth/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.OKTA["LOGIN_REDIRECT"],
            "client_id": settings.OKTA["CLIENT_ID"],
            "client_secret": settings.OKTA["CLIENT_SECRET"]
        }
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        access_token: str = response.json().get("access_token")
        refresh_token: str = response.json().get("refresh_token")
        return access_token, refresh_token

    def get_tokens_from_request(self, request: HttpRequest) -> Tuple[
        Optional[str], Optional[str]
    ]:
        """
        Get the tokens from the request. It checks both the cookies and the
        Authorization header.

        :param request: The request object

        :return: A tuple containing the access token and refresh token, or None
        """
        encrypted_credentials = request.COOKIES.get(
            settings.AUTH_COOKIE_CONFIG["NAME"]
            )
        if encrypted_credentials is None:
            auth_header = request.headers.get("Authorization")
            if auth_header:
                header_parts = auth_header.split(" ")
                if len(header_parts) >= 2 and header_parts[0] == "Bearer":
                    access_token = " ".join(header_parts[1:])
                    refresh_token = None
                    return access_token, refresh_token
                else:
                    raise ValueError("Invalid authorization header")
            return None, None
        else:
            crypto = Crypto()
            credentials_json = crypto.decrypt(encrypted_credentials)
            credentials = json.loads(credentials_json)
            access_token = credentials.get("access_token")
            refresh_token = credentials.get("refresh_token")
        return access_token, refresh_token

    def get_access_token_from_refresh_token(
        self, refresh_token: str
    ) -> str:
        """
        Get a new access token using the refresh token
        :param refresh_token: The refresh token to use for getting a new
        access token
        :return: The new access token
        """
        url = f"{settings.OKTA['DOMAIN']}/oauth/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": settings.OKTA["CLIENT_ID"],
            "client_secret": settings.OKTA["CLIENT_SECRET"]
        }
        response = requests.post(url, headers=headers, data=payload)
        if response.status_code == 401:
            raise SessionExpiredException(
                "The credentials are expired"
            )
        elif response.status_code/100 == 4:
            raise SessionInvalidException(
                "The credentials are invalid"
            )
        response.raise_for_status()
        access_token: Optional[str] = response.json().get("access_token")
        if not access_token:
            raise ValueError("Access token not found in the response")
        return access_token

    def invalidate_token(self, access_token: str) -> None:
        """
        Invalidate the token
        :param access_token: The access token to invalidate
        """
        url = f"{settings.OKTA['DOMAIN']}/oauth/revoke"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }
        payload = {
            "token": access_token,
            "token_type_hint": "access_token",
            "client_id": settings.OKTA["CLIENT_ID"],
            "client_secret": settings.OKTA["CLIENT_SECRET"]
        }
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()

    def remove_credentials_from_cookies(
        self,
        response: HttpResponseBase
    ) -> None:
        """
        Remove the credentials from the cookies
        :param response: The response object
        """
        response.delete_cookie(
            key=settings.AUTH_COOKIE_CONFIG["NAME"],
            domain=settings.AUTH_COOKIE_CONFIG["DOMAIN"],
            path=settings.AUTH_COOKIE_CONFIG["PATH"],
            samesite=settings.AUTH_COOKIE_CONFIG["SAMESITE"],
        )

    def set_credentials_as_cookie(
        self,
        response: HttpResponseBase,
        access_token: str,
        refresh_token: str
    ) -> None:
        """
        Set the access and refresh tokens as a cookie in the response
        :param response: The response object
        :param access_token: The access token to set in the cookie
        :param refresh_token: The refresh token to set in the cookie
        """
        crypto = Crypto()
        credentials_map = {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
        credentials = json.dumps(credentials_map)
        encrypted_credentials = crypto.encrypt(credentials)

        response.set_cookie(
            key=settings.AUTH_COOKIE_CONFIG["NAME"],
            value=encrypted_credentials,
            domain=settings.AUTH_COOKIE_CONFIG["DOMAIN"],
            path=settings.AUTH_COOKIE_CONFIG["PATH"],
            max_age=int(
                settings.AUTH_COOKIE_CONFIG["LIFETIME"].total_seconds()
            ),
            secure=settings.AUTH_COOKIE_CONFIG["SECURE"],
            httponly=settings.AUTH_COOKIE_CONFIG["HTTP_ONLY"],
            samesite=settings.AUTH_COOKIE_CONFIG["SAMESITE"],
        )


class OktaAuthentication(authentication.BaseAuthentication):
    """
    Authentication class for Okta
    """

    def authenticate(self, request: HttpRequest) -> Tuple[
        Optional[User], None
    ]:
        """
        Authenticate the user based on the token
        """
        try:
            token_manager = TokenManager()
            # DRF passes a Request; get underlying HttpRequest for flags
            base_request = getattr(request, "_request", request)
            at, rt = token_manager.get_tokens_from_request(base_request)
            original_access_token = at
            if at is None:
                return None, None
            email, at = token_manager.authenticate(at, rt)
            user = UserSerializer().find_by_email(email)
            if not user.is_active:
                raise InactiveUserException("User is inactive")
            # If access token changed (refreshed), mark it for response cookies
            if original_access_token != at and rt is not None:
                setattr(base_request, "auth_tokens_to_set", (at, rt))
            return user, None
        except SessionExpiredException as e:
            base_req = getattr(request, "_request", request)
            setattr(base_req, "delete_auth_cookie", True)
            raise AuthenticationFailed(
                {
                    "message": str(e),
                    "code": "session_expired"
                }
            )
        except SessionInvalidException as e:
            base_req = getattr(request, "_request", request)
            setattr(base_req, "delete_auth_cookie", True)
            raise AuthenticationFailed(
                {
                    "message": str(e),
                    "code": "session_invalid"
                }
            )
        except InactiveUserException as e:
            base_req = getattr(request, "_request", request)
            setattr(base_req, "delete_auth_cookie", True)
            raise AuthenticationFailed(
                {
                    "message": str(e),
                    "code": "inactive_user"
                }
            )
        except User.DoesNotExist:
            base_req = getattr(request, "_request", request)
            setattr(base_req, "delete_auth_cookie", True)
            raise AuthenticationFailed(
                {
                    "message": "User not found",
                    "code": "user_not_found"
                }
            )
        except ValueError as e:
            base_req = getattr(request, "_request", request)
            setattr(base_req, "delete_auth_cookie", True)
            raise AuthenticationFailed(
                {
                    "message": str(e),
                    "code": "session_invalid"
                }
            )


class AuthenticationCookieMiddleware:
    """
    Middleware to synchronize authentication cookies based on flags set
    during DRF authentication.
    - If request.auth_tokens_to_set is present, set refreshed credentials.
    - If request.delete_auth_cookie is True, delete credentials cookie.
    """

    def __init__(
        self,
        get_response: Callable[[HttpRequest], HttpResponseBase]
    ) -> None:
        self.get_response = get_response
        self.token_manager = TokenManager()

    def __call__(self, request: HttpRequest) -> HttpResponseBase:
        response = self.get_response(request)
        return self.process_response(request, response)

    def process_response(
        self,
        request: HttpRequest,
        response: HttpResponseBase
    ) -> HttpResponseBase:
        to_set = getattr(request, "auth_tokens_to_set", None)
        to_delete = getattr(request, "delete_auth_cookie", False)
        if to_set is not None:
            at, rt = to_set
            self.token_manager.set_credentials_as_cookie(response, at, rt)
        elif to_delete:
            self.token_manager.remove_credentials_from_cookies(response)
        return response


class AuthenticatedRequest(Request):
    user: User


class AuthenticatedAPIView(APIView):
    authentication_classes = [OktaAuthentication]
    permission_classes = [IsAuthenticated]
