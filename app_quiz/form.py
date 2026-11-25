
from django import forms
from .models import Quiz, Resposta


class RespostaQuizForm(forms.ModelForm):
    valor_resposta = forms.DecimalField(
        required=True,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-lg',
            'step': '0.01',
            'placeholder': 'Digite sua resposta',
        }),
    )

    class Meta:
        model = Resposta
        fields = ['valor_resposta']

class CadastroQuizForm(forms.ModelForm):
    CAMPOS_METRICA = ['unidade_medida', 'valor_minimo', 'valor_maximo', 'valor_ideal']
    CAMPOS_MULTIPLA = ['opcao_a', 'opcao_b', 'opcao_c', 'opcao_d', 'alternativa_correta']

    class Meta:
        model = Quiz
        fields = [
            'tipo', 'titulo', 'subtitulo', 'pergunta', 'dica',
            'unidade_medida', 'valor_minimo', 'valor_maximo', 'valor_ideal',
            'opcao_a', 'opcao_b', 'opcao_c', 'opcao_d', 'alternativa_correta', 'ativo',
        ]
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select', 'id': 'id_tipo'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Desafio de Medição'}),
            'subtitulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Breve descrição opcional'}),
            'pergunta': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Digite o enunciado do desafio...'}),
            'dica': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Dica opcional para o participante'}),
            'unidade_medida': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: mm, kg, °C, unidades'}),
            'valor_minimo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'valor_maximo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'valor_ideal': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'opcao_a': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Alternativa A'}),
            'opcao_b': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Alternativa B'}),
            'opcao_c': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Alternativa C (opcional)'}),
            'opcao_d': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Alternativa D (opcional)'}),
            'alternativa_correta': forms.Select(attrs={'class': 'form-select'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.CAMPOS_METRICA + self.CAMPOS_MULTIPLA:
            self.fields[campo].required = False

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')

        if tipo == 'METRICA':
            for campo in self.CAMPOS_MULTIPLA:
                cleaned_data[campo] = None

            vmin, vmax, videal = cleaned_data.get('valor_minimo'), cleaned_data.get('valor_maximo'), cleaned_data.get('valor_ideal')
            if not cleaned_data.get('unidade_medida'):
                self.add_error('unidade_medida', 'Informe a unidade de medida.')
            if vmin is None:
                self.add_error('valor_minimo', 'Informe o valor mínimo.')
            if vmax is None:
                self.add_error('valor_maximo', 'Informe o valor máximo.')
            if vmin is not None and vmax is not None:
                if vmin > vmax:
                    self.add_error('valor_maximo', 'O valor máximo não pode ser menor que o mínimo.')
                if videal is not None and not (vmin <= videal <= vmax):
                    self.add_error('valor_ideal', 'O valor ideal deve estar entre o mínimo e o máximo.')

        elif tipo == 'MULTIPLA':
            cleaned_data['unidade_medida'] = ''
            for campo in ['valor_minimo', 'valor_maximo', 'valor_ideal']:
                cleaned_data[campo] = None

            opcoes = {letra: (cleaned_data.get(f'opcao_{letra.lower()}') or '').strip() for letra in 'ABCD'}
            correta = cleaned_data.get('alternativa_correta')

            if not opcoes['A']:
                self.add_error('opcao_a', 'Preencha a alternativa A.')
            if not opcoes['B']:
                self.add_error('opcao_b', 'Preencha a alternativa B.')
            if not correta:
                self.add_error('alternativa_correta', 'Selecione qual alternativa é a correta.')
            elif not opcoes.get(correta):
                self.add_error('alternativa_correta', f'A alternativa {correta} está vazia e não pode ser o gabarito.')

        return cleaned_data