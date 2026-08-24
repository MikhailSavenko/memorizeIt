from word.views import WriteWord, index, search, Dictionary, WordDetail, WordUpdate, WordDelete, word_bulk_delete
from django.urls import path

app_name = "word"

urlpatterns = [
    path("", index, name="home"),
    path("write/", WriteWord.as_view(), name="new_word"),
    path("search/", search, name="search"),
    path("dictionary/", Dictionary.as_view(), name="dictionary"),  
    path("word/bulk_destroy/", word_bulk_delete, name="word_bulk_delete"), # type:ignore
    path("word/<slug:slug>/", WordDetail.as_view(), name="word_detail"),
    path("word/<slug:slug>/edit/", WordUpdate.as_view(), name="word_update"),
    path("word/<slug:slug>/destroy/", WordDelete.as_view(), name="word_delete")
]
