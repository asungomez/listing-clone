from django.urls import path

from . import views

urlpatterns = [
  path("login/", views.RedirectToLoginView.as_view(), name="login"),
]
