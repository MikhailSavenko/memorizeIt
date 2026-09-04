from word.views import WriteWord, search, Dictionary, WordDetail, WordUpdate, WordDelete, word_bulk_delete, check_word_duplicates
from django.urls import path

app_name = "word"

urlpatterns = [
    path("write/", WriteWord.as_view(), name="new_word"),
    path("check_duplicates/", check_word_duplicates, name="check_duplicates"),
    path("search/", search, name="search"),
    path("dictionary/", Dictionary.as_view(), name="dictionary"),  
    path("bulk_destroy/", word_bulk_delete, name="word_bulk_delete"),
    path("<slug:slug>/", WordDetail.as_view(), name="word_detail"),
    path("<slug:slug>/edit/", WordUpdate.as_view(), name="word_update"),
    path("<slug:slug>/destroy/", WordDelete.as_view(), name="word_delete")
]
