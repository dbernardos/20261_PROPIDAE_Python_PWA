import json
import random
from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.middleware.csrf import rotate_token
from django.db.models import Q
import re

from .models import (
    Evento,
    Atividade,
    Inscricao,
    Apoiador,
    Participa,
    StatusParticipa,
    tipoEvento,
)
from app_login.models import Usuario
from .form import EventoForm, AtividadeForm



# ==========================================================
# FUNÇÕES AUXILIARES
# ==========================================================
def home_root(request):

    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    padrao_mobile = r'android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini'
    is_mobile = bool(re.search(padrao_mobile, user_agent))

    if is_mobile:
        return redirect('app_evento:pwa_home')
    else:
        return redirect('app_login:urllogin')

def busca_evento_pwa(request):
    """Tela inicial do PWA para buscar evento pelo código."""
    if request.method == 'POST':
        codigo = request.POST.get('codigo_evento')
        
        try:
            evento = Evento.objects.get(codigo_evento=codigo)
           
            return redirect('app_evento:pwa_atividades_evento', evento_id=evento.id)
        except Evento.DoesNotExist:
            messages.error(request, "Evento não encontrado. Verifique o código.")
            
    return render(request, 'app_evento/pwa_home.html')

def filtrar_eventos_por_parametros(eventos, request):
    """
    Aplica os filtros de busca, tipo, período e encerramento
    a um queryset de eventos.
    """

    hoje = timezone.localdate()

    query_busca = request.GET.get('busca', '').strip()
    query_tipo = request.GET.get('tipo', '').strip()
    query_periodo = request.GET.get('periodo', '').strip()
    query_data_inicio = request.GET.get('data_inicio', '').strip()
    query_data_fim = request.GET.get('data_fim', '').strip()
    query_apenas_encerrados = request.GET.get('encerrados') == '1'

    # Busca pelo nome ou pela descrição.
    if query_busca:
        eventos = eventos.filter(
            Q(nome__icontains=query_busca)
            | Q(descricao__icontains=query_busca)
        )

    # Aceita somente os tipos definidos no modelo.
    tipos_validos = {
        valor for valor, rotulo in tipoEvento.choices
    }

    if query_tipo in tipos_validos:
        eventos = eventos.filter(tipoEvento=query_tipo)

    # Eventos encerrados ou eventos atuais/futuros.
    if query_apenas_encerrados:
        eventos = eventos.filter(dataFim__lt=hoje)
    elif not (
        query_periodo
        or query_data_inicio
        or query_data_fim
    ):
        eventos = eventos.filter(dataFim__gte=hoje)

    # Filtros por períodos predefinidos.
    if query_periodo == 'hoje':
        eventos = eventos.filter(
            dataInicio__lte=hoje,
            dataFim__gte=hoje,
        )

    elif query_periodo == 'amanha':
        amanha = hoje + timedelta(days=1)

        eventos = eventos.filter(
            dataInicio__lte=amanha,
            dataFim__gte=amanha,
        )

    elif query_periodo == 'fim_semana':
        # Encontra o próximo sábado, considerando o dia atual.
        dias_ate_sabado = (5 - hoje.weekday()) % 7
        sabado = hoje + timedelta(days=dias_ate_sabado)
        domingo = sabado + timedelta(days=1)

        eventos = eventos.filter(
            dataInicio__lte=domingo,
            dataFim__gte=sabado,
        )

    elif query_periodo == '7_dias':
        limite = hoje + timedelta(days=7)

        eventos = eventos.filter(
            dataInicio__lte=limite,
            dataFim__gte=hoje,
        )

    elif query_periodo == '30_dias':
        limite = hoje + timedelta(days=30)

        eventos = eventos.filter(
            dataInicio__lte=limite,
            dataFim__gte=hoje,
        )

    elif query_periodo == 'custom':
        # O evento precisa coincidir com o intervalo informado.
        if query_data_inicio:
            eventos = eventos.filter(
                dataFim__gte=query_data_inicio
            )

        if query_data_fim:
            eventos = eventos.filter(
                dataInicio__lte=query_data_fim
            )

    return eventos, {
        'busca_atual': query_busca,
        'tipo_atual': query_tipo,
        'encerrados_atual': query_apenas_encerrados,
        'periodo_atual': query_periodo,
        'data_inicio_atual': query_data_inicio,
        'data_fim_atual': query_data_fim,
    }


