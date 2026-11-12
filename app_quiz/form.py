from django import forms
from .models import Resposta, Quiz

# FORMS do QUIZ.
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
    """Form para cadastro e edição de desafio único (Métrica ou Múltipla Escolha)"""
    class Meta:
        model = Quiz
        fields = [
            'tipo',
            'titulo',
            'subtitulo',
            'pergunta',
            'dica',
            'unidade_medida',
            'valor_minimo',
            'valor_maximo',
            'valor_ideal',
            'opcao_a',
            'opcao_b',
            'opcao_c',
            'opcao_d',
            'alternativa_correta',
            'ativo',
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
        campos_condicionais = [
            'unidade_medida', 'valor_minimo', 'valor_maximo', 'valor_ideal',
            'opcao_a', 'opcao_b', 'opcao_c', 'opcao_d', 'alternativa_correta'
        ]
        for campo in campos_condicionais:
            if campo in self.fields:
                self.fields[campo].required = False

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')

        if tipo == 'METRICA':
            # Limpa campos de múltipla escolha
            for opt in ['opcao_a', 'opcao_b', 'opcao_c', 'opcao_d', 'alternativa_correta']:
                cleaned_data[opt] = None

            unidade = cleaned_data.get('unidade_medida')
            vmin = cleaned_data.get('valor_minimo')
            vmax = cleaned_data.get('valor_maximo')
            videal = cleaned_data.get('valor_ideal')

            if not unidade:
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
            # Limpa campos numéricos
            cleaned_data['unidade_medida'] = ''
            cleaned_data['valor_minimo'] = None
            cleaned_data['valor_maximo'] = None
            cleaned_data['valor_ideal'] = None

            opcoes = {
                'A': (cleaned_data.get('opcao_a') or '').strip(),
                'B': (cleaned_data.get('opcao_b') or '').strip(),
                'C': (cleaned_data.get('opcao_c') or '').strip(),
                'D': (cleaned_data.get('opcao_d') or '').strip(),
            }
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