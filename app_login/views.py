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
from .form import  EditarPerfilForm #, CadastroUsuarioForm,

from .form import CadastroEtapa1Form, CadastroEtapa2Form, EditarPerfilForm

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
  # =========================================================================
  # 1. QUANDO O FORMULÁRIO É ENVIADO (MÉTODO POST)
  # =========================================================================
  if request.method == 'POST':
    etapa_enviada = request.POST.get('etapa')

    # --- PROCESSAMENTO DA ETAPA 2 (UPDATE) ---
    if etapa_enviada == '2' or 'pular' in request.POST:
      if 'pular' in request.POST:
        request.session.pop('novo_usuario_id', None)
        return redirect('app_evento:urldis_evento')  # Redireciona para sua home

      # Busca o perfil pelo ID da sessão ou pelo usuário autenticado
      usuario_id = request.session.get('novo_usuario_id')
      usuario = None

      if usuario_id:
        usuario = Usuario.objects.filter(pk=usuario_id).first()
      elif request.user.is_authenticated:
        usuario = getattr(request.user, 'participante', None) or getattr(
            request.user, 'user_django', None
        )

      if usuario:
        form2 = CadastroEtapa2Form(
            request.POST, request.FILES, instance=usuario
        )
        if form2.is_valid():
          form2.save()  # Executa apenas o UPDATE no banco
          request.session.pop('novo_usuario_id', None)  # Limpa a sessão
          return redirect('app_evento:urldis_evento')
        else:
          # Se houver algum erro de preenchimento na Etapa 2, mantém na Etapa 2
          return render(
              request,
              'app_login/cadastrar_usuario.html',
              {'form': form2, 'etapa': 2},
          )

    # --- PROCESSAMENTO DA ETAPA 1 (CREATE) ---
    form1 = CadastroEtapa1Form(request.POST)
    if form1.is_valid():
      usuario = form1.save()  # Grava User e Usuario no Banco

      # Autentica e loga o usuário definindo o backend explicitamente
      login(
          request,
          usuario.user_django,
          backend='django.contrib.auth.backends.ModelBackend',
      )

      # Guarda o ID na sessão para a Etapa 2 recuperar com segurança
      request.session['novo_usuario_id'] = usuario.pk

      # Prepara a Etapa 2 para renderizar no mesmo template
      form2 = CadastroEtapa2Form(instance=usuario)
      return render(
          request, 'app_login/cadastrar_usuario.html', {'form': form2, 'etapa': 2}
      )

    # Se a Etapa 1 tiver erros de validação
    return render(
        request, 'app_login/cadastrar_usuario.html', {'form': form1, 'etapa': 1}
    )

  # =========================================================================
  # 2. PRIMEIRO ACESSO À PÁGINA (MÉTODO GET)
  # =========================================================================
  if request.user.is_authenticated:
    # Se já estiver logado, exibe direto a Etapa 2 para completar o perfil
    usuario = getattr(request.user, 'participante', None) or getattr(
        request.user, 'user_django', None
    )
    form2 = CadastroEtapa2Form(instance=usuario)
    return render(
        request, 'app_login/cadastrar_usuario.html', {'form': form2, 'etapa': 2}
    )

  form1 = CadastroEtapa1Form()
  return render(request, 'app_login/cadastrar_usuario.html', {'form': form1, 'etapa': 1})
'''
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
'''
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

    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, request.FILES, instance=usuario)
        
        if form.is_valid():
            # 1. Salva as alterações no model Usuario no Banco de Dados
            usuario_atualizado = form.save()

            # 2. Sincroniza o E-mail e Nome também no User nativo do Django
            request.user.email = usuario_atualizado.email
            request.user.first_name = usuario_atualizado.nome
            request.user.save()

            messages.success(request, 'Perfil atualizado com sucesso no banco de dados!')
            return redirect('app_login:urlmeu_usuario') # Ajuste com o seu name da URL
        else:
            # Alerta se houver erro de validação
            messages.error(request, 'Não foi possível salvar. Verifique os erros no formulário.')
    else:
        form = EditarPerfilForm(instance=usuario)

    return render(request, 'app_evento/meu_usuario.html', {
        'usuario': usuario,
        'form': form
    })