from core.auth import AuthenticatedAPIView, AuthenticatedRequest, TokenManager
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserSerializer

User = get_user_model()


class LoginView(APIView):

    serializer = UserSerializer()

    def get(self, request: Request) -> Response:
        code = request.query_params.get("code")
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


class CurrentUserView(AuthenticatedAPIView):

    def get(self, request: AuthenticatedRequest) -> Response:
        return Response({"user": UserSerializer(request.user).data})
