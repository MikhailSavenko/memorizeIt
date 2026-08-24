from django.contrib import admin
from django.urls import path, include

from memorize.views import index

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", index, name="home"),
    path("", include("word.urls", namespace="word")),
    path("user/", include("user.urls", namespace="user")),
    path("study/", include("study.urls", namespace="study"))
]
