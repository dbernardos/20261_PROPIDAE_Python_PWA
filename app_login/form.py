import re
from dateutil.relativedelta import relativedelta
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import password_validators_help_text_html, validate_password
from django.db import transaction
from django.utils import timezone

from .models import Usuario


def validar_cpf_matematico(cpf_numeros):
    if len(cpf_numeros) != 11 or cpf_numeros == cpf_numeros[0] * 11:
        return False
    for i in range(9, 11):
        soma = sum(int(cpf_numeros[num]) * ((i + 1) - num) for num in range(0, i))
        digito = ((soma * 10) % 11) % 10
        if digito != int(cpf_numeros[i]):
            return False
    return True


def validar_data_nascimento(data):
    if not data:
        return data
    hoje = timezone.localdate()
    if data > hoje:
        raise forms.ValidationError('A data de nascimento não pode ser maior que a data atual.')
    if data < hoje - relativedelta(years=127):
        raise forms.ValidationError('A data limite é de 127 anos atrás.')
    return data


def configurar_campo_data(field):
    hoje = timezone.localdate()
    field.widget.attrs.update({
        'max': hoje.isoformat(),
        'min': (hoje - relativedelta(years=127)).isoformat(),
    })


LABELS_COMPLEMENTARES = {
    'telefone': 'Telefone',
    'formacao': 'Formação Acadêmica',
    'empresa': 'Empresa / Instituição',
    'cargo': 'Cargo',
    'fotoPerfil': 'Foto de Perfil (Máx. 2MB)',
    'biografia': 'Biografia',
}

WIDGETS_COMPLEMENTARES = {
    'telefone': forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': '(00) 00000-0000',
        'inputmode': 'numeric',
        'maxlength': '15',
    }),
    'formacao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex.: Engenharia de Software'}),
    'empresa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex.: Univille / Empresa LTDA'}),
    'cargo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex.: Estudante, Desenvolvedor, Analista'}),
    'fotoPerfil': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
    'biografia': forms.Textarea(attrs={
        'class': 'form-control',
        'rows': 3,
        'placeholder': 'Conte um pouco sobre você, suas áreas de interesse ou experiência...',
    }),
}


class CadastroEtapa1Form(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        label='Nome de Usuário',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    senha = forms.CharField(
        label='Senha',
        help_text=password_validators_help_text_html(),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Digite sua senha forte'}),
    )
    confirmar_senha = forms.CharField(
        label='Confirmar Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Repita a senha digitada'}),
    )

    class Meta:
        model = Usuario
        fields = ['nome', 'cpf', 'email', 'dataNascimento']
        labels = {
            'nome': 'Nome',
            'cpf': 'CPF',
            'email': 'E-mail',
            'dataNascimento': 'Data de Nascimento',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex.: Maria Silva Santos'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ex.: maria.silva@email.com'}),
            'dataNascimento': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'class': 'form-control', 'type': 'date', 'required': 'required'},
            ),
            'cpf': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '000.000.000-00',
                'inputmode': 'numeric',
                'maxlength': '14',
                'required': 'required',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        configurar_campo_data(self.fields['dataNascimento'])

    def clean_cpf(self):
        cpf_limpo = re.sub(r'\D', '', self.cleaned_data.get('cpf', ''))
        if not validar_cpf_matematico(cpf_limpo):
            raise forms.ValidationError('CPF inválido. Verifique os dígitos informados.')
        cpf_formatado = f'{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}'
        if Usuario.objects.filter(cpf=cpf_formatado).exists():
            raise forms.ValidationError('Este CPF já está cadastrado.')
        return cpf_formatado

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip().lower()
        if User.objects.filter(email__iexact=email).exists() or Usuario.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Este e-mail já está em uso por outro usuário.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if '@' in username:
            raise forms.ValidationError('O nome de usuário não pode conter "@".')
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('Este nome de usuário já está em uso.')
        return username
    
    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['dataNascimento'].required = True
            configurar_campo_data(self.fields['dataNascimento'])

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
            self.add_error('confirmar_senha', 'As senhas não coincidem. Tente novamente.')
        return cleaned_data

    @transaction.atomic
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


class CadastroEtapa2Form(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['telefone', 'formacao', 'empresa', 'cargo', 'fotoPerfil', 'biografia']
        labels = LABELS_COMPLEMENTARES
        widgets = WIDGETS_COMPLEMENTARES

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False


class EditarPerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'telefone', 'dataNascimento', 'formacao', 'empresa', 'cargo', 'fotoPerfil', 'biografia']
        labels = {
            'nome': 'Nome Completo',
            'email': 'E-mail',
            'dataNascimento': 'Data de Nascimento',
            **LABELS_COMPLEMENTARES,
        }
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'dataNascimento': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
            **WIDGETS_COMPLEMENTARES,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        configurar_campo_data(self.fields['dataNascimento'])
        if self.instance and self.instance.pk and self.instance.dataNascimento:
            self.initial['dataNascimento'] = self.instance.dataNascimento.strftime('%Y-%m-%d')

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip().lower()
        qs_user = User.objects.filter(email__iexact=email)
        qs_usuario = Usuario.objects.filter(email__iexact=email)
        if self.instance and self.instance.pk:
            qs_user = qs_user.exclude(pk=self.instance.user_django_id)
            qs_usuario = qs_usuario.exclude(pk=self.instance.pk)
        if qs_user.exists() or qs_usuario.exists():
            raise forms.ValidationError('Este e-mail já está em uso por outro usuário.')
        return email

    def clean_dataNascimento(self):
        return validar_data_nascimento(self.cleaned_data.get('dataNascimento'))