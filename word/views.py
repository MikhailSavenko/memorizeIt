from typing import Any, Optional

from django.db.models.query import QuerySet
from django.shortcuts import render, redirect
from django.views.generic import CreateView, FormView, ListView
from django.urls import reverse_lazy
from django.db import transaction

from word.forms import WriteWordForm, ParametersCreateRoomForm, RepeatRoomForm, TranslationInlineFormSet, SearchAliveForm
from word.models import Word
from word.services import check_word_answer, get_all_word_ids, get_available_words_count, check_word_translation, get_next_practice_word_with_translations, get_range_word_ids, remove_word_from_session, get_next_practice_word


def search(request):
    words = []

    context = dict()
    context["query"] = SearchAliveForm(request.GET.get("search") or None)
    
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
    
    form_class = ParametersCreateRoomForm
    template_name = "word/create_room.html"
    
    def get_context_data(self, **kwargs) -> dict:
        """Получает контекст и добавляет поле с количеством слов"""
        context = super().get_context_data(**kwargs)
        context["words_count"] = get_available_words_count()
        return context

    def form_valid(self, form):
        """Создаем набор слов для повторения исходя из заданных в форме параметров"""
        cleaned_data = form.cleaned_data
        first_num = cleaned_data.get("first_num")
        second_num = cleaned_data.get("second_num")
        reverse = cleaned_data.get("reverse")
        

        all_word_ids = get_all_word_ids()

        if first_num is not None and second_num is not None:
            all_word_ids = get_range_word_ids(all_word_ids=all_word_ids, first_num=first_num, second_num=second_num)

        self.request.session["words_ids"] = all_word_ids

        if reverse:
            return redirect("word:reverse_room")
        return redirect("word:room")


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
