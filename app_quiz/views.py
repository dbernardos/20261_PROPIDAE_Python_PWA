import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie

from app_evento.models import Atividade, Inscricao, Participa
from .form import CadastroQuizForm, RespostaQuizForm
from .models import Quiz, Resposta


def _verificar_permissao_evento(user, evento):
    """Ajuste o atributo de dono do evento conforme seu model Evento (ex: evento.organizador ou evento.criador)."""
    if not user.is_staff and getattr(evento, 'usuario', None) != user:
        # Se o seu model Evento usa outro campo (ex: evento.criador), substitua 'usuario' acima.
        pass


@never_cache
def boas_vindas(request, cracha, atividade_id):
    inscricao = get_object_or_404(Inscricao, cracha=cracha)
    atividade = get_object_or_404(Atividade, id=atividade_id)
    quizzes = Quiz.objects.filter(atividade=atividade, ativo=True)
    total_quizzes = quizzes.count()

    participacao = Participa.objects.filter(inscricao=inscricao, atividade=atividade).first()
    respondidos_count = (
        Resposta.objects.filter(participa=participacao, quiz__in=quizzes, completo=True).count()
        if total_quizzes > 0 and participacao else 0
    )

    todos_respondidos = total_quizzes > 0 and respondidos_count >= total_quizzes
    context = {
        'cracha': cracha,
        'participante': inscricao.usuario,
        'inscricao': inscricao,
        'atividade': atividade,
        'quizzes': quizzes,
        'evento': atividade.evento,
        'tem_quiz_pendente': total_quizzes > 0 and not todos_respondidos,
        'todos_respondidos': todos_respondidos,
    }
    return render(request, 'app_quiz/boas_vindas.html', context)


@login_required
def cadastrar_quiz(request, atividade_id=None, quiz_id=None):
    if quiz_id:
        quiz = get_object_or_404(Quiz, id=quiz_id)
        atividade = quiz.atividade
    else:
        quiz = None
        atividade = get_object_or_404(Atividade, id=atividade_id)

    _verificar_permissao_evento(request.user, atividade.evento)
    editando = quiz is not None

    form_quiz = CadastroQuizForm(request.POST or None, instance=quiz)
    if request.method == 'POST' and form_quiz.is_valid():
        quiz_salvo = form_quiz.save(commit=False)
        quiz_salvo.atividade = atividade
        quiz_salvo.save()  # A numeração sequencial já é feita no Quiz.save()
        messages.success(request, f'Desafio {"atualizado" if editando else "cadastrado"} com sucesso!')
        return redirect('app_quiz:urlgerenciar_quizzes', atividade_id=atividade.id)

    return render(request, 'app_quiz/cadastrar_quiz.html', {
        'form_quiz': form_quiz,
        'editando': editando,
        'quiz': quiz,
        'atividade': atividade,
        'evento': atividade.evento,
    })


@login_required
def gerenciar_quizzes(request, atividade_id):
    atividade = get_object_or_404(Atividade, id=atividade_id)
    _verificar_permissao_evento(request.user, atividade.evento)

    if request.method == 'POST':
        acao = request.POST.get('acao')
        quiz = get_object_or_404(Quiz, id=request.POST.get('quiz_id'), atividade=atividade)

        if acao == 'alternar_status':
            quiz.ativo = not quiz.ativo
            quiz.save(update_fields=['ativo'])
            messages.success(request, f'Quiz "{quiz.titulo}" foi {"ativado" if quiz.ativo else "desativado"}!')
        elif acao == 'excluir':
            quiz.delete()
            messages.success(request, 'Quiz excluído com sucesso!')

        return redirect('app_quiz:urlgerenciar_quizzes', atividade_id=atividade.id)

    quizzes = Quiz.objects.filter(atividade=atividade).prefetch_related(
        Prefetch(
            'respostas',
            queryset=Resposta.objects.filter(completo=True).select_related('participa__inscricao__usuario'),
        )
    )
    return render(request, 'app_quiz/gerenciar_quizzes.html', {
        'atividade': atividade,
        'evento': atividade.evento,
        'quizzes': quizzes,
    })


@never_cache
def quizzes_atividade(request, cracha, atividade_id):
    inscricao = get_object_or_404(Inscricao, cracha=cracha)
    atividade = get_object_or_404(Atividade, id=atividade_id)
    participacao = get_object_or_404(Participa, inscricao=inscricao, atividade=atividade)

    if not participacao.presente:
        messages.error(request, 'Você precisa registrar presença pelo Leitor QR Code primeiro.')
        return redirect('app_quiz:urlboas_vindas', cracha=cracha, atividade_id=atividade.id)

    quizzes = Quiz.objects.filter(atividade=atividade, ativo=True).order_by('numero')
    quizzes_respondidos = list(
        Resposta.objects.filter(participa=participacao, completo=True).values_list('quiz_id', flat=True)
    )
    return render(request, 'app_quiz/quizzes.html', {
        'cracha': cracha,
        'participante': inscricao.usuario,
        'inscricao': inscricao,
        'atividade': atividade,
        'quizzes': quizzes,
        'quizzes_respondidos': quizzes_respondidos,
    })


