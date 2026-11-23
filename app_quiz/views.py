import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie

from app_evento.models import Atividade, Inscricao, Participa
from app_quiz.models import Quiz, Resposta

from .form import CadastroQuizForm, RespostaQuizForm


# Views do Quiz.
# -----------------------------------------------

@never_cache
def boas_vindas(request, cracha, atividade_id):
    """Página de boas-vindas após leitura do QR Code"""
    inscricao = get_object_or_404(Inscricao, cracha=cracha)
    participante = inscricao.usuario
    atividade = get_object_or_404(Atividade, id=atividade_id)

    # Filtra apenas os quizzes ativos vinculados a esta atividade
    quizzes = Quiz.objects.filter(atividade=atividade, ativo=True).distinct()
    total_quizzes = quizzes.count()

    participacao = Participa.objects.filter(
        inscricao=inscricao,
        atividade=atividade,
    ).first()

    if total_quizzes > 0 and participacao:
        respondidos_count = (
            Resposta.objects.filter(
                participa=participacao,
                quiz__in=quizzes,
                completo=True,
            )
            .values('quiz_id')
            .distinct()
            .count()
        )
    else:
        respondidos_count = 0

    todos_respondidos = total_quizzes > 0 and respondidos_count >= total_quizzes
    tem_quiz_pendente = total_quizzes > 0 and not todos_respondidos

    context = {
        'cracha': cracha,
        'participante': participante,
        'inscricao': inscricao,
        'atividade': atividade,
        'quizzes': quizzes,
        'evento': atividade.evento,
        'tem_quiz_pendente': tem_quiz_pendente,
        'todos_respondidos': todos_respondidos,
    }

    return render(request, 'app_quiz/boas_vindas.html', context)


@login_required
def cadastrar_quiz(request, atividade_id=None, quiz_id=None):
    """View para cadastrar ou editar um quiz vinculado a uma atividade"""
    atividade = None
    evento = None
    quiz = None
    editando = False

    if quiz_id:
        quiz = get_object_or_404(Quiz, id=quiz_id)
        editando = True
        atividade = quiz.atividade
        evento = atividade.evento
    elif atividade_id:
        atividade = get_object_or_404(Atividade, id=atividade_id)
        evento = atividade.evento

    if request.method == 'POST':
        form_quiz = CadastroQuizForm(request.POST, instance=quiz)
        if form_quiz.is_valid():
            quiz_salvo = form_quiz.save(commit=False)
            quiz_salvo.atividade = atividade

            if not editando:
                ultimo_numero = (
                    Quiz.objects.filter(atividade=atividade)
                    .aggregate(max_numero=models.Max('numero'))['max_numero']
                    or 0
                )
                quiz_salvo.numero = ultimo_numero + 1

            quiz_salvo.save()
            messages.success(
                request,
                f'Desafio {"atualizado" if editando else "cadastrado"} com sucesso!',
            )
            return redirect(
                'app_quiz:urlgerenciar_quizzes',
                atividade_id=quiz_salvo.atividade.id,
            )
    else:
        initial_data = {}
        if atividade:
            initial_data['atividade'] = atividade

        form_quiz = CadastroQuizForm(instance=quiz, initial=initial_data)

    context = {
        'form_quiz': form_quiz,
        'editando': editando,
        'quiz': quiz,
        'atividade': atividade,
        'evento': evento,
    }

    return render(request, 'app_quiz/cadastrar_quiz.html', context)


