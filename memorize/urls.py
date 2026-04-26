from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("word.urls", namespace="word")),
    path("user/", include("user.urls", namespace="user"))
]
