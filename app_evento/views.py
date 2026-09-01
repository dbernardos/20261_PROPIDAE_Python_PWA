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

from .models import Evento, Atividade, Inscricao, Apoiador
from .form import EventoForm, AtividadeForm

# create your EVENTO views here.
# -----------------------------------------------
@never_cache
@ensure_csrf_cookie
def home(request):
    return render(request, 'app_evento/home.html')

@never_cache
@login_required
def cadastrar_evento(request):
    """View para cadastro de evento para o adm logado"""
    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES)

        if form.is_valid():
            evento = form.save(commit=False)
            evento.administrador = request.user
            evento.save()
            
            # processamento do campo de apoiadores(separado por virgulas)
            nomes_apoiadores = form.cleaned_data.get('apoiadores')
            if nomes_apoiadores:
                objetos_apoiadores = []
                for nome in nomes_apoiadores:
                    # Busca o apoiador pelo nome, cria um novo se não existir
                    apoiador_obj, criado = Apoiador.objects.get_or_create(nome=nome)
                    objetos_apoiadores.append(apoiador_obj)

                # Vincula a lista de objetos ao relacionamento ManyToMany do evento
                evento.apoiadores.set(objetos_apoiadores)
                
            messages.success(request, 'Evento cadastrado com sucesso!')
            return redirect('app_evento:urlcad_atividade', evento_id=evento.id)
    else:
        form = EventoForm()

    return render(request, 'app_evento/cadastrar_evento.html', {'form_evento': form})

@never_cache
@login_required
def editar_evento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    
    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES, instance=evento)
        if form.is_valid():
            evento = form.save()
            
            nomes_apoiadores = form.cleaned_data.get('apoiadores')
            if nomes_apoiadores:
                objetos_apoiadores = [Apoiador.objects.get_or_create(nome=nome)[0] for nome in nomes_apoiadores]
                evento.apoiadores.set(objetos_apoiadores)
            else:
                evento.apoiadores.clear()
            
            messages.success(request, '✅ Evento atualizado com sucesso!')
            return redirect('app_evento:urldis_evento')
    else:
        form = EventoForm(instance=evento)
        messages.info(request, f'✏️ Edite as informações do evento "{evento.nome}" abaixo:')

    return render(request, 'app_evento/cadastrar_evento.html', {
        'form_evento': form, 
        'evento': evento,
        'editando': True
    })

@never_cache
@login_required
def excluir_evento(request, evento_id):
    """View para excluir um evento cadastrado"""
    evento = get_object_or_404(Evento, id=evento_id)
    if request.method == 'POST':
        evento.delete()
        messages.success(request, '🗑️ Evento excluído com sucesso!')
    return redirect('app_evento:urlcad_evento')


@never_cache
@login_required
def detalhes_evento(request, evento_id):
    """Exibe os detalhes de um evento e a lista de suas atividades cadastradas"""
    evento = get_object_or_404(Evento, id=evento_id)
    atividades = Atividade.objects.filter(evento=evento)

    context = {
        'evento': evento,
        'atividades': atividades,
    }
    return render(request, 'app_evento/detalhes_evento.html', context)

@never_cache
@login_required
def cadastrar_atividade(request, evento_id):
    evento_atual = get_object_or_404(Evento, id=evento_id)
    if request.method == 'POST':
        form = AtividadeForm(request.POST)

        if form.is_valid():
            atividade = form.save(commit=False)
            atividade.evento = evento_atual
            atividade.save()
            
            messages.success(request, '🎉 Atividade cadastrada com sucesso!')
            return redirect('app_evento:urldados') 
    else:
        form = AtividadeForm()
        context = {
            'form_atividade': form,
            'evento': evento_atual  # Passando o objeto evento para o HTML
        }

    return render(request, 'app_evento/cadastrar_atividade.html', context)

def editar_atividade(request, atividade_id):
    atividade = get_object_or_404(Atividade, pk=atividade_id)
    return render(request, 'app_evento/form_atividade.html', {'atividade': atividade})

def excluir_atividade(request, atividade_id):
    atividade = get_object_or_404(Atividade, pk=atividade_id)
    evento_id = atividade.evento.id 
    if request.method == 'POST':
        atividade.delete()
        return redirect('app_evento:urldetalhes_evento', evento_id=evento_id)
    return redirect('app_evento:urldetalhes_evento', evento_id=evento_id)


@never_cache
def dados(request):
    template = 'app_evento/dados.html'
    eventos = Evento.objects.all()
    atividades = Atividade.objects.all()
    contexto = {
        'eventos': eventos,
        'atividades': atividades,
    }
    return render(request, template, contexto)

@never_cache
@login_required
def minhas_inscricoes(request):
    inscricoes = (
        Inscricao.objects.filter(usuario=request.user)
        .select_related('evento')
        .order_by('-dataHora')
    )

    return render(
        request, 'app_evento/minhas_inscricoes.html', {'inscricoes': inscricoes}
    )

def eventos_disponiveis(request):
    eventos = Evento.objects.all()
    form = EventoForm()  # Instancia o formulário
    
    context = {
        'eventos': eventos,
        'form_evento': form,  # Passa o form esperado pelo template
    }
    return render(request, 'app_evento/eventos.html', context)

@never_cache
@login_required
def sorteio(request):
    # Inicializa a lista de prêmios na sessão se não existir
    if 'premios_lista' not in request.session:
        request.session['premios_lista'] = []

    if request.method == 'POST':
        premio_nome = request.POST.get('premio')
        qtd_ganhadores = request.POST.get('qtd_ganhadores', 1)

        if premio_nome:
            # Recupera a lista atual e adiciona o novo prêmio
            premios = request.session['premios_lista']
            premios.append({
                'nome': premio_nome,
                'quantidade': int(qtd_ganhadores) if qtd_ganhadores else 1,
                'sorteado': False
            })
            
            # Atualiza e marca a sessão como modificada
            request.session['premios_lista'] = premios
            request.session.modified = True

            messages.success(request, f'Prêmio "{premio_nome}" cadastrado com sucesso!')

        return redirect('app_evento:urlsorteio')

    # Carrega a lista cadastrada
    premios = request.session.get('premios_lista', [])
    
    # Define o último prêmio cadastrado como o ativo para a tela inicial
    ultimo_premio = premios[-1] if premios else {'nome': 'Nenhum prêmio cadastrado', 'quantidade': 1}

    context = {
        'premios': premios,
        'sorteio': ultimo_premio,
    }

    return render(request, 'app_evento/sorteio.html', context)