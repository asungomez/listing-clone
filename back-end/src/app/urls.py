from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
   openapi.Info(
      title="My Listings API",
      default_version='v1',
      description="My Listings API",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path(
        'swagger/',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'
        ),
    path("admin/", admin.site.urls),
    path("users/", include("user.urls")),
    path("accounts/", include("user.account_urls"))
]
