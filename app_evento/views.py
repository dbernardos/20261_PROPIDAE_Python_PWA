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

from .models import Evento, Atividade, Inscricao
from .form import EventoForm, AtividadeForm

# reate your EVENTO views here.
# -----------------------------------------------
@never_cache
@login_required(login_url='login')
def cadastrar_evento(request):
    """View para cadastro de evento para o adm logado"""
    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES)

        if form.is_valid():
            evento = form.save(commit=False)
            evento.administrador = request.user
            evento.save()
            messages.success(request, '🎉 Evento cadastrado com sucesso!')
            return redirect('cadastrar_atividade', evento_id=evento.id)  # Redireciona para a página de cadastro de atividade
    else:
        form = EventoForm()

    context = {
            'form_evento': form,
    }
    return render(request, 'cadastrar_evento.html', {'form_evento': form})

@never_cache
@login_required(login_url='login')
def excluir_evento(request, evento_id):
    """View para excluir um evento cadastrado"""
    evento = get_object_or_404(Evento, id=evento_id)
    if request.method == 'POST':
        evento.delete()
        messages.success(request, '🗑️ Evento excluído com sucesso!')
    return redirect('cadastrar_evento')

@never_cache
def detalhes_evento(request, evento_id):
    """Exibe os detalhes de um evento e a lista de suas atividades cadastradas"""
    evento = get_object_or_404(Evento, id=evento_id)
    atividades = Atividade.objects.filter(evento=evento)

    context = {
        'evento': evento,
        'atividades': atividades,
    }
    return render(request, 'detalhes_evento.html', context)

@never_cache
@login_required(login_url='login')
def cadastrar_atividade(request, evento_id):
    evento_atual = get_object_or_404(Evento, id=evento_id)
    if request.method == 'POST':
        form = AtividadeForm(request.POST)

        if form.is_valid():

            atividade = form.save(commit=False)
            
            #evento_atual = Evento.objects.first() 
            atividade.evento = evento_atual
            
            atividade.save()
            
            messages.success(request, '🎉 Atividade cadastrada com sucesso!')
            return redirect('dados') 
            
    else:
        form = AtividadeForm()

    return render(request, 'cadastrar_atividade.html', {'form_atividade': form})


@never_cache
def dados(request):
    template = 'dados.html'
    eventos = Evento.objects.all()
    atividades = Atividade.objects.all()
    contexto = {
        'eventos': eventos,
        'atividades': atividades,
    }
    return render(request, template, contexto)