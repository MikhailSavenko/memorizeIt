from django.urls import path
from django.contrib.auth.views import LogoutView

from user.views import RegisterUserView, LoginUserView

app_name = "user"

urlpatterns = [
    path("register/", RegisterUserView.as_view(), name="register_user"),
    path("login/", LoginUserView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout")
]