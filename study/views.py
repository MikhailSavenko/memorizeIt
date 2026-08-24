from typing import Any, Optional

from django.http import HttpResponse
from django.views.generic import FormView
from django.shortcuts import redirect

from study.forms import ParametersCreateRoomForm, RepeatRoomForm
from study.services import remove_word_from_session, get_next_practice_word, get_next_practice_word_with_translations, check_word_answer, check_word_translation

from word.models import Word
from word.services import get_all_word_ids, get_available_words_count, get_range_word_ids


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
            return redirect("study:reverse_room")
        return redirect("study:room")


class RepeatRoom(FormView):

    form_class = RepeatRoomForm
    template_name = "word/room.html"

    def render_to_response(self, context: dict[str, Any], **response_kwargs: Any) -> HttpResponse:
        # Работаем с HTMX в форме будет триггер, если будет отправлен POST с формы то HX-Request заголовок будет
        # И мы отдадим не целую страницу, а лишь часть с новым словом
        if self.request.headers.get("HX-Request"):
            self.template_name = "partials/word_card_partial.html"

        return super().render_to_response(context, **response_kwargs)

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
            # В нашем partials/word_card_partial.html будем проверять этот тег, чтобы выкинуть поздравление о завершении
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
        
        # если верно, удалим слово из сессии и вызовем get для вызова get_context_data(достать новое слово) и render_ro_response(перезагрузить часть страницы)
        session = self.request.session
        words_ids = remove_word_from_session(session=session, word_id=word_id)
        
        self.request.session["words_ids"] = words_ids
        # Заменим метод за ГЕТ чтобы не было предыдущего ответа в форме
        self.request.method = "GET"

        # Вызываем get чтобы вызвать render_ro_response
        return self.get(self.request)


class ReverseRepeatRoom(FormView):

    form_class = RepeatRoomForm
    template_name = "word/reverse_room.html"

    def render_to_response(self, context: dict[str, Any], **response_kwargs: Any) -> HttpResponse:
            # Работаем с HTMX в форме будет триггер, если будет отправлен POST с формы то HX-Request заголовок будет
            # И мы отдадим не целую страницу, а лишь часть с новым словом
            if self.request.headers.get("HX-Request"):
                self.template_name = "partials/word_card_partial.html"
    
            return super().render_to_response(context, **response_kwargs)

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
        # Заменим метод за ГЕТ чтобы не было предыдущего ответа в форме
        self.request.method = "GET"
        
        # Вызываем get чтобы вызвать render_ro_response
        return self.get(self.request)
    
