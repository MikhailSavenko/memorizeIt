from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

User = get_user_model()


class RegisterUserForm(UserCreationForm):
    """Форма регистрации пользователя"""

    class Meta:
        model = User
        fields = ("username", "email")
    

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "form-control", 
                "placeholder": field.label
            })


class AuthenticationUserForm(AuthenticationForm):
    """Форма для входа в аккаунт пользователя"""
    

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.fields["username"].label = "Email or Username"
        self.fields["username"].widget.attrs.update({
                "class": "form-control", 
                "placeholder": "Enter your email or username"
            })

        self.fields["password"].widget.attrs.update({
                "class": "form-control", 
                "placeholder": "Enter your password"
            })