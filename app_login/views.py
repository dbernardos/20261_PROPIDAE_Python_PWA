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
#from .form import ParticipanteForm, RespostaQuizForm, EventoForm, AtividadeForm

from .form import UsuarioForm


# reate your views here.
# -----------------------------------------------
def get_client_ip(request):
    """Obtém o IP do cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

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

def boas_vindas(request, cracha):
    """Página de boas-vindas com quadro de progresso"""
    participante = get_object_or_404(Usuario, nome=cracha)
    
    # Obtém todos os quizzes ativos
    quizzes = Quiz.objects.filter(ativo=True)
    
    # Calcula progresso para cada quiz
    progresso_quizzes = []
    for quiz in quizzes:
        resposta = Resposta.objects.filter(
            participante=participante, 
            quiz=quiz
        ).first()
        
        progresso_quizzes.append({
            'quiz': quiz,
            'resposta': resposta,
            #'completo': resposta.completo if resposta else False,
            #'tentativas': resposta.tentativas if resposta else 0
        })
    
    # Progresso geral
    progresso_geral = participante.get_progresso_geral()
    
    context = {
        'participante': participante,
        'progresso_quizzes': progresso_quizzes,
        'progresso_geral': progresso_geral,
        'quizzes_completos': progresso_geral['respondidos'],
        'total_quizzes': progresso_geral['total'],
        'porcentagem_conclusao': progresso_geral['porcentagem']
    }
    
    return render(request, 'quiz/boas_vindas.html', context)