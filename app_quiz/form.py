from django import forms
from .models import Resposta

class RespostaQuizForm(forms.ModelForm):
    """Form para resposta do quiz"""
    class Meta:
        model = Resposta
        fields = ['valor_resposta']
        widgets = {
            'valor_resposta': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg',
                'step': '0.01',
                'placeholder': 'Digite sua resposta'
            })
        }