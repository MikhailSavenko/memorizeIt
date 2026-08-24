from django import forms


class RepeatRoomForm(forms.Form):
    answer = forms.CharField(required=True, widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": "Write your answer..", "autofocus": True, "autocomplete": "off"}))
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