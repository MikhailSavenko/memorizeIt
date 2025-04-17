from django import forms

from word.models import Word


class RepeatRoomForm(forms.Form):
    answer = forms.CharField(required=True, label="Перевод слова")
    word_id = forms.IntegerField(widget=forms.HiddenInput())


class ParametersForm(forms.Form):
    from_num = forms.IntegerField(required=False, label="Write the init number in range")
    to_num = forms.IntegerField(required=False, label="Write the finish number in range")
    all_words = forms.BooleanField(required=False, label="OR pick all words =)")
    
    def clean(self):
        cleaned_data = super().clean()
        
        from_num = cleaned_data.get("from_num")
        to_num = cleaned_data.get("to_num")
        all_words = cleaned_data.get("all_words")

        if (from_num is not None and to_num is not None) and all_words is not None:
            raise forms.ValidationError("Введите диапазон слов либо выберите все слова! Что-то одно.")
        # Можно добавить дополнительные проверки?

        return cleaned_data
    

class WriteWordForm(forms.ModelForm):

    class Meta:
        model = Word
        fields = ["word", "part_of_speech", "transcription", "translation"]
    
        widgets = {
            "part_of_speech": forms.Select(attrs={
                "class": "form-control"
            }),
            "word": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Write English word"
            }),
            "transcription": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Write transcription"
            }),
            "translation": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Write translation"
            }),
        }