# ==========================================================
# VIEWS GERAIS E EVENTOS
# ==========================================================

@never_cache
@ensure_csrf_cookie
def home(request):
    return render(request, 'app_evento/home.html')


@never_cache
def eventos_disponiveis(request):
    """Exibe os eventos públicos disponíveis no catálogo."""

    eventos = Evento.objects.filter(
        eventoPublico=True
    ).exclude(
        dataFim__isnull=True
    ).order_by('dataInicio')

    # Não exibe os próprios eventos do usuário no catálogo público.
    if request.user.is_authenticated:
        eventos = eventos.exclude(
            administrador__user_django=request.user
        )

    eventos, filtros = filtrar_eventos_por_parametros(
        eventos,
        request,
    )

    context = {
        'eventos': eventos,
        'tipos_evento': tipoEvento.choices,
        **filtros,
    }

    return render(
        request,
        'app_evento/eventos.html',
        context,
    )


@never_cache
@login_required
def cadastrar_evento(request):
    """Cadastra um evento para o administrador autenticado."""

    try:
        usuario_perfil = Usuario.objects.get(
            user_django=request.user
        )
    except Usuario.DoesNotExist:
        messages.warning(
            request,
            'Você precisa completar seu perfil de Usuário antes de criar um evento.',
        )
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
                    apoiador_obj, criado = Apoiador.objects.get_or_create(
                        nome=nome
                    )
                    objetos_apoiadores.append(apoiador_obj)

                evento.apoiadores.set(objetos_apoiadores)

            messages.success(
                request,
                'Evento cadastrado com sucesso!',
            )

            return redirect(
                'app_evento:urlcad_atividade',
                evento_id=evento.id,
            )
    else:
        form = EventoForm()

    return render(
        request,
        'app_evento/cadastrar_evento.html',
        {'form_evento': form},
    )


@never_cache
@login_required
def editar_evento(request, evento_id):
    """Edita um evento existente."""

    evento = get_object_or_404(
        Evento,
        id=evento_id,
    )

    if request.method == 'POST':
        form = EventoForm(
            request.POST,
            request.FILES,
            instance=evento,
        )

        if form.is_valid():
            evento = form.save()

            nomes_apoiadores = form.cleaned_data.get('apoiadores')

            if nomes_apoiadores:
                objetos_apoiadores = [
                    Apoiador.objects.get_or_create(nome=nome)[0]
                    for nome in nomes_apoiadores
                ]
                evento.apoiadores.set(objetos_apoiadores)
            else:
                evento.apoiadores.clear()

            messages.success(
                request,
                'Evento atualizado com sucesso!',
            )

            return redirect(
                'app_evento:urldet_myevento',
                evento_id=evento.id,
            )
    else:
        form = EventoForm(instance=evento)

        messages.info(
            request,
            f'Edite as informações do evento "{evento.nome}" abaixo:',
        )

    return render(
        request,
        'app_evento/cadastrar_evento.html',
        {
            'form_evento': form,
            'evento': evento,
            'editando': True,
        },
    )


@never_cache
@login_required
def excluir_evento(request, evento_id):
    """Exclui um evento após uma solicitação POST."""

    evento = get_object_or_404(
        Evento,
        id=evento_id,
    )

    if request.method == 'POST':
        evento.delete()

        messages.success(
            request,
            'Evento excluído com sucesso!',
        )

    return redirect('app_evento:urldis_myevento')


@never_cache
def detalhes_evento(request, evento_id):
    """
    Exibe os detalhes de um evento e identifica as atividades
    nas quais o usuário está inscrito.
    """

    evento = get_object_or_404(
        Evento,
        id=evento_id,
    )

    atividades = Atividade.objects.filter(
        evento=evento
    ).order_by('horaInicio')

    atividades_inscritas_ids = []
    esta_inscrito_no_evento = False

    if request.user.is_authenticated:
        usuario_perfil = getattr(
            request.user,
            'user_django',
            None,
        )

        if not usuario_perfil:
            try:
                usuario_perfil = Usuario.objects.get(
                    user_django=request.user
                )
            except Usuario.DoesNotExist:
                usuario_perfil = None

        if usuario_perfil:
            esta_inscrito_no_evento = Inscricao.objects.filter(
                usuario=usuario_perfil,
                evento=evento,
                ativa=True,
            ).exists()

            atividades_inscritas_ids = Participa.objects.filter(
                inscricao__usuario=usuario_perfil,
                inscricao__ativa=True,
                atividade__evento=evento,
            ).values_list(
                'atividade_id',
                flat=True,
            )

    context = {
        'evento': evento,
        'atividades': atividades,
        'atividades_inscritas_ids': list(
            atividades_inscritas_ids
        ),
        'esta_inscrito_no_evento': esta_inscrito_no_evento,
    }

    return render(
        request,
        'app_evento/detalhes_evento.html',
        context,
    )


