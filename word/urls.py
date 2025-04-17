from word.views import WrideWord, CreateRoom, RepeatRoom, index, search, ReverseRepeatRoom
from django.urls import path

urlpatterns = [
    path("", index, name="home"),
    path("write/", WrideWord.as_view(), name="new_word"),
    path("create_room/", CreateRoom.as_view(), name="create_room"),
    path("room/", RepeatRoom.as_view(), name="room"),
    path("reverse_room/", ReverseRepeatRoom.as_view(), name="reverse_room"),
    path("search/", search, name="search")
]
