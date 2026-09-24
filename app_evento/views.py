import json
import random
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.middleware.csrf import rotate_token

from .models import Evento, Atividade, Inscricao, Apoiador, Participa, StatusParticipa
from app_login.models import Usuario
from .form import EventoForm, AtividadeForm


# -----------------------------------------------
# VIEWS GERAIS E EVENTOS
# -----------------------------------------------
@never_cache
@ensure_csrf_cookie
def home(request):
    return render(request, 'app_evento/home.html')


@never_cache
@login_required
def cadastrar_evento(request):
    """View para cadastro de evento para o adm logado"""
    try:
        usuario_perfil = Usuario.objects.get(user_django=request.user)
    except Usuario.DoesNotExist:
        messages.warning(request, 'Você precisa completar seu perfil de Usuário antes de criar um evento.')
        return redirect('app_login:urlcad_usuario')
    
    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES)

        if form.is_valid():
            evento = form.save(commit=False)
            evento.administrador = usuario_perfil
            evento.save()
            
            nomes_apoiadores = form.cleaned_data.get('apoiadores')
            if nomes_apoiadores:
                objetos_apoiadores = []
                for nome in nomes_apoiadores:
                    apoiador_obj, criado = Apoiador.objects.get_or_create(nome=nome)
                    objetos_apoiadores.append(apoiador_obj)

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
def detalhes_evento(request, evento_id):
    """Exibe os detalhes de um evento e indica em quais atividades o usuário está inscrito"""
    evento = get_object_or_404(Evento, id=evento_id)
    atividades = Atividade.objects.filter(evento=evento)

    atividades_inscritas_ids = []
    
    if request.user.is_authenticated:
        usuario_perfil = getattr(request.user, 'user_django', None)
        if usuario_perfil:
            atividades_inscritas_ids = Participa.objects.filter(
                inscricao__usuario=usuario_perfil,
                atividade__evento=evento
            ).values_list('atividade_id', flat=True)

    context = {
        'evento': evento,
        'atividades': atividades,
        'atividades_inscritas_ids': list(atividades_inscritas_ids),
    }
    return render(request, 'app_evento/detalhes_evento.html', context)


def eventos_disponiveis(request):
    eventos = Evento.objects.all()
    
    if request.user.is_authenticated:
        try:
            usuario_perfil = Usuario.objects.get(user_django=request.user)
            eventos = eventos.exclude(administrador=usuario_perfil)
        except Usuario.DoesNotExist:
            pass
        
    form = EventoForm()
    
    context = {
        'eventos': eventos,
        'form_evento': form,
    }
    return render(request, 'app_evento/eventos.html', context)


@never_cache
@login_required
def detalhes_meus_evento(request, evento_id):
    """Exibe os detalhes de um evento e indica em quais atividades o usuário está inscrito"""
    try:
        usuario_perfil = Usuario.objects.get(user_django=request.user)
    except Usuario.DoesNotExist:
        raise PermissionDenied("Você precisa completar seu perfil de usuário para acessar esta página.")
    
    evento = get_object_or_404(Evento, id=evento_id, administrador=usuario_perfil)
    atividades = Atividade.objects.filter(evento=evento)

    total_inscritos = Participa.objects.filter(atividade__evento=evento).count()

    context = {
        'evento': evento,
        'atividades': atividades,
        'total_inscritos': total_inscritos,
    }
    return render(request, 'app_evento/detalhes_meus_evento.html', context)


@login_required
@never_cache
def meus_eventos_disponiveis(request):
    try:
        usuario_perfil = Usuario.objects.get(user_django=request.user)
        eventos_do_usuario = Evento.objects.filter(administrador=usuario_perfil)
    except Usuario.DoesNotExist:
        eventos_do_usuario = []
    
    context = {
        'eventos': eventos_do_usuario,
    }
    return render(request, 'app_evento/meus_eventos.html', context)


