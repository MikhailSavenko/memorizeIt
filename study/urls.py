from django.urls import path
from study.views import CreateRoom, RepeatRoom, ReverseRepeatRoom

app_name = "study"

urlpatterns = [
    path("create_room/", CreateRoom.as_view(), name="create_room"),
    path("room/", RepeatRoom.as_view(), name="room"),
    path("reverse_room/", ReverseRepeatRoom.as_view(), name="reverse_room"),
]
