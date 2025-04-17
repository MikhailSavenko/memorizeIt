from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, FormView
from word.forms import WriteWordForm, ParametersForm, RepeatRoomForm
from word.models import Word
from django.urls import reverse_lazy


def put_words_in_cookies(request, words_list):
    if not words_list:
        raise ValueError("Нет слов.")
    request.session["words_ids"] = [w.id for w in words_list]


class WrideWord(CreateView):

    form_class = WriteWordForm
    template_name = "word/write_word.html"
    success_url = reverse_lazy("new_word")


class CreateRoom(FormView):
    
    form_class = ParametersForm
    template_name = "word/create_room.html"
    
    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        words_count = Word.objects.count()
        context["words_count"] = words_count
        return context

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        
        from_num = cleaned_data.get("from_num")
        to_num = cleaned_data.get("to_num")
        all_words = cleaned_data.get("all_words")

        if all_words:
            words_list_for_repeat = Word.objects.all()
        elif from_num and to_num:
            words_list_for_repeat = Word.objects.filter(id__gte=from_num, id__lte=to_num)

        put_words_in_cookies(request=self.request, words_list=words_list_for_repeat)
        
        return redirect("room")


class RepeatRoom(FormView):

    form_class = RepeatRoomForm
    template_name = "word/room.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print("hello")
        words_ids = self.request.session.get("words_ids")
        words_list = list(self.pull_out_words(words_ids=words_ids))
        # Получаем слово
        word = words_list[-1]
        context["word"] = word.word
        # Передаем wordid чтобы потом автоматически вставить в форму 
        context["word_id"] = word.id
        
        # # Обновляем куки на клиенте, убираем этот id
        # put_words_in_cookies(words_list=words_list)
        return context

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        
        answer = cleaned_data.get("answer")
        word_id = cleaned_data.get("word_id")
        word = get_object_or_404(Word, id=word_id)
        # если неверное выведем error но не обновим страницу
        print(answer)
        print(word.translation)
        if answer != word.translation:
            print("hi")
            form.add_error("answer", "Incorrect translation!")
            return self.form_invalid(form)
        # если верно, удалим слово из сессии и перейдем снова на room
        words_ids = self.request.session.get("words_ids", [])
        
        if word_id in words_ids:
            words_ids.remove(word_id)
        self.request.session["words_ids"] = words_ids
        
        return redirect("room")

    def pull_out_words(self, words_ids: list):
        if not words_ids:
            raise ValueError("Нет слов")
        words_list = Word.objects.filter(id__in=words_ids)
        return words_list