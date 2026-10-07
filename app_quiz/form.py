from django import forms
from .models import Resposta, Quiz

# Create your QUIZ forms here.
# -----------------------------------------------
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

class CadastroQuizForm(forms.ModelForm):
    """Form para cadastro do quiz"""
    class Meta:
        model = Quiz
        fields = ['atividade', 'titulo', 'numero', 'subtitulo', 'pergunta', 'dica', 'unidade_medida', 'valor_minimo', 'valor_maximo', 'valor_ideal', 'icone', 'ativo']
        widgets = {
            'atividade': forms.Select(attrs={'class': 'form-select'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'numero': forms.NumberInput(attrs={'class': 'form-control'}),
            'subtitulo': forms.TextInput(attrs={'class': 'form-control'}),
            'pergunta': forms.Textarea(attrs={'class': 'form-control'}),
            'dica': forms.Textarea(attrs={'class': 'form-control'}),
            'unidade_medida': forms.TextInput(attrs={'class': 'form-control'}),
            'valor_minimo': forms.NumberInput(attrs={'class': 'form-control'}),
            'valor_maximo': forms.NumberInput(attrs={'class': 'form-control'}),
            'valor_ideal': forms.NumberInput(attrs={'class': 'form-control'}),
            'icone': forms.TextInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }