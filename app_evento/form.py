from datetime import datetime
from django import forms
from django.utils import timezone
from .models import Apoiador, Atividade, Evento


class EventoForm(forms.ModelForm):
    apoiadores = forms.CharField(
        required=False,
        label='Apoiadores / Patrocinadores (separe por vírgulas)',
        widget=forms.TextInput(attrs={
            'placeholder': 'Ex: Google, Microsoft, Ambev',
            'class': 'form-control mb-3',
        }),
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
        ]
        labels = {
            'nome': 'Nome do Evento',
            'descricao': 'Descrição',
            'emailContato': 'E-mail de Contato',
            'apoiadores': 'Apoiadores / Patrocinadores',
            'local': 'Local do Evento',
            'imagemBanner': 'Imagem do Banner (Máx. 4MB)',
            'dataInicio': 'Data de Início',
            'dataFim': 'Data de Término',
            'tipoEvento': 'Tipo do Evento',
        }
        widgets = {
            'nome': forms.TextInput(attrs={
                'placeholder': 'Ex.: XXIX Colóquio de Usinagem',
                'class': 'form-control mb-3',
            }),
            'descricao': forms.Textarea(attrs={
                'placeholder': 'Ex.: Resumo dos objetivos e temas abordados...',
                'class': 'form-control mb-3',
                'rows': 4,
            }),
            'emailContato': forms.EmailInput(attrs={
                'placeholder': 'Ex.: contato@evento.com',
                'class': 'form-control mb-3',
            }),
            'local': forms.TextInput(attrs={
                'placeholder': 'Ex.: Rua dos Imigrantes, 445, Rau, Jaraguá do Sul - SC, CEP 89254-430',
                'class': 'form-control mb-3',
            }),
            'imagemBanner': forms.FileInput(attrs={
                'class': 'form-control mb-3',
                'accept': 'image/*',
            }),
            'dataInicio': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'class': 'form-control mb-3', 'type': 'date'},
            ),
            'dataFim': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'class': 'form-control mb-3', 'type': 'date'},
            ),
            'tipoEvento': forms.Select(attrs={'class': 'form-select mb-3'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            nomes_apoiadores = [ap.nome for ap in self.instance.apoiadores.all()]
            self.initial['apoiadores'] = ', '.join(nomes_apoiadores)

            if self.instance.dataInicio:
                self.initial['dataInicio'] = self.instance.dataInicio.strftime('%Y-%m-%d')
            if self.instance.dataFim:
                self.initial['dataFim'] = self.instance.dataFim.strftime('%Y-%m-%d')

    def clean_apoiadores(self):
        texto_apoiadores = self.cleaned_data.get('apoiadores', '')
        if not texto_apoiadores:
            return []
        return [nome.strip() for nome in texto_apoiadores.split(',') if nome.strip()]

    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('dataInicio')
        data_fim = cleaned_data.get('dataFim')

        if data_inicio and data_fim and data_inicio > data_fim:
            self.add_error(
                'dataFim',
                'A data de término não pode ser anterior à data de início.',
            )

        # Ao editar, garante que atividades já cadastradas não fiquem fora do novo período
        if self.instance and self.instance.pk and data_inicio and data_fim and data_inicio <= data_fim:
            for ativ in self.instance.atividade_set.all():
                ativ_inicio = (
                    timezone.localtime(ativ.horaInicio).date()
                    if timezone.is_aware(ativ.horaInicio)
                    else ativ.horaInicio.date()
                )
                ativ_fim = (
                    timezone.localtime(ativ.horaFim).date()
                    if timezone.is_aware(ativ.horaFim)
                    else ativ.horaFim.date()
                )
                if ativ_inicio < data_inicio:
                    self.add_error(
                        'dataInicio',
                        f'Existe atividade ("{ativ.nome}") iniciando em {ativ_inicio.strftime("%d/%m/%Y")}, antes da nova data inicial.',
                    )
                    break
                if ativ_fim > data_fim:
                    self.add_error(
                        'dataFim',
                        f'Existe atividade ("{ativ.nome}") terminando em {ativ_fim.strftime("%d/%m/%Y")}, após a nova data final.',
                    )
                    break

        return cleaned_data

    def save(self, commit=True):
        evento = super().save(commit=False)
        nomes_apoiadores = self.cleaned_data.get('apoiadores', [])

        def save_m2m():
            objetos_apoiadores = [
                Apoiador.objects.get_or_create(nome=nome)[0]
                for nome in nomes_apoiadores
            ]
            evento.apoiadores.set(objetos_apoiadores)

        if commit:
            evento.save()
            save_m2m()
        else:
            self.save_m2m = save_m2m

        return evento


class AtividadeForm(forms.ModelForm):
    horaInicio = forms.DateTimeField(
        label='Hora de Início',
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M'],
        widget=forms.DateTimeInput(
            format='%Y-%m-%dT%H:%M',
            attrs={'type': 'datetime-local'},
        ),
    )
    horaFim = forms.DateTimeField(
        label='Hora de Término',
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M'],
        widget=forms.DateTimeInput(
            format='%Y-%m-%dT%H:%M',
            attrs={'type': 'datetime-local'},
        ),
    )

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
            'tipoAtividade': 'Tipo de Atividade',
            'complementoLocal': 'Complemento do Local',
            'limitePessoas': 'Limite de Participantes',
        }
        widgets = {
            'nome': forms.TextInput(attrs={
                'placeholder': 'Ex.: Workshop de Gestão de Projetos',
            }),
            'descricao': forms.Textarea(attrs={
                'placeholder': 'Ex.: Tópicos abordados, dinâmicas e objetivos da atividade...',
                'rows': 4,
            }),
            'tipoAtividade': forms.Select(),
            'complementoLocal': forms.TextInput(attrs={
                'placeholder': 'Ex.: Sala 204 - Bloco B',
            }),
            'limitePessoas': forms.NumberInput(attrs={
                'placeholder': 'Ex.: 50',
                'min': 1,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            if self.instance.horaInicio:
                dt_inicio = (
                    timezone.localtime(self.instance.horaInicio)
                    if timezone.is_aware(self.instance.horaInicio)
                    else self.instance.horaInicio
                )
                self.initial['horaInicio'] = dt_inicio.strftime('%Y-%m-%dT%H:%M')
            if self.instance.horaFim:
                dt_fim = (
                    timezone.localtime(self.instance.horaFim)
                    if timezone.is_aware(self.instance.horaFim)
                    else self.instance.horaFim
                )
                self.initial['horaFim'] = dt_fim.strftime('%Y-%m-%dT%H:%M')

    @staticmethod
    def _para_data(valor):
        if isinstance(valor, datetime):
            if timezone.is_aware(valor):
                valor = timezone.localtime(valor)
            return valor.date()
        return valor

    @staticmethod
    def _formatar_data(valor):
        if isinstance(valor, datetime):
            if timezone.is_aware(valor):
                valor = timezone.localtime(valor)
            return valor.strftime('%d/%m/%Y às %H:%M')
        return valor.strftime('%d/%m/%Y')

    def clean_limitePessoas(self):
        limite = self.cleaned_data.get('limitePessoas')
        if limite is not None:
            if limite < 1:
                raise forms.ValidationError(
                    'O limite deve ser de pelo menos 1 participante (ou deixe vazio para ilimitado).'
                )
            if self.instance and self.instance.pk:
                inscritos_atuais = self.instance.participa_set.count()
                if limite < inscritos_atuais:
                    raise forms.ValidationError(
                        f'Já existem {inscritos_atuais} participantes inscritos; o limite não pode ser menor que esse número.'
                    )
        return limite

    def clean(self):
        cleaned_data = super().clean()
        hora_inicio = cleaned_data.get('horaInicio')
        hora_fim = cleaned_data.get('horaFim')
        evento = cleaned_data.get('evento') or getattr(self.instance, 'evento', None)

        if hora_inicio and hora_fim and hora_fim <= hora_inicio:
            self.add_error(
                'horaFim',
                'A hora de término deve ser posterior à hora de início.',
            )

        if evento and hora_inicio and hora_fim:
            if self._para_data(hora_inicio) < self._para_data(evento.dataInicio):
                self.add_error(
                    'horaInicio',
                    f'A atividade não pode começar antes do evento ({self._formatar_data(evento.dataInicio)}).',
                )

            if self._para_data(hora_fim) > self._para_data(evento.dataFim):
                self.add_error(
                    'horaFim',
                    f'A atividade não pode terminar após o encerramento do evento ({self._formatar_data(evento.dataFim)}).',
                )

        return cleaned_data