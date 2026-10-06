from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="E-mail")

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password1",
            "password2",
        )


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = (
            "phone",
            "telegram",
            "city",
        )

        labels = {
            "phone": "Телефон",
            "telegram": "Telegram",
            "city": "Город",
        }
