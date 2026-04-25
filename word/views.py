from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, FormView, ListView
from word.forms import WriteWordForm, ParametersForm, RepeatRoomForm
from word.models import Word
from django.urls import reverse_lazy
from django.db.models import Q


def pull_out_words(words_ids: list):
    """Получаем QuerySet объектов Word по списку их ID"""
    if not words_ids:
        return Word.objects.none()
    words_list = Word.objects.filter(id__in=words_ids)
    return words_list


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
        words = Word.objects.filter(Q(word__icontains=query)|Q(translation__icontains=query))
    return render(request, "word/search_alive.html", context={"words": words, "query": query})
    

def index(request):
    return render(request, "word/index.html")


class WriteWord(CreateView):

    form_class = WriteWordForm
    template_name = "word/write_word.html"
    success_url = reverse_lazy("new_word")


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
            return redirect("reverse_room")
        return redirect("room")

# Два класса Repeat и Reverse можно дальше создать базовый и два наследника
class RepeatRoom(FormView):

    form_class = RepeatRoomForm
    template_name = "word/room.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        words_ids = self.request.session.get("words_ids", [])
        words_list = list(pull_out_words(words_ids=words_ids))
        # Получаем слово
        word = words_list[-1]
        context["word"] = word.word
        context["part_of_speech"] = word.part_of_speech
        # Передаем word_id чтобы потом автоматически вставить в форму 
        context["word_id"] = word.pk
        return context

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        
        answer = cleaned_data.get("answer")
        word_id = cleaned_data.get("word_id")
        word = get_object_or_404(Word, id=word_id)
        
        # если неверное выведем error но не обновим страницу
        translations_list = [t.strip().lower() for t in word.translation.split(",")]
        answer = answer.strip().lower()
        
        if answer not in translations_list:
            form.add_error("answer", "Incorrect translation!")

            data = form.data.copy()
            data["answer"] = ""
            form.data = data

            return self.form_invalid(form)
        
        # если верно, удалим слово из сессии и перейдем снова на room
        words_ids = self.request.session.get("words_ids", [])
        
        if word_id in words_ids:
            words_ids.remove(word_id)
        self.request.session["words_ids"] = words_ids
        
        if not words_ids:
            return redirect("create_room") 
        return redirect("room")


class ReverseRepeatRoom(FormView):

    form_class = RepeatRoomForm
    template_name = "word/reverse_room.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        words_ids = self.request.session.get("words_ids", [])
        words_list = list(pull_out_words(words_ids=words_ids))
        # Получаем слово
        word = words_list[-1]
        context["word"] = word.translation
        context["part_of_speech"] = word.part_of_speech
        # Передаем word_id чтобы потом автоматически вставить в форму 
        context["word_id"] = word.pk
        return context

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        
        answer = cleaned_data.get("answer")
        word_id = cleaned_data.get("word_id")
        word = get_object_or_404(Word, id=word_id)

        # если неверное выведем error но не обновим страницу
        words_list = [t.strip().lower() for t in word.word.split(",")]
        answer = answer.strip().lower()

        if answer not in words_list:
            form.add_error("answer", "Incorrect translation!")

            data = form.data.copy()
            data["answer"] = ""
            form.data = data

            return self.form_invalid(form)
        
        # если верно, удалим слово из сессии и перейдем снова на room
        words_ids = self.request.session.get("words_ids", [])
        
        if word_id in words_ids:
            words_ids.remove(word_id)
        self.request.session["words_ids"] = words_ids

        if not words_ids:
            return redirect("create_room") 
        return redirect("reverse_room")
    

class Dictionary(ListView):

    model = Word
    template_name = "word/dictionary.html"
    context_object_name = "words"

    def get_context_data(self, **kwargs):
        """Получает контекст достает из поля введенный параметр поиска, ищет слово и добаляет его pk в контекст для JS"""
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("search_dict")
        if query:
            word = Word.objects.filter(
                Q(id__icontains=query) |
                Q(word__icontains=query) |
                Q(translation__icontains=query)
            ).first()
            if word:
                context["highlight_id"] = word.pk
        return context