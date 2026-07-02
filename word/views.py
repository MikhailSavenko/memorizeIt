from typing import Any, Optional

from django.db.models.query import QuerySet
from django.shortcuts import render, redirect
from django.views.generic import CreateView, FormView, ListView
from django.urls import reverse_lazy
from django.db.models import Q
from django.db import transaction

from word.forms import WriteWordForm, ParametersForm, RepeatRoomForm, TranslationInlineFormSet
from word.models import Word
from word.services import check_word_answer, check_word_translation, get_next_practice_word_with_translations, remove_word_from_session, get_next_practice_word


def set_word_ids_in_session(request, words_ids_list):
    """Кладет ids Word в сессию"""
    if not words_ids_list:
        raise ValueError("No words.")
    request.session["words_ids"] = words_ids_list


def search(request):
    words = []
    query = ""
    if request.method == "GET":
        query = request.GET.get("search")
        if not isinstance(query, str):
            raise ValueError("Only string")
        words = Word.objects.filter(Q(word__icontains=query)|Q(translation__text__icontains=query))
    return render(request, "word/search_alive.html", context={"words": words, "query": query})
    

def index(request):
    return render(request, "word/index.html")


class WriteWord(CreateView):

    form_class = WriteWordForm
    template_name = "word/write_word.html"
    success_url = reverse_lazy("word:new_word")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context["translation_formset"] = TranslationInlineFormSet(
            self.request.POST or None
        )

        return context
    
    def form_valid(self, form):
        formset = TranslationInlineFormSet(self.request.POST)

        if not formset.is_valid():
            return self.form_invalid(form)
        
        with transaction.atomic():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
        
        return redirect(self.get_success_url())
    

class CreateRoom(FormView):
    
    form_class = ParametersForm
    template_name = "word/create_room.html"
    
    def get_context_data(self, **kwargs) -> dict:
        """Получает контекст и добавляет поле с количеством слов"""
        context = super().get_context_data(**kwargs)
        words_count = Word.objects.count()                   # можно в дальнейшем вынести в контекстный процессор или Simple Tag
        context["words_count"] = words_count
        return context

    def form_valid(self, form):
        """Создаем набор слов для повторения исходя из заданных в форме параметров"""
        cleaned_data = form.cleaned_data
        from_num = cleaned_data.get("from_num")
        to_num = cleaned_data.get("to_num")
        all_words = cleaned_data.get("all_words")
        reverse = cleaned_data.get("reverse")

        words_ids_list_for_repeat = []

        if all_words:
            words_ids_list_for_repeat = list(Word.objects.all().values_list("id", flat=True))
        elif from_num and to_num:
            words_ids_list_for_repeat = list(Word.objects.filter(id__gte=from_num, id__lte=to_num).values_list("id", flat=True))

        set_word_ids_in_session(request=self.request, words_ids_list=words_ids_list_for_repeat)

        if reverse:
            return redirect("word:reverse_room")
        return redirect("word:room")

# Два класса Repeat и Reverse можно дальше создать базовый и два наследника
class RepeatRoom(FormView):

    form_class = RepeatRoomForm
    template_name = "word/room.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        words_ids = self.request.session.get("words_ids", [])
        # Получаем слово
        word: Optional[Word] = get_next_practice_word(words_ids=words_ids)

        if word:
            context["word"] = word.word
            context["part_of_speech"] = word.part_of_speech
            # Передаем word_id чтобы потом автоматически вставить в форму 
            context["word_id"] = word.pk 
        else:
            context["no_word_left"] = True
            
        return context

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        
        answer = cleaned_data.get("answer")
        word_id = cleaned_data.get("word_id")

        # если неверное выведем error но не обновим страницу
        translation_check = check_word_translation(user_answer=answer, word_id=word_id)
        
        if not translation_check:
            form.add_error("answer", "Incorrect translation!")

            data = form.data.copy()
            data["answer"] = ""
            form.data = data

            return self.form_invalid(form)
        
        # если верно, удалим слово из сессии и перейдем снова на room
        session = self.request.session
        words_ids = remove_word_from_session(session=session, word_id=word_id)
        
        self.request.session["words_ids"] = words_ids

        if not words_ids:
            return redirect("word:create_room") 
        
        return redirect("word:room")


class ReverseRepeatRoom(FormView):

    form_class = RepeatRoomForm
    template_name = "word/reverse_room.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        words_ids = self.request.session.get("words_ids", [])
        # Получаем слово
        word: Optional[Word] = get_next_practice_word_with_translations(words_ids=words_ids)

        if word:
            context["word"] = word.translations_string 
            context["part_of_speech"] = word.part_of_speech
            # Передаем word_id чтобы потом автоматически вставить в форму 
            context["word_id"] = word.pk
        else:
            context["no_word_left"] = True

        return context

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        
        answer = cleaned_data.get("answer")
        word_id = cleaned_data.get("word_id")

        # если неверное выведем error но не обновим страницу
        check_word = check_word_answer(user_answer=answer, word_id=word_id)

        if not check_word:
            form.add_error("answer", "Incorrect translation!")

            data = form.data.copy()
            data["answer"] = ""
            form.data = data

            return self.form_invalid(form)
        
        # если верно, удалим слово из сессии и перейдем снова на room
        session = self.request.session
        words_ids = remove_word_from_session(session=session, word_id=word_id)
        
        self.request.session["words_ids"] = words_ids

        if not words_ids:
            return redirect("word:create_room") 
        
        return redirect("word:reverse_room")
    

class Dictionary(ListView):

    model = Word
    template_name = "word/dictionary.html"
    context_object_name = "words"
    
    paginate_by = 29

    def get_queryset(self) -> QuerySet[Word]:
        return Word.objects.prefetch_related("translation_set").all()
