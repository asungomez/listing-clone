from core.auth import (
    AdminAPIView, AuthenticatedAPIView, AuthenticatedRequest, TokenManager,
)
from django.conf import settings
from django.contrib.auth import get_user_model
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    CurrentUserResponseSerializer, ListUsersResponseSerializer, UserSerializer,
)

User = get_user_model()


class CurrentUserView(AuthenticatedAPIView):

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="Current user",
                schema=CurrentUserResponseSerializer(),
            )
        }
    )
    def get(self, request: AuthenticatedRequest) -> Response:
        serializer = CurrentUserResponseSerializer({"user": request.user})
        return Response(serializer.data)


class ListUsersView(AdminAPIView):

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="List users",
                schema=ListUsersResponseSerializer(),
            )
        },
        manual_parameters=[
            openapi.Parameter(
                "email",
                openapi.IN_QUERY,
                description="Filter users by email",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                "offset",
                openapi.IN_QUERY,
                description="Starting index for results (default 0)",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
            openapi.Parameter(
                "page_size",
                openapi.IN_QUERY,
                description="Number of results to return (default 25)",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
        ],
    )
    def get(self, request: AuthenticatedRequest) -> Response:
        """
        List users.
        :param request: The request object
        :return: The response object
        """
        email = request.query_params.get("email")
        try:
            offset = int(request.query_params.get("offset", 0))
            page_size = int(request.query_params.get("page_size", 25))
        except ValueError:
            return Response(
                {"message": "offset and page_size must be integers"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if offset < 0:
            offset = 0
        if page_size <= 0:
            page_size = 1
        if page_size > 100:
            page_size = 100

        user_serializer = UserSerializer()
        if email is None:
            users, total_count = user_serializer.all_users(
                offset,
                page_size
                )
        else:
            users, total_count = user_serializer.search_by_email(
                email,
                offset,
                page_size
                )
        serializer = ListUsersResponseSerializer({
            "users": users,
            "total_count": total_count,
        })
        return Response(serializer.data)


class LoginView(APIView):

    serializer = UserSerializer()

    @swagger_auto_schema(
        responses={302: openapi.Response(
            description="Redirect to the login page",
            type=openapi.TYPE_STRING,
        )},
        manual_parameters=[
            openapi.Parameter(
                "code",
                openapi.IN_QUERY,
                description="Code from the OAuth provider",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                "state",
                openapi.IN_QUERY,
                description="State from the OAuth provider",
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ]
    )
    def get(self, request: Request) -> Response:
        code = request.query_params.get("code")
        state = request.query_params.get("state")
        if code is None:
            return Response(
                status=status.HTTP_302_FOUND,
                headers={
                    "Location": f"{settings.FRONT_END_URL}/error"
                }
            )
        try:
            token_manager = TokenManager()
            at, rt = token_manager.get_tokens_from_provider(code)
            email, at = token_manager.authenticate(at, rt)
            try:
                self.serializer.find_by_email(email)
            except User.DoesNotExist:
                self.serializer.create({"email": email})

            if state == "swagger":
                response = Response(
                    status=status.HTTP_302_FOUND,
                    headers={
                        "Location": "/swagger"
                    }
                )
            else:
                response = Response(
                    status=status.HTTP_302_FOUND,
                    headers={
                        "Location": f"{settings.FRONT_END_URL}/my-listings"
                    }
                )

            token_manager.set_credentials_as_cookie(response, at, rt)
            return response
        except Exception as e:
            print(e)
            return Response(
                status=status.HTTP_302_FOUND,
                headers={
                    "Location": f"{settings.FRONT_END_URL}/error"
                }
            )


class LogoutView(APIView):

    @swagger_auto_schema(
        responses={200: openapi.Response(
            description="Logout the user",
            type=openapi.TYPE_STRING,
        )}
    )
    def post(self, request: Request) -> Response:
        """
        Logout the user by invalidating the access token and removing the
        credentials from the cookies.
        :param request: The request object
        :return: The response object
        """
        token_manager = TokenManager()
        access_token, _ = token_manager.get_tokens_from_request(request)
        if access_token is None:
            return Response(status=status.HTTP_200_OK)
        token_manager.invalidate_token(access_token)
        response = Response(status=status.HTTP_200_OK)
        token_manager.remove_credentials_from_cookies(response)
        return response


class RedirectToLoginView(APIView):

    @swagger_auto_schema(
        responses={302: openapi.Response(
            description="Redirect to the login page",
            type=openapi.TYPE_STRING,
        )}
    )
    def get(self, _: Request) -> Response:
        """
        Redirect to the login page. This endpoint is only used for the Swagger
        UI.
        """
        location = (
            f"{settings.OKTA['DOMAIN']}/authorize?response_type=code"
            f"&client_id={settings.OKTA['CLIENT_ID']}&state=swagger"
            f"&scope=openid%20email%20offline_access"
            f"&redirect_uri={settings.OKTA['LOGIN_REDIRECT']}"
        )
        return Response(
            status=status.HTTP_302_FOUND,
            headers={
                "Location": location
            }
        )
