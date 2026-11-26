from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache

from .form import CadastroEtapa1Form, CadastroEtapa2Form, EditarPerfilForm
from .models import Usuario


@never_cache
def cadastrar_usuario(request):
    if request.GET.get('deslogar'):
        logout(request)
        return redirect('app_login:urllogin')

    if request.method == 'POST':
        etapa = request.POST.get('etapa', '1')

        # Etapa 1: criação da conta + login
        if etapa == '1':
            form1 = CadastroEtapa1Form(request.POST)
            if form1.is_valid():
                usuario = form1.save()
                login(
                    request,
                    usuario.user_django,
                    backend='django.contrib.auth.backends.ModelBackend',
                )
                return render(request, 'app_login/cadastrar_usuario.html', {
                    'form': CadastroEtapa2Form(instance=usuario),
                    'etapa': 2,
                })
            return render(request, 'app_login/cadastrar_usuario.html', {
                'form': form1,
                'etapa': 1,
            })

        # Etapa 2: atualização opcional do próprio usuário autenticado
        if not request.user.is_authenticated:
            return redirect('app_login:urllogin')

        if 'pular' in request.POST:
            return redirect('app_evento:urldis_evento')

        usuario = get_object_or_404(Usuario, user_django=request.user)
        form2 = CadastroEtapa2Form(request.POST, request.FILES, instance=usuario)
        if form2.is_valid():
            form2.save()
            return redirect('app_evento:urldis_evento')

        return render(request, 'app_login/cadastrar_usuario.html', {
            'form': form2,
            'etapa': 2,
        })

    if request.user.is_authenticated:
        return redirect('app_evento:urldis_evento')

    return render(request, 'app_login/cadastrar_usuario.html', {
        'form': CadastroEtapa1Form(),
        'etapa': 1,
    })


@login_required
def meu_usuario(request):
    usuario = getattr(request.user, 'participante', None)
    if not usuario:
        messages.warning(request, 'Seu usuário ainda não possui perfil cadastrado.')
        return redirect('app_evento:urldis_evento')

    form = EditarPerfilForm(instance=usuario)
    password_form = PasswordChangeForm(request.user)

    if request.method == 'POST':
        acao = request.POST.get('acao')

        if acao == 'alterar_senha':
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Senha alterada com sucesso!')
                return redirect('app_login:urlmeu_usuario')
            messages.error(request, 'Não foi possível alterar a senha. Verifique os erros abaixo.')

        elif acao == 'excluir_conta':
            user = request.user
            logout(request)
            user.delete()
            messages.success(request, 'Sua conta foi excluída permanentemente.')
            return redirect('app_login:urllogin')

        else:
            form = EditarPerfilForm(request.POST, request.FILES, instance=usuario)
            if form.is_valid():
                usuario_atualizado = form.save()
                request.user.email = usuario_atualizado.email
                request.user.first_name = usuario_atualizado.nome
                request.user.save(update_fields=['email', 'first_name'])
                messages.success(request, 'Perfil atualizado com sucesso!')
                return redirect('app_login:urlmeu_usuario')
            messages.error(request, 'Não foi possível salvar. Verifique os erros no formulário.')

    password_form.fields['old_password'].widget.attrs.pop('autofocus', None)

    return render(request, 'app_evento/meu_usuario.html', {
        'usuario': usuario,
        'form': form,
        'password_form': password_form,
    })
