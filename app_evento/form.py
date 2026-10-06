from django import forms
from .models import Evento, Atividade, Apoiador
from datetime import date, datetime

# Create your EVENTO forms here.
# -----------------------------------------------
class EventoForm(forms.ModelForm):

    # Campo de apoiadores como CharField para entrada de texto
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
            'eventoPublico': 'Evento Público?',
        }
        
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'digite o nome do evento', 'class': 'form-control mb-3'}),
            'descricao': forms.Textarea(attrs={'placeholder': 'digite a descrição do evento', 'class': 'form-control mb-3', 'rows': 4}),
            'emailContato': forms.EmailInput(attrs={'placeholder': 'digite o e-mail de contato', 'class': 'form-control mb-3'}),
            'local': forms.TextInput(attrs={'placeholder': 'digite o local do evento', 'class': 'form-control mb-3'}),
            'imagemBanner': forms.FileInput(attrs={'class': 'form-control mb-3', 'accept': 'image/*'}),
            'dataInicio': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'class': 'form-control', 'type': 'date'}
            ),
           'dataFim': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'tipoEvento': forms.Select(attrs={'class': 'form-select mb-3'}),
            'eventoPublico': forms.CheckboxInput(attrs={'class': 'form-check-input mb-3'}),
        }
     
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # CORREÇÃO: Sobrescreve 'self.initial['apoiadores']' com a string formatada.
        # Se alterarmos apenas 'self.fields[...].initial', o Django ignora e mantêm o QuerySet em 'self.initial'.
        if self.instance and self.instance.pk:
            nomes_apoiadores = [ap.nome for ap in self.instance.apoiadores.all()]
            self.initial['apoiadores'] = ', '.join(nomes_apoiadores)
            
        if self.instance and self.instance.pk and self.instance.dataInicio:
            self.initial['dataInicio'] = self.instance.dataInicio.strftime('%Y-%m-%d')
        if self.instance and self.instance.pk and self.instance.dataFim:
            self.initial['dataFim'] = self.instance.dataFim.strftime('%Y-%m-%d')    

    def clean_apoiadores(self):
        """Transforma a string digitada em uma lista de nomes limpos"""
        texto_apoiadores = self.cleaned_data.get('apoiadores', '')
        if not texto_apoiadores:
            return []
        
        # Divide por vírgula e remove espaços extras de cada nome
        return [nome.strip() for nome in texto_apoiadores.split(',') if nome.strip()]

    def clean_dataInicio(self):
        dataInicio = self.cleaned_data.get('dataInicio')
        dataFim = self.cleaned_data.get('dataFim')

        if dataInicio and dataFim and dataInicio > dataFim:
            raise forms.ValidationError("A data de início não pode ser maior que a data de término.")
        
        return dataInicio

    def save(self, commit=True):
        # Salva o evento sem commitar no banco por enquanto
        evento = super().save(commit=False)

        nomes_apoiadores = self.cleaned_data.get('apoiadores', [])

        def save_m2m():
            objetos_apoiadores = []
            for nome in nomes_apoiadores:
                # Busca se o apoiador já existe pelo nome ou cria um novo no banco
                apoiador_obj, _ = Apoiador.objects.get_or_create(nome=nome)
                objetos_apoiadores.append(apoiador_obj)
            
            # Associa a lista de objetos Apoiador ao evento
            evento.apoiadores.set(objetos_apoiadores)

        if commit:
            evento.save()
            save_m2m()
        else:
            self.save_m2m = save_m2m

        return evento



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
            'tipoAtividade': 'Tipo de atividade',
            'complementoLocal': 'Complemento do Local',
            'horaInicio': 'Hora de Início',
            'horaFim': 'Hora de Término',
            'limitePessoas': 'Limite de Participantes',
        }
        
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'digite o nome da atividade', 'class': 'form-control mb-3'}),
            'descricao': forms.Textarea(attrs={'placeholder': 'digite a descrição da atividade', 'class': 'form-control mb-3', 'rows': 4}),
            'tipoAtividade': forms.Select(attrs={'class': 'form-select mb-3'}),
            'complementoLocal': forms.TextInput(attrs={'placeholder': 'digite o complemento do local', 'class': 'form-control mb-3'}),
            'horaInicio': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={'class': 'form-control mb-3', 'type': 'datetime-local'}
            ),
            'horaFim': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={'class': 'form-control mb-3', 'type': 'datetime-local'}
            ),
            'limitePessoas': forms.NumberInput(attrs={'placeholder': 'digite o limite de participantes', 'class': 'form-control mb-3', 'type': 'number'}),
        }


    def clean(self):
        cleaned_data = super().clean()
        horaInicio = cleaned_data.get('horaInicio')
        horaFim = cleaned_data.get('horaFim')

        evento = cleaned_data.get('evento') or getattr(self.instance, 'evento', None)

        # 1. Checagem de ordem simples (término < início)
        if horaInicio and horaFim and horaFim < horaInicio:
            self.add_error(
                'horaFim',
                'A hora de término não pode ser anterior à hora de início.',
            )

        # 2. Checagem dos limites do Evento
        if evento and horaInicio and horaFim:
            # Converte para .date() para comparação segura se houver mistura de date/datetime
            dt_atv_inicio = (
                horaInicio.date() if isinstance(horaInicio, datetime) else horaInicio
            )
            dt_atv_fim = horaFim.date() if isinstance(horaFim, datetime) else horaFim

            dt_ev_inicio = (
                evento.dataInicio.date()
                if isinstance(evento.dataInicio, datetime)
                else evento.dataInicio
            )
            dt_ev_fim = (
                evento.dataFim.date()
                if isinstance(evento.dataFim, datetime)
                else evento.dataFim
            )

            # Prepara as strings formatadas antecipadamente (garante que as variáveis sempre existam)
            inicio_fmt = (
                evento.dataInicio.strftime('%d/%m/%Y às %H:%M')
                if isinstance(evento.dataInicio, datetime)
                else evento.dataInicio.strftime('%d/%m/%Y')
            )

            fim_fmt = (
                evento.dataFim.strftime('%d/%m/%Y às %H:%M')
                if isinstance(evento.dataFim, datetime)
                else evento.dataFim.strftime('%d/%m/%Y')
            )

            # Valida se a atividade começa antes do evento
            if dt_atv_inicio < dt_ev_inicio:
                self.add_error(
                    'horaInicio',
                    f'A atividade não pode começar antes do evento ({inicio_fmt}).',
                )

            # Valida se a atividade termina depois do evento
            if dt_atv_fim > dt_ev_fim:
                self.add_error(
                    'horaFim',
                    f'A atividade não pode terminar após o encerramento do evento'
                    f' ({fim_fmt}).',
                )

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if self.instance and self.instance.pk:
          
            if self.instance.horaInicio:
                self.initial['horaInicio'] = self.instance.horaInicio.strftime('%Y-%m-%dT%H:%M')
            
            if self.instance.horaFim:
                self.initial['horaFim'] = self.instance.horaFim.strftime('%Y-%m-%dT%H:%M')