# -----------------------------------------------
# VIEWS DE ATIVIDADES E INSCRIÇÕES
# -----------------------------------------------
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
            'evento': evento_atual
        }

    return render(request, 'app_evento/cadastrar_atividade.html', context)


@never_cache
@login_required
def editar_atividade(request, atividade_id):
    atividade = get_object_or_404(Atividade, pk=atividade_id)
    evento = atividade.evento

    if request.method == 'POST':
        form = AtividadeForm(request.POST, instance=atividade)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Atividade "{atividade.nome}" atualizada com sucesso!')
            return redirect('app_evento:urldet_myevento', evento_id=evento.id)
    else:
        form = AtividadeForm(instance=atividade)

    context = {
        'form_atividade': form,
        'atividade': atividade,
        'evento': evento,
        'editando': True
    }
    return render(request, 'app_evento/cadastrar_atividade.html', context)


def excluir_atividade(request, atividade_id):
    atividade = get_object_or_404(Atividade, pk=atividade_id)
    evento_id = atividade.evento.id 
    if request.method == 'POST':
        atividade.delete()
        return redirect('app_evento:urldet_evento', evento_id=evento_id)
    return redirect('app_evento:urldet_evento', evento_id=evento_id)


@never_cache
@login_required
def alternar_participacao_atividade(request, atividade_id):
    """Inscreve ou cancela a inscrição do usuário na atividade informada"""
    atividade = get_object_or_404(Atividade, id=atividade_id)
    evento = atividade.evento

    try:
        usuario_perfil = Usuario.objects.get(user_django=request.user)
    except Usuario.DoesNotExist:
        messages.warning(request, 'Você precisa completar seu perfil antes de se inscrever em atividades.')
        return redirect('app_login:urlcad_usuario')

    # 1. Garante a existência da Inscrição no evento
    inscricao, _ = Inscricao.objects.get_or_create(
        usuario=usuario_perfil,
        evento=evento
    )

    # 2. Verifica se a participação já existe nesta atividade
    participacao = Participa.objects.filter(inscricao=inscricao, atividade=atividade).first()

    if participacao:
        participacao.delete()
        messages.warning(request, f'Você se desinscreveu da atividade "{atividade.nome}".')
        return redirect('app_evento:urldet_evento', evento_id=evento.id)

    # 3. Controle de limite de vagas
    if atividade.limitePessoas:
        total_inscritos = Participa.objects.filter(atividade=atividade).count()
        if total_inscritos >= atividade.limitePessoas:
            messages.error(request, f'A atividade "{atividade.nome}" está com as vagas esgotadas.')
            return redirect('app_evento:urldet_evento', evento_id=evento.id)

    # 4. Cria a participação
    Participa.objects.create(
        inscricao=inscricao,
        atividade=atividade,
        funcao=StatusParticipa.PARTICIPANTE
    )
    messages.success(request, f'Inscrição confirmada na atividade "{atividade.nome}"!')

    return redirect('app_evento:urlcomprovante_inscricao', evento_id=evento.id)


@login_required
def minhas_inscricoes(request):
    """Exibe todas as inscrições do usuário logado"""
    try:
        usuario = Usuario.objects.get(user_django=request.user)
    except Usuario.DoesNotExist:
        messages.warning(request, 'Você precisa completar seu perfil para visualizar suas inscrições.')
        return redirect('app_login:urlcad_usuario')

    inscricoes = Inscricao.objects.filter(usuario=usuario).select_related('evento').prefetch_related('participa_set__atividade')

    return render(request, 'app_evento/minhas_inscricoes.html', {
        'inscricoes': inscricoes
    })


