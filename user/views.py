from django.contrib.auth import get_user_model
from django.views.generic import CreateView
from user.forms import RegisterUserForm

User = get_user_model()

class RegisterUserView(CreateView):
    
    form_class = RegisterUserForm
    template_name = "register_user.html"

