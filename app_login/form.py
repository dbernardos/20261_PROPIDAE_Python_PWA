from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario
from dateutil.relativedelta import relativedelta
import re
from django.utils import timezone
from django.contrib.auth.password_validation import validate_password, password_validators_help_text_html


# FORMS do LOGIN.
# -----------------------------------------------

def validar_cpf_matematico(cpf_numeros):
    if len(cpf_numeros) != 11 or cpf_numeros == cpf_numeros[0] * 11:
        return False
    for i in range(9, 11):
        soma = sum(int(cpf_numeros[num]) * ((i + 1) - num) for num in range(0, i))
        digito = ((soma * 10) % 11) % 10
        if digito != int(cpf_numeros[i]):
            return False
    return True
  


# FORMULÁRIO 1: OBRIGATÓRIO (CRIA O USUÁRIO NO BANCO)
class CadastroEtapa1Form(forms.ModelForm):
  username = forms.CharField(max_length=150, label='Nome de Usuário')
  senha = forms.CharField(
      widget=forms.PasswordInput(
          attrs={'class': 'form-control', 'placeholder': 'Digite sua senha'}
      ),
      label='Senha',
      help_text=password_validators_help_text_html(),
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
            attrs={'class': 'form-control',
                'placeholder': '000.000.000-00',
                'inputmode': 'numeric',
                'maxlength': '14',
                'required': 'required',
                }
        ),
    }
    

  def clean_cpf(self):
    cpf = self.cleaned_data.get('cpf', '')
    cpf_limpo = re.sub(r'\D', '', cpf)
    if not validar_cpf_matematico(cpf_limpo):
      raise forms.ValidationError('CPF inválido. Verifique os dígitos informados.')
    cpf_formatado = f'{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}'
    if Usuario.objects.filter(cpf=cpf_formatado).exists():
      raise forms.ValidationError('Este CPF já está cadastrado.')
    return cpf_formatado

  def clean_email(self):
    email = self.cleaned_data.get('email')
    if User.objects.filter(email=email).exists():
      raise forms.ValidationError(
          'Este e-mail já está em uso por outro usuário.'
      )
    return email

  def clean_username(self):
    username = self.cleaned_data.get('username', '').strip()
    if '@' in username:
      raise forms.ValidationError('O nome de usuário não pode conter "@".')
    if User.objects.filter(username__iexact=username).exists():
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

    if senha:
      usuario_temp = User(
          username=cleaned_data.get('username') or '',
          first_name=cleaned_data.get('nome') or '',
          email=cleaned_data.get('email') or '',
      )
      try:
        validate_password(senha, user=usuario_temp)
      except forms.ValidationError as e:
        self.add_error('senha', e)

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

def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Formata a data existente para AAAA-MM-DD[cite: 1]
        if self.instance and self.instance.pk and self.instance.dataNascimento:
            self.initial['dataNascimento'] = (
                self.instance.dataNascimento.strftime('%Y-%m-%d')
            )
        # Bloqueia edição do CPF se já estiver cadastrado
        if self.instance and self.instance.pk and self.instance.cpf:
            self.fields['cpf'].disabled = True


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
    
    labels = {
        'fotoPerfil': 'Foto de Perfil (Máx. 2MB)',
    }
    
    widgets = {
        'biografia': forms.Textarea(attrs={'rows': 3}),
        'telefone': forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': '(00) 00000-0000',
                'inputmode': 'numeric',
                'maxlength': '15',
            }
        ),
    }

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    # Torna todos os campos da etapa 2 opcionais
    for field in self.fields.values():
      field.required = False

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
            #'cpf', 
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
            #'cpf': 'CPF',
            'telefone': 'Telefone',
            'dataNascimento': 'Data de Nascimento',
            
            'formacao': 'Formação Acadêmica',
            'empresa': 'Empresa / Instituição',
            'cargo': 'Cargo',
            'fotoPerfil': 'Foto de Perfil (Máx. 2MB)',
            'biografia': 'Biografia',
        }
        
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
           # 'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00'}),
            'telefone': forms.TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': '(00) 00000-0000',
                    'inputmode': 'numeric',
                    'maxlength': '15',}
            ),
            
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
        # Formata a data existente para AAAA-MM-DD 
        if self.instance and self.instance.pk and self.instance.dataNascimento:
            self.initial['dataNascimento'] = (
            self.instance.dataNascimento.strftime('%Y-%m-%d')
        )