@login_required
def gerenciar_quizzes(request, atividade_id):
    """View centralizada para gerenciar, alternar status, excluir e listar respostas dos quizzes."""
    atividade = get_object_or_404(Atividade, id=atividade_id)

    if request.method == 'POST':
        acao = request.POST.get('acao')
        quiz_id = request.POST.get('quiz_id')
        quiz = get_object_or_404(Quiz, id=quiz_id, atividade=atividade)

        if acao == 'alternar_status':
            quiz.ativo = not quiz.ativo
            quiz.save()
            status_txt = 'ativado' if quiz.ativo else 'desativado'
            messages.success(request, f'Quiz "{quiz.titulo}" foi {status_txt}!')

        elif acao == 'excluir':
            quiz.delete()
            messages.success(request, 'Quiz excluído com sucesso!')

        return redirect('app_quiz:urlgerenciar_quizzes', atividade_id=atividade.id)

    respostas = Resposta._meta.get_field('quiz').remote_field.get_accessor_name()

    quizzes = Quiz.objects.filter(atividade=atividade).prefetch_related(
        Prefetch(
            respostas,
            queryset=Resposta.objects.select_related(
                'participa__inscricao__usuario'
            ),
        )
    )

    context = {
        'atividade': atividade,
        'evento': atividade.evento,
        'quizzes': quizzes,
    }
    return render(request, 'app_quiz/gerenciar_quizzes.html', context)

@never_cache
def quizzes_atividade(request, cracha, atividade_id):
    """Página que lista apenas os quizzes da atividade em que foi feito o check-in"""
    inscricao = get_object_or_404(Inscricao, cracha=cracha)
    participante = inscricao.usuario
    atividade = get_object_or_404(Atividade, id=atividade_id)

    # Garante que ele só veja os quizzes se a presença estiver confirmada
    participacao = get_object_or_404(Participa, inscricao=inscricao, atividade=atividade)
    if not participacao.presente:
        messages.error(request, 'Você precisa registrar presença pelo Leitor QR Code primeiro.')
        return redirect('app_quiz:urlboas_vindas', cracha=cracha, atividade_id=atividade.id)

    quizzes = Quiz.objects.filter(
        atividade=atividade,
        ativo=True,
    ).order_by('numero').distinct()

    quizzes_respondidos = Resposta.objects.filter(
        participa=participacao,
        completo=True,
    ).values_list('quiz_id', flat=True)

    context = {
        'cracha': cracha,
        'participante': participante,
        'inscricao': inscricao,
        'atividade': atividade,
        'quizzes': quizzes,
        'quizzes_respondidos': quizzes_respondidos,
    }

    return render(request, 'app_quiz/quizzes.html', context)

@ensure_csrf_cookie
@never_cache
def leitor_qrcode(request, codigo_leitor):
    atividade = get_object_or_404(Atividade, codigo_leitor=codigo_leitor)

    context = {
        'atividade': atividade,
    }
    return render(request, 'app_quiz/leitor_qrcode.html', context)

