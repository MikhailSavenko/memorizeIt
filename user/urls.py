from django.urls import path
from user.views import RegisterUserView, LoginUserView

app_name = "user"

urlpatterns = [
    path("register/", RegisterUserView.as_view(), name="register_user"),
    path("login/", LoginUserView.as_view(), name="login")
]