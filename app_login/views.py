from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib import messages

from django.utils import timezone
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import rotate_token
from django.views.decorators.csrf import ensure_csrf_cookie

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Usuario

from .form import UsuarioForm, ParticipanteForm
from .form import CadastroUsuarioForm


# Create your LOGIN views here.
# -----------------------------------------------
def get_client_ip(request):
    """Obtém o IP do cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def cadastrar_usuario(request):
    if request.method == 'POST':
        # request.FILES é necessário por causa da fotoPerfil (ImageField)
        form = CadastroUsuarioForm(request.POST, request.FILES)
        
        if form.is_valid():
            # 1. Pegamos os dados validados
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            senha = form.cleaned_data['senha']
            #cpf = form.cleaned_data['cpf'] # Usaremos o CPF como 'username' do Django
            
            # 2. Criamos o User padrão de autenticação do Django
            user = User.objects.create_user(
                username=username, # O Django exige um username. Usar o CPF ou E-mail é uma boa tática
                email=email,
                password=senha
            )
            
            # 3. Criamos o model 'Usuario' sem salvar no banco ainda (commit=False)
            usuario_perfil = form.save(commit=False)
            
            # 4. Vinculamos o User do Django ao campo 'participante'
            usuario_perfil.user_django = user
            
            # 5. Salva o perfil no banco de dados
            usuario_perfil.save()
            
            messages.success(request, 'Cadastro realizado com sucesso! Faça seu login.')
            return redirect('app_login:urllogin')
    else:
        form = CadastroUsuarioForm()

    return render(request, 'app_login/cadastrar_usuario.html', {'form': form})

def login_participante(request):
    """Página de login/cadastro pelo crachá"""
    if request.method == 'POST':
        form = ParticipanteForm(request.POST)
        if form.is_valid():
            cracha = form.cleaned_data['cracha']
            
            # Tenta encontrar participante existente ou cria novo
            participante, created = Usuario.objects.get_or_create(
                defaults={
                    'nome': form.cleaned_data.get('nome'),
                    'email': form.cleaned_data.get('email')
                }
            )
            
            # Atualiza informações se já existir
            if not created:
                if form.cleaned_data.get('nome'):
                    participante.nome = form.cleaned_data.get('nome')
                if form.cleaned_data.get('email'):
                    participante.email = form.cleaned_data.get('email')
                participante.save()
            
            # Atualiza último acesso
            participante.ultimo_acesso = timezone.now()
            participante.save()
            
            # Redireciona para página de boas-vindas
            return redirect('boas_vindas', cracha=participante.nome)
    else:
        form = ParticipanteForm()
    
    return render(request, 'quiz/login_participante.html', {'form': form})

