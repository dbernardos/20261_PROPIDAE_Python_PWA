from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class UsuarioForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email']

        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',   
            }),

            'email': forms.EmailInput(attrs={
                'class': 'form-control',   
            }),
        }