# -----------------------------------------------
# OUTRAS VIEWS E SORTEIO
# -----------------------------------------------
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
def sorteio(request, atividade_id=None):
    if not atividade_id:
        messages.warning(request, "⚠️ Nenhuma atividade selecionada.")
        return redirect('app_evento:urldis_myevento')

    atividade = get_object_or_404(Atividade, id=atividade_id)
    
    # 1. BUSCA OS PARTICIPANTES DA ATIVIDADE
    # Traz todas as participações ligadas a esta atividade e otimiza a consulta (select_related)
    participacoes = Participa.objects.filter(
        atividade=atividade
    ).select_related('inscricao__usuario__user_django')

    # Extrai o nome completo (ou username) de cada inscrito
    lista_participantes = []
    for p in participacoes:
        if p.inscricao and p.inscricao.usuario and p.inscricao.usuario.user_django:
            user = p.inscricao.usuario.user_django
            # Usa o nome completo; se estiver em branco, usa o nome de usuário (username)
            nome = user.get_full_name().strip() or user.username
            lista_participantes.append(nome)

    # 2. GERENCIAMENTO DE PRÊMIOS DA SESSÃO POR ATIVIDADE
    session_key = f'premios_atividade_{atividade.id}'
    if session_key not in request.session:
        request.session[session_key] = []

    # Processa ações do modal (cadastrar, editar, remover, limpar)
    if request.method == 'POST':
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, '❌ Apenas administradores podem gerenciar prêmios.')
            return redirect('app_evento:urlsorteio_atividade', atividade_id=atividade.id)

        action = request.POST.get('action', 'add')
        premios = request.session.get(session_key, [])

        if action == 'add':
            premio_nome = request.POST.get('premio')
            qtd_ganhadores = request.POST.get('qtd_ganhadores', 1)
            if premio_nome:
                premios.append({
                    'nome': premio_nome,
                    'quantidade': int(qtd_ganhadores) if qtd_ganhadores else 1
                })
                messages.success(request, f'🎁 Prêmio "{premio_nome}" cadastrado!')

        elif action == 'edit':
            try:
                index = int(request.POST.get('premio_index'))
                nova_qtd = int(request.POST.get('nova_qtd', 1))
                if 0 <= index < len(premios) and nova_qtd > 0:
                    premios[index]['quantidade'] = nova_qtd
                    messages.success(request, '✏️ Quantidade alterada!')
            except (ValueError, TypeError):
                pass

        elif action == 'delete':
            try:
                index = int(request.POST.get('premio_index'))
                if 0 <= index < len(premios):
                    removido = premios.pop(index)
                    messages.success(request, f'🗑️ Prêmio "{removido["nome"]}" removido!')
            except (ValueError, TypeError):
                pass

        elif action == 'clear_all':
            premios = []
            messages.success(request, '🧹 Todos os prêmios desta atividade foram apagados!')

        request.session[session_key] = premios
        request.session.modified = True
        return redirect('app_evento:urlsorteio_atividade', atividade_id=atividade.id)

    premios = request.session.get(session_key, [])

    context = {
        'atividade': atividade,
        'premios': premios,
        'sorteio': random.choice(premios) if premios else {'nome': 'Nenhum prêmio cadastrado', 'quantidade': 1},
        'participantes_json': json.dumps(lista_participantes), # Passa os nomes em formato JSON para o JS
        'premios_json': json.dumps(premios),
    }

    return render(request, 'app_evento/sorteio.html', context)

@never_cache
@login_required
def comprovante_inscricao(request, evento_id):
    """Exibe o comprovante e o crachá do participante no evento"""
    try:
        usuario_perfil = Usuario.objects.get(user_django=request.user)
    except Usuario.DoesNotExist:
        messages.warning(request, 'Você precisa completar seu perfil de usuário.')
        return redirect('app_login:urlcad_usuario')

    evento = get_object_or_404(Evento, id=evento_id)
    inscricao = get_object_or_404(Inscricao, usuario=usuario_perfil, evento=evento)
    participacoes = Participa.objects.filter(inscricao=inscricao).select_related('atividade')

    context = {
        'evento': evento,
        'inscricao': inscricao,
        'participacoes': participacoes,
        'usuario': usuario_perfil,
    }
    return render(request, 'app_evento/inscricao.html', context)