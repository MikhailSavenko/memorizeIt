from word.views import WriteWord, CreateRoom, RepeatRoom, index, search, ReverseRepeatRoom, Dictionary, WordDetail, WordUpdate, WordDelete
from django.urls import path

app_name = "word"

urlpatterns = [
    path("", index, name="home"),
    path("write/", WriteWord.as_view(), name="new_word"),
    path("create_room/", CreateRoom.as_view(), name="create_room"),
    path("room/", RepeatRoom.as_view(), name="room"),
    path("reverse_room/", ReverseRepeatRoom.as_view(), name="reverse_room"),
    path("search/", search, name="search"),
    path("dictionary/", Dictionary.as_view(), name="dictionary"),
    path("word/<slug:slug>/", WordDetail.as_view(), name="word_detail"),
    path("word/<slug:slug>/edit/", WordUpdate.as_view(), name="word_update"),
    path("word/<slug:slug>/destroy/", WordDelete.as_view(), name="word_delete")
]
