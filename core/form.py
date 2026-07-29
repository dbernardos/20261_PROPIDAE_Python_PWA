from django import forms
from django.forms import fields
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Resposta, Evento


class UsuarioForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',   
            }),

            'email': forms.TextInput(attrs={
                'class': 'form-control',   
            }),
        }

class ParticipanteForm(forms.ModelForm):
    """Form para registro/login do participante pelo crachá"""
    class Meta:
        model = Usuario
        fields = ['nome', 'email']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo (opcional)'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'E-mail (opcional)'
            })
        }

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

class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = [
            'nome',
            'descricao',
            'emailContato',
            'apoiadores',
            'local',
            'complementoLocal',
            'imagemBanner',
            'dataInicio',
            'dataFim',
            'tipoEvento',
            'eventoMultiplo',
            'eventoPublico'
        ]

        labels = {
            'nome': 'Nome do Evento',
            'descricao': 'Descrição',
            'emailContato': 'E-mail de Contato',
            'apoiadores': 'Apoiadores / Patrocinadores',
            'local': 'Local do Evento',
            'complementoLocal': 'Complemento do Local',
            'imagemBanner': 'Imagem do Banner',
            'dataInicio': 'Data de Início',
            'dataFim': 'Data de Término',
            'tipoEvento': 'Tipo do Evento',
            'eventoMultiplo': 'Evento Múltiplo?',
            'eventoPublico': 'Evento Público?',
        }

        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control mb-3'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control mb-3', 'rows': 4}),
            'emailContato': forms.EmailInput(attrs={'class': 'form-control mb-3'}),
            'apoiadores': forms.TextInput(attrs={'class': 'form-control mb-3'}),
            'local': forms.TextInput(attrs={'class': 'form-control mb-3'}),
            'complementoLocal': forms.TextInput(attrs={'class': 'form-control mb-3'}),
            'imagemBanner': forms.FileInput(attrs={'class': 'form-control mb-3'}),
            'dataInicio': forms.DateInput(attrs={'class': 'form-control mb-3', 'type': 'date'}),
            'dataFim': forms.DateInput(attrs={'class': 'form-control mb-3', 'type': 'date'}),
            'tipoEvento': forms.Select(attrs={'class': 'form-select mb-3'}),
            'eventoMultiplo': forms.CheckboxInput(attrs={'class': 'form-check-input mb-3'}),
            'eventoPublico': forms.CheckboxInput(attrs={'class': 'form-check-input mb-3'}),
        }