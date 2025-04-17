from django import forms

from word.models import Word


class RepeatRoomForm(forms.Form):
    answer = forms.CharField(required=True, widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": "Write your answer.."}))
    word_id = forms.IntegerField(widget=forms.HiddenInput())


class ParametersForm(forms.Form):
    from_num = forms.IntegerField(required=False, widget=forms.NumberInput(
        attrs={"class": "form-control", "placeholder": "Enter from which word number to start"}
    ))
    to_num = forms.IntegerField(required=False, widget=forms.NumberInput(
        attrs={"class": "form-control", "placeholder": "Enter the last word number in range"}
    ))
    all_words = forms.BooleanField(required=False, label="All words")

    reverse = forms.BooleanField(required=False, label="Reverse pairs")
    
    def clean(self):
        cleaned_data = super().clean()
        
        from_num = cleaned_data.get("from_num")
        to_num = cleaned_data.get("to_num")
        all_words = cleaned_data.get("all_words")
        
        if from_num is not None and to_num is not None and all_words is True:
            raise forms.ValidationError("All params not allow")
        # Можно добавить дополнительные проверки?
        if from_num is None and to_num is None and not all_words:
            raise forms.ValidationError("Empty all params!")
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
                "placeholder": "Write translation. If their is many use comma: <word>, <word>,.."
            }),
        }