@never_cache
@login_required
def detalhes_meus_evento(request, evento_id):
    """Exibe os detalhes de um evento administrado pelo usuário."""

    try:
        usuario_perfil = Usuario.objects.get(
            user_django=request.user
        )
    except Usuario.DoesNotExist:
        raise PermissionDenied(
            'Você precisa completar seu perfil de usuário para acessar esta página.'
        )

    evento = get_object_or_404(
        Evento,
        id=evento_id,
        administrador=usuario_perfil,
    )

    atividades = Atividade.objects.filter(
        evento=evento
    ).order_by('horaInicio')

    total_inscritos = Participa.objects.filter(
        atividade__evento=evento
    ).count()

    context = {
        'evento': evento,
        'atividades': atividades,
        'total_inscritos': total_inscritos,
    }

    return render(
        request,
        'app_evento/detalhes_meus_evento.html',
        context,
    )


@login_required
@never_cache
def meus_eventos_disponiveis(request):
    """Exibe e filtra os eventos administrados pelo usuário."""

    try:
        usuario_perfil = Usuario.objects.get(
            user_django=request.user
        )

        eventos_do_usuario = Evento.objects.filter(
            administrador=usuario_perfil
        ).order_by('dataInicio')

    except Usuario.DoesNotExist:
        eventos_do_usuario = Evento.objects.none()

    eventos_do_usuario, filtros = filtrar_eventos_por_parametros(
        eventos_do_usuario,
        request,
    )

    context = {
        'eventos': eventos_do_usuario,
        'tipos_evento': tipoEvento.choices,
        **filtros,
    }

    return render(
        request,
        'app_evento/meus_eventos.html',
        context,
    )


# ==========================================================
# VIEWS DE ATIVIDADES E INSCRIÇÕES
# ==========================================================

@never_cache
@login_required
def cadastrar_atividade(request, evento_id):
    """Cadastra uma atividade vinculada a um evento."""

    evento_atual = get_object_or_404(
        Evento,
        id=evento_id,
    )

    if request.method == 'POST':
        form = AtividadeForm(request.POST)

        if form.is_valid():
            atividade = form.save(commit=False)
            atividade.evento = evento_atual
            atividade.save()

            messages.success(
                request,
                'Atividade cadastrada com sucesso!',
            )

            return redirect(
                'app_evento:urldet_myevento',
                evento_id=evento_atual.id,
            )

        messages.error(
            request,
            'Por favor, corrija os erros destacados no formulário.',
        )
    else:
        form = AtividadeForm()

    context = {
        'form_atividade': form,
        'evento': evento_atual,
    }

    return render(
        request,
        'app_evento/cadastrar_atividade.html',
        context,
    )


@never_cache
@login_required
def editar_atividade(request, atividade_id):
    """Edita uma atividade existente."""

    atividade = get_object_or_404(
        Atividade,
        pk=atividade_id,
    )

    evento = atividade.evento

    if request.method == 'POST':
        form = AtividadeForm(
            request.POST,
            instance=atividade,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                f'Atividade "{atividade.nome}" atualizada com sucesso!',
            )

            return redirect(
                'app_evento:urldet_myevento',
                evento_id=evento.id,
            )
    else:
        form = AtividadeForm(instance=atividade)

    context = {
        'form_atividade': form,
        'atividade': atividade,
        'evento': evento,
        'editando': True,
    }

    return render(
        request,
        'app_evento/cadastrar_atividade.html',
        context,
    )


