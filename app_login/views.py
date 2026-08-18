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
from .models import Usuario

from .form import UsuarioForm, ParticipanteForm


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
    """View para cadastro de usuário"""
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.set_password(form.cleaned_data['password'])
            usuario.save()
            messages.success(request, 'Usuário cadastrado com sucesso!')
            return redirect('app_login:urllogin')
    else:
        form = UsuarioForm()
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

