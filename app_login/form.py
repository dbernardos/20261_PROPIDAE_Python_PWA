from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario

class CadastroUsuarioForm(forms.ModelForm):
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
            'biografia': forms.Textarea(attrs={'rows': 3}),
        }

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