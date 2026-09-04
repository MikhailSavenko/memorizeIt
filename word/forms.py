from django import forms
from django.urls import reverse_lazy

from word.models import Word, Translation
from word.clients import transcription_by_wordsapi
    

class TranslationsFormSetErrorMessage(forms.BaseInlineFormSet):
    default_error_messages = {
        "too_few_forms": "The word must have at least one translation!",
    }


TranslationInlineFormSet = forms.inlineformset_factory(
    parent_model=Word,
    model=Translation,
    fields=("text",),
    extra=0,
    can_delete=True,
    min_num=1,
    validate_min=True,
    formset=TranslationsFormSetErrorMessage,
    widgets={
        "text": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Write translation"
            })
    }
)
    

class WriteWordForm(forms.ModelForm):

    class Meta:
        model = Word
        fields = ["word", "part_of_speech", "transcription"]
    
        widgets = {
            "part_of_speech": forms.Select(attrs={
                "class": "form-control"
            }),
            "word": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Write word",
                "hx-get": reverse_lazy("word:search"),
                "hx-trigger": "keyup changed delay:1000ms",
                "hx-target": "#word-alert-container",
                "hx-vals": "js:{text: event.target.value}"
            }),
            "transcription": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Transcription is not required. You can keep this empty"
            })
        }
    
    def clean(self):
        data = super().clean()
        transcription = data.get("transcription")
        word = data.get("word")
        # Пока разработка нет смысла делать запросы к апи попусту #РАССКОММЕНТИРОВАТЬ
        # if not transcription:

        #     get_transcription = transcription_by_wordsapi(word=word)

        #     if get_transcription:
        #         data["transcription"] = get_transcription
                
        return data


class SearchAliveForm(forms.Form):
    text = forms.CharField(max_length=50, required=True)


class SearchDictForm(forms.Form):
    search_dict = forms.CharField(max_length=50, 
                           required=False,
                           widget=forms.TextInput(
                               attrs={
                                   "placeholder": "Search by №, word and translation",
                                   "class": "form-control"
                               }
                           )
                           )