@never_cache
def quiz_detail(request, cracha, quiz_id):
    """Página detalhada do quiz"""
    inscricao = get_object_or_404(Inscricao, cracha=cracha)
    participante = inscricao.usuario

    quiz = get_object_or_404(Quiz, id=quiz_id)

    if not quiz.ativo:
        messages.warning(
            request, 'Este desafio está temporariamente desativado pelo organizador.'
        )
        return redirect(
            'app_quiz:urlquizzes_atividade',
            cracha=cracha,
            atividade_id=quiz.atividade.id,
        )

    participa_obj, _ = Participa.objects.get_or_create(
        inscricao=inscricao,
        atividade=quiz.atividade,
    )

    resposta, _ = Resposta.objects.get_or_create(
        participa=participa_obj,
        quiz=quiz,
    )

    if resposta.completo and request.method == 'POST':
        messages.warning(
            request, 'Você já respondeu a este desafio e não pode enviá-lo novamente.'
        )
        return redirect(
            'app_quiz:urlpagina_leitor',
            codigo_leitor=quiz.atividade.codigo_leitor,
        )

    form = RespostaQuizForm(instance=resposta)

    if request.method == 'POST':
        # Fluxo de Múltipla Escolha
        if quiz.tipo == 'MULTIPLA':
            escolha = request.POST.get('resposta_multipla', '').strip().upper()

            if escolha not in ['A', 'B', 'C', 'D']:
                messages.error(request, 'Selecione uma alternativa antes de enviar.')
            else:
                resposta.resposta_texto = escolha
                if escolha == quiz.alternativa_correta:
                    resposta.correto = True
                    resposta.status = 'certo'
                else:
                    resposta.correto = False
                    resposta.status = 'errado'

                resposta.completo = True
                resposta.save()

                messages.success(
                    request, f'Resposta do Desafio {quiz.numero} registrada com sucesso!'
                )
                return redirect(
                    'app_quiz:urlpagina_leitor',
                    codigo_leitor=quiz.atividade.codigo_leitor,
                )

        # Fluxo Numérico / Métrico
        else:
            form = RespostaQuizForm(request.POST, instance=resposta)
            if form.is_valid():
                resposta = form.save(commit=False)
                valor = resposta.valor_resposta

                if (
                    valor is not None
                    and quiz.valor_minimo is not None
                    and quiz.valor_maximo is not None
                    and quiz.valor_minimo <= valor <= quiz.valor_maximo
                ):
                    resposta.correto = True
                    if quiz.valor_ideal is not None and valor == quiz.valor_ideal:
                        resposta.status = 'certo'
                    else:
                        resposta.status = 'aproximado'
                else:
                    resposta.correto = False
                    resposta.status = 'errado'

                resposta.completo = True
                resposta.save()

                messages.success(
                    request, f'Resposta do Desafio {quiz.numero} registrada com sucesso!'
                )
                return redirect(
                    'app_quiz:urlpagina_leitor',
                    codigo_leitor=quiz.atividade.codigo_leitor,
                )

    context = {
        'cracha': cracha,
        'participante': participante,
        'inscricao': inscricao,
        'quiz': quiz,
        'atividade': quiz.atividade,
        'resposta': resposta,
        'form': form,
    }

    return render(request, 'app_quiz/quiz_detail.html', context)

@never_cache
def leitor_identificar(request):
    if request.method == 'POST':
        try:
            dados_recebidos = json.loads(request.body)
            codigo = dados_recebidos.get('codigo', '').strip()
            atividade_param = str(dados_recebidos.get('atividade_id', '')).strip()

            if not atividade_param:
                return JsonResponse(
                    {'autorizado': False, 'mensagem': 'Atividade não identificada.'}
                )

            try:
                inscricao = Inscricao.objects.get(cracha=codigo)
            except Inscricao.DoesNotExist:
                return JsonResponse(
                    {'autorizado': False, 'mensagem': 'QR Code não cadastrado.'}
                )

            try:
                if atividade_param.isdigit():
                    participacao = Participa.objects.get(
                        inscricao=inscricao,
                        atividade_id=int(atividade_param),
                    )
                else:
                    participacao = Participa.objects.get(
                        inscricao=inscricao,
                        atividade__codigo_leitor=atividade_param,
                    )
            except Participa.DoesNotExist:
                return JsonResponse(
                    {
                        'autorizado': False,
                        'mensagem': 'Acesso negado. Este participante não está inscrito nesta atividade.',
                    }
                )

            agora = timezone.now()
            participacao.presente = True
            participacao.data_hora_presenca = agora
            participacao.save()

            url_destino = reverse(
                'app_quiz:urlboas_vindas',
                kwargs={
                    'cracha': codigo,
                    'atividade_id': participacao.atividade_id,
                },
            )

            return JsonResponse(
                {
                    'autorizado': True,
                    'id': codigo,
                    'mensagem': f'Presença confirmada às ({agora.strftime("%H:%M:%S")})',
                    'redirect_url': url_destino,
                }
            )

        except json.JSONDecodeError:
            return JsonResponse({'mensagem': 'Dados Inválidos'}, status=400)

    return JsonResponse({'mensagem': 'Método não permitido'}, status=405)