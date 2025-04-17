from word.views import WrideWord, CreateRoom, RepeatRoom
from django.urls import path

urlpatterns = [
    path("write/", WrideWord.as_view(), name="new_word"),
    path("create_room/", CreateRoom.as_view(), name="create_room"),
    path("room/", RepeatRoom.as_view(), name="room")
]
