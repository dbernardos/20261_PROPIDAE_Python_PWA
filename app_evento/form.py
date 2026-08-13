from django import forms
from .models import Evento, Atividade, Apoiador

# Create your EVENTO forms here.
# -----------------------------------------------
class EventoForm(forms.ModelForm):

    #campo de apoiadores como CharField para entrada de texto, que será processado posteriormente
    apoiadores = forms.CharField(
        required=False,
        label='Apoiadores / Patrocinadores (separe por vírgulas)',
        widget=forms.TextInput(attrs={
            'placeholder': 'Ex: Google, Microsoft, Ambev', 
            'class': 'form-control mb-3'
        })
    )
    
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
            #'apoiadores': forms.TextInput(attrs={'placeholder': 'Ex: Google, Microsoft, Ambev', 'class': 'form-control mb-3'}), não é necessário, pois já foi definido acima
            'local': forms.TextInput(attrs={'placeholder': 'digite o local do evento', 'class': 'form-control mb-3'}),
            'imagemBanner': forms.FileInput(attrs={'class': 'form-control mb-3','accept': 'image/*'}),
            'dataInicio': forms.DateInput(attrs={'class': 'form-control mb-3', 'type': 'date'}),
            'dataFim': forms.DateInput(attrs={'class': 'form-control mb-3', 'type': 'date'}),
            'tipoEvento': forms.Select(attrs={'class': 'form-select mb-3'}),
            'eventoMultiplo': forms.CheckboxInput(attrs={'class': 'form-check-input mb-3'}),
            'eventoPublico': forms.CheckboxInput(attrs={'class': 'form-check-input mb-3'}),
        }

    # função para interceptar o texto digitado do cmpo apoiadores e transformar em uma lista de nomes limpos
    def clean_apoiadores(self):
        """Transforma a string digitada em uma lista de nomes limpos"""
        texto_apoiadores = self.cleaned_data.get('apoiadores', '')
        if not texto_apoiadores:
            return []
        
        # Divide por vírgula e remove espaços extras de cada nome
        return [nome.strip() for nome in texto_apoiadores.split(',') if nome.strip()]
    
    
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
