from django.urls import path

from . import views

urlpatterns = [
  path("", views.ListingViewSet.as_view({
    "post": "create",
  }), name="listings"),
  path("my-listings", views.MyListingsView.as_view(), name="my-listings"),
]
