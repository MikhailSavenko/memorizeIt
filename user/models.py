from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    
    email = models.EmailField(unique=True, blank=False)

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = ["username"]

