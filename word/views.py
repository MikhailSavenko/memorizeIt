from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, FormView
from word.forms import WriteWordForm, ParametersForm, RepeatRoomForm
from word.models import Word
from django.urls import reverse_lazy
from django.db.models import Q


def put_words_in_cookies(request, words_list):
    if not words_list:
        raise ValueError("No words.")
    request.session["words_ids"] = [w.id for w in words_list]


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
        print(cleaned_data)
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
        
        words_ids = self.request.session.get("words_ids")
        words_list = list(self.pull_out_words(words_ids=words_ids))
        # Получаем слово
        word = words_list[-1]
        context["word"] = word.word
        # Передаем word_id чтобы потом автоматически вставить в форму 
        context["word_id"] = word.id
        return context

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        
        answer = cleaned_data.get("answer")
        word_id = cleaned_data.get("word_id")
        word = get_object_or_404(Word, id=word_id)
        # если неверное выведем error но не обновим страницу
        translations_list = [t.strip().lower() for t in word.translation.split(",")]
        answer = answer.strip().lower()
        if answer not in translations_list and answer != word.translation:
            form.add_error("answer", "Incorrect translation!")
            return self.form_invalid(form)
        # если верно, удалим слово из сессии и перейдем снова на room
        words_ids = self.request.session.get("words_ids", [])
        
        if word_id in words_ids:
            words_ids.remove(word_id)
        self.request.session["words_ids"] = words_ids
        if not words_ids:
            return redirect("create_room") 
        return redirect("room")

    def pull_out_words(self, words_ids: list):
        if not words_ids:
            raise ValueError("No words!")
        words_list = Word.objects.filter(id__in=words_ids)
        return words_list