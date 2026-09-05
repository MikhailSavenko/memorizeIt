from typing import Any

from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.http.response import HttpResponse as HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db import transaction
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_POST

from word.forms import WriteWordForm, TranslationInlineFormSet, SearchAliveForm, SearchDictForm
from word.models import Word
from word.services import bulk_delete_words_by_ids, calculate_target_page_and_id, get_searched_word, parse_and_validate_word_ids_json


def search(request):
    form = SearchAliveForm(request.GET or None)
    search_text = ""
    words = []

    if form.is_valid():

        search_text = form.cleaned_data["text"]
        words = get_searched_word(text=search_text)
    
    context = {
        "query": search_text,
        "words": words
    }

    return render(request, "partials/search_alive.html", context=context)
    

def check_word_duplicates(request):
    form = SearchAliveForm(request.GET or None)
    search_text = ""
    words = []

    if form.is_valid():

        search_text = form.cleaned_data["text"]
        words = get_searched_word(text=search_text)
    
    context = {
        "query": search_text,
        "words": words
    }

    return render(request, "partials/word_duplicates_alert.html", context=context)


#Авторизация login_required
@require_POST
def word_bulk_delete(request):
    raw_data = request.POST.get("delete_ids", "[]")
    
    try:
        parsed_data = parse_and_validate_word_ids_json(raw_data)
        bulk_delete_words_by_ids(parsed_data)
    except ValidationError as e:
        return JsonResponse({"error": e.message}, status=400)
    
    return JsonResponse({"status": "success"}, status=200)


class WriteWord(CreateView):

    form_class = WriteWordForm
    template_name = "word/write_word.html"
    success_url = reverse_lazy("word:new_word")

    @property
    def translation_formset(self):
        if not hasattr(self, "_cached_formset"):
            self._cached_formset = TranslationInlineFormSet(
                self.request.POST or None
            )
        return self._cached_formset

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        # тут мы при какой-либо ошибке вернем значения введенные в переводы или пустой формсет
        context["translation_formset"] = self.translation_formset 

        return context
    
    def form_valid(self, form):
        formset = self.translation_formset

        if not formset.is_valid(): # валидация самой формы form.is_valid делается на уровне CreateView сама под капотом
            return self.form_invalid(form) # тут мы при невалидном формсете вернем значения самой формы
        
        with transaction.atomic():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
        
        return redirect(self.get_success_url())
    

class Dictionary(ListView):

    model = Word
    template_name = "word/dictionary.html"
    
    paginate_by = 29

    highlight_id = None

    def get_queryset(self) -> QuerySet[Word]:
        return Word.objects.prefetch_related("translation_set").all()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        if self.highlight_id:
            context["highlight_id"] = self.highlight_id

        return context

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        form = SearchDictForm(request.GET)

        if form.is_valid():
            search_query = form.cleaned_data.get("search_dict")

            if search_query:

                word_id, target_page = calculate_target_page_and_id(search_query=search_query, paginate_by=self.paginate_by)

                if word_id and target_page:
                    request.GET = request.GET.copy()
                    request.GET["page"] = str(target_page)

                    self.highlight_id = word_id

        return super().get(request, *args, **kwargs)


class WordDetail(DetailView):

    model = Word
    template_name = "word/word_detail.html"

    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self) -> QuerySet[Any, Any]:
        return super().get_queryset().prefetch_related("translation_set")


class WordUpdate(UpdateView):
    model = Word
    form_class = WriteWordForm
    template_name = "word/write_word.html"

    slug_field = "slug"
    slug_url_kwarg = "slug"

    object: Word

    def get_success_url(self) -> str:
        return reverse_lazy("word:word_detail", kwargs={"slug": self.object.slug})

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context["translation_formset"] = TranslationInlineFormSet(
            self.request.POST or None,
            instance=self.object
        )

        return context

    def form_valid(self, form):
        formset = TranslationInlineFormSet(self.request.POST, instance=self.object)
    
        if not formset.is_valid():
            return self.render_to_response(self.get_context_data(form=form, translation_formset=formset))

        with transaction.atomic():
            self.object = form.save()
            formset.instance = self.object
            formset.save()

        return redirect(self.get_success_url())


class WordDelete(DeleteView):
    model = Word
    slug_field = "slug"
    slug_url_kwarg = "slug"

    success_url = reverse_lazy("word:dictionary")

