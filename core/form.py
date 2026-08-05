from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Resposta, Evento, Atividade


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
            'imagemBanner': 'Imagem do Banner',
            'dataInicio': 'Data de Início',
            'dataFim': 'Data de Término',
            'tipoEvento': 'Tipo do Evento',
            'eventoMultiplo': 'Evento Múltiplo?',
            'eventoPublico': 'Evento Público?',
        }
        
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'digite o nome do evento', 'class': 'form-control mb-3'}),
            'descricao': forms.Textarea(attrs={'placeholder': 'digite a descrição do evento', 'class': 'form-control mb-3', 'rows': 4}),
            'emailContato': forms.EmailInput(attrs={'placeholder': 'digite o e-mail de contato', 'class': 'form-control mb-3'}),
            'apoiadores': forms.TextInput(attrs={'placeholder': 'digite os apoiadores', 'class': 'form-control mb-3'}),
            'local': forms.TextInput(attrs={'placeholder': 'digite o local do evento', 'class': 'form-control mb-3'}),
            'imagemBanner': forms.FileInput(attrs={'class': 'form-control mb-3','accept': 'image/*'}),
            'dataInicio': forms.DateInput(attrs={'class': 'form-control mb-3', 'type': 'date'}),
            'dataFim': forms.DateInput(attrs={'class': 'form-control mb-3', 'type': 'date'}),
            'tipoEvento': forms.Select(attrs={'class': 'form-select mb-3'}),
            'eventoMultiplo': forms.CheckboxInput(attrs={'class': 'form-check-input mb-3'}),
            'eventoPublico': forms.CheckboxInput(attrs={'class': 'form-check-input mb-3'}),
        }

class AtividadeForm(forms.ModelForm):
    class Meta:
        model = Atividade
        fields = [
            'nome',
            'descricao',
            'tipoAtividade',
            'complementoLocal',
            'horaInicio',
            'horaFim',
            'limitePessoas',
        ]

        labels = {
            'nome': 'Nome da Atividade',
            'descricao': 'Descrição',
            'tipoAtividade' : 'Tipo de atividade',
            'complementoLocal': 'Complemento do Local',
            'horaInicio': 'Hora de Início',
            'horaFim': 'Hora de Término',
            'limitePessoas': 'Limite de Participantes',

        }
        
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder':'digite o nome da atividade','class': 'form-control mb-3'}),
            'descricao': forms.Textarea(attrs={'placeholder':'digite a descrição da atividade','class': 'form-control mb-3', 'rows': 4}),
            'tipoAtividade': forms.Select(attrs={'class': 'form-select mb-3'}),
            'complementoLocal': forms.TextInput(attrs={'placeholder':'digite o complemento do local','class': 'form-control mb-3'}),
            'horaInicio': forms.DateTimeInput(attrs={'class': 'form-control mb-3', 'type': 'datetime-local'}),
            'horaFim': forms.DateTimeInput(attrs={'class': 'form-control mb-3', 'type': 'datetime-local'}),
            'limitePessoas': forms.NumberInput(attrs={'placeholder':'digite o limite de participantes','class': 'form-control mb-3', 'type': 'number'}),
            
        }
