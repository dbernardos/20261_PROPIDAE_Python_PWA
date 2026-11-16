from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

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
from .form import  EditarPerfilForm #, CadastroUsuarioForm,

from .form import CadastroEtapa1Form, CadastroEtapa2Form, EditarPerfilForm

# Views do LOGIN.
# -----------------------------------------------

def get_client_ip(request):
    """Obtém o IP do cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@never_cache
def cadastrar_usuario(request):
    if request.GET.get('deslogar'):
        logout(request)
        return redirect('app_login:urllogin')

    if request.method == 'POST':
        usuario_id = request.POST.get('usuario_id')

        # ==================== 1. ETAPA 1 (CRIAÇÃO + LOGIN) ====================
        if not usuario_id:
            form1 = CadastroEtapa1Form(request.POST)
            if form1.is_valid():
                usuario = form1.save()

                # Autentica o usuário recém-criado
                login(
                    request,
                    usuario.user_django,
                    backend='django.contrib.auth.backends.ModelBackend',
                )

                form2 = CadastroEtapa2Form(instance=usuario)
                return render(
                    request,
                    'app_login/cadastrar_usuario.html',
                    {'form': form2, 'etapa': 2, 'usuario_id': usuario.pk},
                )

            return render(
                request,
                'app_login/cadastrar_usuario.html',
                {'form': form1, 'etapa': 1},
            )

        # ==================== 2. ETAPA 2 (UPDATE DO PERFIL) ====================
        usuario = get_object_or_404(Usuario, pk=usuario_id)

        if 'pular' in request.POST:
            return redirect('app_evento:urldis_evento')

        form2 = CadastroEtapa2Form(request.POST, request.FILES, instance=usuario)
        if form2.is_valid():
            form2.save()
            return redirect('app_evento:urldis_evento')

        return render(
            request,
            'app_login/cadastrar_usuario.html',
            {'form': form2, 'etapa': 2, 'usuario_id': usuario.pk},
        )

    # ==================== 3. REQUISIÇÃO GET ====================
    # Se o usuário JÁ está logado e tenta voltar para o cadastro, permanece na tela de eventos
    if request.user.is_authenticated:
        return redirect('app_evento:urldis_evento')

    form1 = CadastroEtapa1Form()
    return render(
        request, 'app_login/cadastrar_usuario.html', {'form': form1, 'etapa': 1}
    )

@login_required
def meu_usuario(request):
    # Busca o perfil Usuario ligado ao login atual ou cria se não existir
    usuario, created = Usuario.objects.get_or_create(
        user_django=request.user,
        defaults={
            'nome': request.user.first_name or request.user.username,
            'email': request.user.email,
        }
    )

    form = EditarPerfilForm(instance=usuario)
    password_form = PasswordChangeForm(request.user)

    if request.method == 'POST':
        acao = request.POST.get('acao')

        if acao == 'alterar_senha':
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                
                # Mantém a sessão ativa após a troca de senha
                update_session_auth_hash(request, user)
                messages.success(request, 'Senha alterada com sucesso!')
                return redirect('app_login:urlmeu_usuario')
            else:
                messages.error(request, 'Não foi possível alterar a senha. Verifique os erros abaixo.')

        elif acao == 'excluir_conta':
            user = request.user
            logout(request)
            user.delete() 
            messages.success(request, 'Sua conta foi excluída permanentemente.')
            return redirect('app_login:urllogin') 

        else:
            # Edição de perfil (acao == 'editar_perfil' ou envio padrão do formulário)
            form = EditarPerfilForm(request.POST, request.FILES, instance=usuario)
            if form.is_valid():
              
                usuario_atualizado = form.save()

               
                request.user.email = usuario_atualizado.email
                request.user.first_name = usuario_atualizado.nome
                request.user.save()

                messages.success(request, 'Perfil atualizado com sucesso!')
                return redirect('app_login:urlmeu_usuario')
            else:
                messages.error(request, 'Não foi possível salvar. Verifique os erros no formulário.')

    return render(request, 'app_evento/meu_usuario.html', {
        'usuario': usuario,
        'form': form,
        'password_form': password_form,
    })
    
def resolver_username_login(identificador):
    identificador = (identificador or '').strip()
    if not identificador:
        return ''

    if '@' in identificador:
        user = User.objects.filter(email__iexact=identificador).first()
    else:
        user = User.objects.filter(username__iexact=identificador).first()

    return user.username if user else identificador