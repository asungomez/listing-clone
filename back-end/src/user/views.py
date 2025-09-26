from core.auth import TokenManager
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views import View
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
                    "Location": f"{settings.FRONT_END_URL}/profiles"
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


class CurrentUserView(View):
    serializer = UserSerializer()

    def get(self, request: HttpRequest) -> HttpResponse:
        try:
            if not request.user.is_authenticated:
                return JsonResponse({"error": "Not authenticated"}, status=401)
            email = request.user.email
            user = self.serializer.find_by_email(email)
            return JsonResponse({"user": self.serializer(user).data})
        except Exception as e:
            json_error = {"error": str(e)}
            return JsonResponse(json_error, status=401)
