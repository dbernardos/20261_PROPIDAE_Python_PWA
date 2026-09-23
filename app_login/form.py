from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario
import re

class CadastroUsuarioForm(forms.ModelForm):

    username = forms.CharField(max_length=150, label="Nome de Usuário")

    # Criamos campos extras que não estão no model Usuario, mas são necessários para o login
    senha = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Digite sua senha'}),
        label='Senha'
    )
    confirmar_senha = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirme sua senha'}),
        label='Confirmar Senha'
    )

    class Meta:
        model = Usuario
        # Campos do seu model que aparecerão na tela para o usuário preencher
        fields = [
            'nome', 'cpf', 'email', 'telefone', 'dataNascimento',
            'biografia', 'fotoPerfil', 'cargo', 'formacao', 'empresa'
        ]
        
        # Ajustando os widgets para melhor usabilidade no HTML
        widgets = {
            'dataNascimento': forms.DateInput(attrs={'type': 'date'}),
            'cpf': forms.TextInput(attrs={'placeholder': '000.000.000-00', 'required': 'required'}),
            'biografia': forms.Textarea(attrs={'rows': 3}),
        }

    # 2. Exemplo de validação individual para o CPF
    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        # Remove pontos e traços para validar apenas os números
        cpf_limio = re.sub(r'\D', '', cpf)
        if len(cpf_limio) != 11:
            raise forms.ValidationError("Insira um CPF válido com 11 dígitos.")
        return cpf

    # Validação para verificar se as senhas são iguais
    def clean(self):
        cleaned_data = super().clean()
        senha = cleaned_data.get('senha')
        confirmar_senha = cleaned_data.get('confirmar_senha')

        if senha and confirmar_senha and senha != confirmar_senha:
            self.add_error('confirmar_senha', 'As senhas não coincidem. Tente novamente.')
        
        return cleaned_data

    # Validação para garantir que o email não está sendo usado no User do Django
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail já está em uso por outro usuário.")
        return email

# Create your LOGIN forms here.
# -----------------------------------------------
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

class EditarPerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        # O atributo 'fields' DEVE estar dentro de 'class Meta'
        fields = [
            'nome', 
            'email', 
            'cpf', 
            'telefone', 
            'dataNascimento', 
            'cargo', 
            'empresa', 
            'formacao', 
            'fotoPerfil', 
            'biografia'
        ]
        
        labels = {
            'nome': 'Nome Completo',
            'email': 'E-mail',
            'cpf': 'CPF',
            'telefone': 'Telefone',
            'dataNascimento': 'Data de Nascimento',
            'cargo': 'Cargo',
            'empresa': 'Empresa / Instituição',
            'formacao': 'Formação Acadêmica',
            'fotoPerfil': 'Foto de Perfil',
            'biografia': 'Biografia',
        }
        
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
            'dataNascimento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cargo': forms.TextInput(attrs={'class': 'form-control'}),
            'empresa': forms.TextInput(attrs={'class': 'form-control'}),
            'formacao': forms.TextInput(attrs={'class': 'form-control'}),
            'fotoPerfil': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'biografia': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
