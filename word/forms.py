from django import forms

from word.models import Word, Translation
from word.clients import transcription_by_wordsapi

class RepeatRoomForm(forms.Form):
    answer = forms.CharField(required=True, widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": "Write your answer.."}))
    word_id = forms.IntegerField(widget=forms.HiddenInput())


class ParametersCreateRoomForm(forms.Form):
    first_num = forms.IntegerField(required=False, widget=forms.NumberInput(
        attrs={"class": "form-control", "placeholder": "Enter from which word number to start"}
    ))
    second_num = forms.IntegerField(required=False, widget=forms.NumberInput(
        attrs={"class": "form-control", "placeholder": "Enter the last word number in range"}
    ))
    all_words = forms.BooleanField(required=False, label="All words")

    reverse = forms.BooleanField(required=False, label="Reverse pairs")
    
    def clean(self):
        cleaned_data = super().clean()
        
        first_num = cleaned_data.get("first_num")
        second_num = cleaned_data.get("second_num")
        all_words = cleaned_data.get("all_words")
        
        if all_words and any((second_num, first_num)):
            raise forms.ValidationError("Cannot combine 'All words' with a specific range. Please choose one.")
            
        if not all_words:
            if first_num is None or second_num is None:
                raise forms.ValidationError("You must specify both fields for the range or enter 'All words'.")
            
        return cleaned_data
    

TranslationInlineFormSet = forms.inlineformset_factory(
    parent_model=Word,
    model=Translation,
    fields=("text",),
    extra=1,
    can_delete=False,
    widgets={
        "translation": forms.Select(attrs={
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
                "placeholder": "Write word"
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