@login_required
def excluir_atividade(request, atividade_id):
    """Exclui uma atividade mediante solicitação POST."""

    atividade = get_object_or_404(
        Atividade,
        pk=atividade_id,
    )

    evento_id = atividade.evento.id

    if request.method == 'POST':
        atividade.delete()

    return redirect(
        'app_evento:urldet_myevento',
        evento_id=evento_id,
    )


@never_cache
@login_required
def alternar_participacao_atividade(request, atividade_id):
    """Inscreve ou cancela a inscrição do usuário em uma atividade."""

    atividade = get_object_or_404(
        Atividade,
        id=atividade_id,
    )

    evento = atividade.evento

    try:
        usuario_perfil = Usuario.objects.get(
            user_django=request.user
        )
    except Usuario.DoesNotExist:
        messages.warning(
            request,
            'Você precisa completar seu perfil antes de se inscrever em atividades.',
        )
        return redirect('app_login:urlcad_usuario')

    inscricao, _ = Inscricao.objects.get_or_create(
        usuario=usuario_perfil,
        evento=evento,
    )

    participacao = Participa.objects.filter(
        inscricao=inscricao,
        atividade=atividade,
    ).first()

    # Se já participa, remove a participação.
    if participacao:
        participacao.delete()

        atividades_restantes = Participa.objects.filter(
            inscricao=inscricao,
        ).count()

        if atividades_restantes == 0:
            inscricao.ativa = False
            inscricao.save()

            messages.warning(
                request,
                f'Sua inscrição no evento "{evento.nome}" foi desativada porque você removeu todas as atividades.',
            )
        else:
            messages.warning(
                request,
                f'Você se desinscreveu da atividade "{atividade.nome}".',
            )

        return redirect(
            'app_evento:urldet_evento',
            evento_id=evento.id,
        )

    # Verifica se ainda existem vagas.
    if atividade.limitePessoas:
        total_inscritos = Participa.objects.filter(
            atividade=atividade,
        ).count()

        if total_inscritos >= atividade.limitePessoas:
            messages.error(
                request,
                f'A atividade "{atividade.nome}" está com as vagas esgotadas.',
            )

            return redirect(
                'app_evento:urldet_evento',
                evento_id=evento.id,
            )

    # Reativa a inscrição se estava desativada.
    if not inscricao.ativa:
        inscricao.ativa = True
        inscricao.save()

    Participa.objects.create(
        inscricao=inscricao,
        atividade=atividade,
        funcao=StatusParticipa.PARTICIPANTE,
    )

    messages.success(
        request,
        f'Inscrição confirmada na atividade "{atividade.nome}"!',
    )

    return redirect(
        'app_evento:urlcomprovante_inscricao',
        evento_id=evento.id,
    )


@login_required
def minhas_inscricoes(request):
    """Exibe todas as inscrições ativas do usuário autenticado."""

    try:
        usuario = Usuario.objects.get(
            user_django=request.user
        )
    except Usuario.DoesNotExist:
        messages.warning(
            request,
            'Você precisa completar seu perfil para visualizar suas inscrições.',
        )
        return redirect('app_login:urlcad_usuario')

    inscricoes = Inscricao.objects.filter(
        usuario=usuario,
        ativa=True,
    ).select_related(
        'evento',
    ).prefetch_related(
        'participa_set__atividade',
    )

    # Regenera os dados da inscrição caso o arquivo do QR Code não exista.
    for inscricao in inscricoes:
        if inscricao.qrcode_imagem:
            if not inscricao.qrcode_imagem.storage.exists(
                inscricao.qrcode_imagem.name
            ):
                inscricao.save()

    total_atividades = sum(
        len(inscricao.participa_set.all())
        for inscricao in inscricoes
    )

    return render(
        request,
        'app_evento/minhas_inscricoes.html',
        {
            'inscricoes': inscricoes,
            'total_atividades': total_atividades,
        },
    )