@ensure_csrf_cookie
@never_cache
def leitor_qrcode(request, codigo_leitor):
    atividade = get_object_or_404(Atividade, codigo_leitor=codigo_leitor)
    return render(request, 'app_quiz/leitor_qrcode.html', {'atividade': atividade})


@never_cache
def quiz_detail(request, cracha, quiz_id):
    inscricao = get_object_or_404(Inscricao, cracha=cracha)
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if not quiz.ativo:
        messages.warning(request, 'Este desafio está temporariamente desativado pelo organizador.')
        return redirect('app_quiz:urlquizzes_atividade', cracha=cracha, atividade_id=quiz.atividade.id)

    participacao = get_object_or_404(Participa, inscricao=inscricao, atividade=quiz.atividade)
    if not participacao.presente:
        messages.error(request, 'Você precisa registrar presença pelo Leitor QR Code primeiro.')
        return redirect('app_quiz:urlboas_vindas', cracha=cracha, atividade_id=quiz.atividade.id)

    # Não cria registro no banco durante o GET
    resposta = Resposta.objects.filter(participa=participacao, quiz=quiz).first()

    if resposta and resposta.completo and request.method == 'POST':
        messages.warning(request, 'Você já respondeu a este desafio e não pode enviá-lo novamente.')
        return redirect('app_quiz:urlpagina_leitor', codigo_leitor=quiz.atividade.codigo_leitor)

    form = RespostaQuizForm(request.POST or None, instance=resposta)

    if request.method == 'POST':
        resposta = resposta or Resposta(participa=participacao, quiz=quiz)

        if quiz.tipo == 'MULTIPLA':
            escolha = request.POST.get('resposta_multipla', '').strip().upper()
            if escolha not in ('A', 'B', 'C', 'D'):
                messages.error(request, 'Selecione uma alternativa antes de enviar.')
            else:
                resposta.resposta_texto = escolha
                resposta.avaliar()
                resposta.save()
                messages.success(request, f'Resposta do Desafio {quiz.numero} registrada com sucesso!')
                return redirect('app_quiz:urlpagina_leitor', codigo_leitor=quiz.atividade.codigo_leitor)
        elif form.is_valid():
            resposta = form.save(commit=False)
            resposta.participa = participacao
            resposta.quiz = quiz
            resposta.avaliar()
            resposta.save()
            messages.success(request, f'Resposta do Desafio {quiz.numero} registrada com sucesso!')
            return redirect('app_quiz:urlpagina_leitor', codigo_leitor=quiz.atividade.codigo_leitor)

    return render(request, 'app_quiz/quiz_detail.html', {
        'cracha': cracha,
        'participante': inscricao.usuario,
        'inscricao': inscricao,
        'quiz': quiz,
        'atividade': quiz.atividade,
        'resposta': resposta,
        'form': form,
    })


@never_cache
def leitor_identificar(request):
    if request.method != 'POST':
        return JsonResponse({'mensagem': 'Método não permitido'}, status=405)

    try:
        dados = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'mensagem': 'Dados Inválidos'}, status=400)

    codigo = str(dados.get('codigo', '')).strip()
    atividade_param = str(dados.get('atividade_id', '')).strip()

    if not atividade_param:
        return JsonResponse({'autorizado': False, 'mensagem': 'Atividade não identificada.'})

    inscricao = Inscricao.objects.filter(cracha=codigo).first()
    if not inscricao:
        return JsonResponse({'autorizado': False, 'mensagem': 'QR Code não cadastrado.'})

    filtro = {'atividade_id': int(atividade_param)} if atividade_param.isdigit() else {'atividade__codigo_leitor': atividade_param}
    participacao = Participa.objects.filter(inscricao=inscricao, **filtro).first()
    if not participacao:
        return JsonResponse({'autorizado': False, 'mensagem': 'Acesso negado. Este participante não está inscrito nesta atividade.'})

    agora = timezone.now()
    participacao.presente = True
    participacao.data_hora_presenca = agora
    participacao.save(update_fields=['presente', 'data_hora_presenca'])

    url_destino = reverse('app_quiz:urlboas_vindas', kwargs={'cracha': codigo, 'atividade_id': participacao.atividade_id})
    return JsonResponse({
        'autorizado': True,
        'id': codigo,
        'mensagem': f'Presença confirmada às ({agora.strftime("%H:%M:%S")})',
        'redirect_url': url_destino,
    })