from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario
from dateutil.relativedelta import relativedelta
import re
from django.utils import timezone


# FORMULÁRIO 1: OBRIGATÓRIO (CRIA O USUÁRIO NO BANCO)
class CadastroEtapa1Form(forms.ModelForm):
  username = forms.CharField(max_length=150, label='Nome de Usuário')
  senha = forms.CharField(
      widget=forms.PasswordInput(
          attrs={'class': 'form-control', 'placeholder': 'Digite sua senha'}
      ),
      label='Senha',
  )
  confirmar_senha = forms.CharField(
      widget=forms.PasswordInput(
          attrs={'class': 'form-control', 'placeholder': 'Confirme sua senha'}
      ),
      label='Confirmar Senha',
  )

  class Meta:
    model = Usuario
    fields = ['nome', 'cpf', 'email', 'dataNascimento']
    widgets = {
        'dataNascimento': forms.DateInput(
            format='%Y-%m-%d',
            attrs={
                'class': 'form-control',
                'type': 'date',
                'max': timezone.localdate().isoformat(),
                'min': (timezone.localdate() - relativedelta(years=127)).isoformat,
                'required': 'required',
            },
        ),
        'cpf': forms.TextInput(
            attrs={'placeholder': '000.000.000-00', 'required': 'required'}
        ),
    }

  def clean_cpf(self):
    cpf = self.cleaned_data.get('cpf')
    cpf_limpo = re.sub(r'\D', '', cpf)
    if len(cpf_limpo) != 11:
      raise forms.ValidationError('Insira um CPF válido com 11 dígitos.')
    if Usuario.objects.filter(cpf=cpf).exists():
      raise forms.ValidationError('Este CPF já está cadastrado.')
    return cpf

  def clean_email(self):
    email = self.cleaned_data.get('email')
    if User.objects.filter(email=email).exists():
      raise forms.ValidationError(
          'Este e-mail já está em uso por outro usuário.'
      )
    return email

  def clean_username(self):
    username = self.cleaned_data.get('username')
    if User.objects.filter(username=username).exists():
      raise forms.ValidationError('Este nome de usuário já está em uso.')
    return username

  def clean_dataNascimento(self):
    
    dataNascimento = self.cleaned_data.get('dataNascimento')

    if dataNascimento:
        hoje = timezone.localdate()
        data_minima = hoje - relativedelta(years=127)
    
        if dataNascimento > hoje:
            raise forms.ValidationError(
                'A data de nascimento não pode ser maior que a data atual.'
            )
        if dataNascimento < data_minima:
            raise forms.ValidationError(
                'A data limite é de 127 anos atrás.'
            )  
    return dataNascimento

  def clean(self):
    cleaned_data = super().clean()
    senha = cleaned_data.get('senha')
    confirmar_senha = cleaned_data.get('confirmar_senha')
    if senha and confirmar_senha and senha != confirmar_senha:
      self.add_error(
          'confirmar_senha', 'As senhas não coincidem. Tente novamente.'
      )
    return cleaned_data

  def save(self, commit=True):
    user = User.objects.create_user(
        username=self.cleaned_data['username'],
        email=self.cleaned_data['email'],
        password=self.cleaned_data['senha'],
        first_name=self.cleaned_data['nome'],
    )
    usuario = super().save(commit=False)
    usuario.user_django = user
    if commit:
      usuario.save()
    return usuario


# FORMULÁRIO 2: Não Obrigatório 
class CadastroEtapa2Form(forms.ModelForm):

  class Meta:
    model = Usuario
    fields = [
        'telefone',
        'formacao',
        'empresa',
        'cargo',
        'fotoPerfil',
        'biografia',
    ]
    widgets = {
        'biografia': forms.Textarea(attrs={'rows': 3}),
    }

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    # Torna todos os campos da etapa 2 opcionais
    for field in self.fields.values():
      field.required = False

'''
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
            'formacao',  'empresa',  'cargo',  'fotoPerfil',  'biografia', 
        ]
        
        # Ajustando os widgets para melhor usabilidade no HTML
        widgets = {
           'dataNascimento': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'class': 'form-control', 'type': 'date', 'max': timezone.localdate().isoformat()}
            ),
            'cpf': forms.TextInput(attrs={'placeholder': '000.000.000-00', 'required': 'required'}),
            'biografia': forms.Textarea(attrs={'rows': 3}),
        }

    
    @property
    def etapa1_fields(self):
        """Retorna os campos da 1ª etapa"""
        campos = [
            'nome',
            'username',
            'cpf',
            'dataNascimento',
            'email',
            'telefone',
            'senha',
            'confirmar_senha',
            
        ]
        return [self[f] for f in campos if f in self.fields]
    
    @property
    def etapa2_fields(self):
        """Retorna os campos da 2ª etapa"""
        campos = [
            
            'formacao',
            'empresa',
            'cargo',
            'fotoPerfil',
            'biografia',
        ]
        return [self[f] for f in campos if f in self.fields]
    
    
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
    
    def clean_dataNascimento(self):
        dataNascimento = self.cleaned_data.get('dataNascimento')
        
        # Compara a data inserida com a data de hoje
        if dataNascimento and dataNascimento > timezone.localdate():
            raise forms.ValidationError("A data de nascimento não pode ser maior que a data atual.")
            
        return dataNascimento
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Nota: Se o seu sistema usa o 'email' ou 'cpf' como username, 
        # mude 'username=nome' para 'username=email' ou 'username=cpf' abaixo:
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nome já está cadastrado em nosso sistema.")
        return username
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Formata a data existente para AAAA-MM-DD sem alterar a estrutura do formulário
        if self.instance and self.instance.pk and self.instance.dataNascimento:
            self.initial['dataNascimento'] = (
            self.instance.dataNascimento.strftime('%Y-%m-%d')
        )
'''
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
            
            'formacao', 
            'empresa', 
            'cargo', 
            'fotoPerfil', 
            'biografia'
        ]
        
        labels = {
            'nome': 'Nome Completo',
            'email': 'E-mail',
            'cpf': 'CPF',
            'telefone': 'Telefone',
            'dataNascimento': 'Data de Nascimento',
            
            'formacao': 'Formação Acadêmica',
            'empresa': 'Empresa / Instituição',
            'cargo': 'Cargo',
            'fotoPerfil': 'Foto de Perfil',
            'biografia': 'Biografia',
        }
        
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
            'dataNascimento': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'class': 'form-control', 'type': 'date', 'max': timezone.localdate().isoformat()}
            ),
            
            'formacao': forms.TextInput(attrs={'class': 'form-control'}),
            'empresa': forms.TextInput(attrs={'class': 'form-control'}),
            'cargo': forms.TextInput(attrs={'class': 'form-control'}),   
            'fotoPerfil': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'biografia': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Formata a data existente para AAAA-MM-DD sem alterar a estrutura do formulário
        if self.instance and self.instance.pk and self.instance.dataNascimento:
            self.initial['dataNascimento'] = (
            self.instance.dataNascimento.strftime('%Y-%m-%d')
        )