@never_cache
@login_required
def comprovante_inscricao(request, evento_id):
    """Exibe o comprovante e o crachá do participante."""

    try:
        usuario_perfil = Usuario.objects.get(
            user_django=request.user
        )
    except Usuario.DoesNotExist:
        messages.warning(
            request,
            'Você precisa completar seu perfil de usuário.',
        )
        return redirect('app_login:urlcad_usuario')

    evento = get_object_or_404(
        Evento,
        id=evento_id,
    )

    inscricao = get_object_or_404(
        Inscricao,
        usuario=usuario_perfil,
        evento=evento,
    )

    participacoes = Participa.objects.filter(
        inscricao=inscricao,
    ).select_related(
        'atividade',
    )

    context = {
        'evento': evento,
        'inscricao': inscricao,
        'participacoes': participacoes,
        'usuario': usuario_perfil,
    }

    return render(
        request,
        'app_evento/comprovante.html',
        context,
    )


# ==========================================================
# OUTRAS VIEWS E SORTEIO
# ==========================================================

@never_cache
@login_required
def sorteio(request, atividade_id=None):
    """Gerencia os prêmios e os participantes de uma atividade."""

    if not atividade_id:
        messages.warning(
            request,
            'Nenhuma atividade selecionada.',
        )
        return redirect('app_evento:urldis_myevento')

    atividade = get_object_or_404(
        Atividade,
        id=atividade_id,
    )

    participacoes = Participa.objects.filter(
        atividade=atividade,
    ).select_related(
        'inscricao__usuario__user_django',
    )

    lista_participantes = []

    for participacao in participacoes:
        if (
            participacao.inscricao
            and participacao.inscricao.usuario
            and participacao.inscricao.usuario.user_django
        ):
            user = participacao.inscricao.usuario.user_django
            nome = user.get_full_name().strip() or user.username
            lista_participantes.append(nome)

    session_key = f'premios_atividade_{atividade.id}'

    if session_key not in request.session:
        request.session[session_key] = []

    if request.method == 'POST':
        if not (
            request.user.is_staff
            or request.user.is_superuser
        ):
            messages.error(
                request,
                'Apenas administradores podem gerenciar prêmios.',
            )

            return redirect(
                'app_evento:urlsorteio_atividade',
                atividade_id=atividade.id,
            )

        action = request.POST.get('action', 'add')
        premios = request.session.get(session_key, [])

        if action == 'add':
            premio_nome = request.POST.get(
                'premio',
                '',
            ).strip()

            try:
                qtd_ganhadores = int(
                    request.POST.get('qtd_ganhadores', 1)
                )
            except (ValueError, TypeError):
                qtd_ganhadores = 1

            if premio_nome and qtd_ganhadores > 0:
                premios.append({
                    'nome': premio_nome,
                    'quantidade': qtd_ganhadores,
                })

                messages.success(
                    request,
                    f'Prêmio "{premio_nome}" cadastrado!',
                )
            else:
                messages.error(
                    request,
                    'Informe um nome de prêmio e uma quantidade válida.',
                )

        elif action == 'edit':
            try:
                index = int(request.POST.get('premio_index'))
                nova_qtd = int(request.POST.get('nova_qtd', 1))

                if (
                    0 <= index < len(premios)
                    and nova_qtd > 0
                ):
                    premios[index]['quantidade'] = nova_qtd

                    messages.success(
                        request,
                        'Quantidade alterada!',
                    )

            except (ValueError, TypeError):
                messages.error(
                    request,
                    'Não foi possível alterar a quantidade do prêmio.',
                )

        elif action == 'delete':
            try:
                index = int(request.POST.get('premio_index'))

                if 0 <= index < len(premios):
                    removido = premios.pop(index)

                    messages.success(
                        request,
                        f'Prêmio "{removido["nome"]}" removido!',
                    )

            except (ValueError, TypeError):
                messages.error(
                    request,
                    'Não foi possível remover o prêmio.',
                )

        elif action == 'clear_all':
            premios = []

            messages.success(
                request,
                'Todos os prêmios desta atividade foram apagados!',
            )

        request.session[session_key] = premios
        request.session.modified = True

        return redirect(
            'app_evento:urlsorteio_atividade',
            atividade_id=atividade.id,
        )

    premios = request.session.get(
        session_key,
        [],
    )

    context = {
        'atividade': atividade,
        'premios': premios,
        'sorteio': random.choice(premios) if premios else {
            'nome': 'Nenhum prêmio cadastrado',
            'quantidade': 1,
        },
        'participantes_json': json.dumps(lista_participantes),
        'premios_json': json.dumps(premios),
    }

    return render(
        request,
        'app_evento/sorteio.html',
        context,
    )