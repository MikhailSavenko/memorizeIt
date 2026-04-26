from django.contrib.auth import get_user_model
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.shortcuts import redirect

from user.forms import RegisterUserForm


User = get_user_model()

class RegisterUserView(CreateView):
    
    form_class = RegisterUserForm
    template_name = "user/register.html"
    success_url = reverse_lazy("word:new_word")


    def form_valid(self, form):
        user = form.save()
        self.object = user
        login(self.request, user)
        success_url = str(self.get_success_url())
        return redirect(success_url)
    
