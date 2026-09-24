from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

import json
from django.http import JsonResponse

from .models import Quiz, Resposta
from .form import RespostaQuizForm
from app_evento.models import Inscricao, Participa, Atividade 


# Views do Quiz.
# -----------------------------------------------

def calcular_progresso_geral(participante):
    total = Quiz.objects.filter(ativo=True).count()
    
    respondidos = Resposta.objects.filter(
        participa__inscricao__usuario=participante,
        quiz__ativo=True,
        completo=True
    ).count()
    
    porcentagem = round((respondidos / total) * 100, 2) if total > 0 else 0
    
    return {
        'total': total,
        'respondidos': respondidos,
        'porcentagem': porcentagem,
    }



def boas_vindas(request, cracha):
    """Página de boas-vindas com quadro de progresso"""
    # Busca a inscrição no app_evento usando o crachá
    inscricao = get_object_or_404(Inscricao, cracha=cracha)
    # Extrai o participante (Usuário) a partir da inscrição
    participante = inscricao.usuario 

    print(f">>>>> Inscrição encontrada: {inscricao}")
    print(f">>>>> participante: {participante}")
    # Obtém todos os quizzes ativos
    quizzes = Quiz.objects.filter(ativo=True)
    
    # Calcula progresso para cada quiz
    progresso_quizzes = []
    for quiz in quizzes:
        resposta = Resposta.objects.filter(
            participa__inscricao=inscricao, 
            quiz=quiz,

        ).first()
        
        progresso_quizzes.append({
            'quiz': quiz,
            'resposta': resposta,
            'completo': resposta.completo if resposta else False,
            
        })
    
    progresso_geral = calcular_progresso_geral(participante)
    
    context = {
        'cracha': cracha,
        'participante': participante,
        'inscricao': inscricao,
        'progresso_quizzes': progresso_quizzes,
        'progresso_geral': progresso_geral,
        'quizzes_completos': progresso_geral['respondidos'],
        'total_quizzes': progresso_geral['total'],
        'porcentagem_conclusao': progresso_geral['porcentagem']
    }
    
    return render(request, 'app_quiz/boas_vindas.html', context)
    

def leitor_qrcode(request):
    return render(request, 'app_quiz/leitor_qrcode.html')

def quiz_detail(request, cracha, quiz_numero):
    """Página detalhada do quiz"""
    # 1. Busca a inscrição pelo crachá e obtém o usuário associado
    inscricao = get_object_or_404(Inscricao, cracha=cracha)
    participante = inscricao.usuario 
    quiz = get_object_or_404(Quiz, numero=quiz_numero, ativo=True)
    
    # 2. Obtém a relação Participa
    participa_obj = Participa.objects.filter(inscricao=inscricao).first()
    
    if not participa_obj:
        atividade = Atividade.objects.filter(evento=inscricao.evento).first()
        if not atividade:
            atividade = Atividade.objects.create(
            evento=inscricao.evento,
            nome="Quiz/Desafio",
            descricao="Atividade gerada para vincular ao Quiz"
            )
            
        participa_obj = Participa.objects.create(
            inscricao=inscricao,
            atividade=atividade,
            
        )
            
    resposta, created = Resposta.objects.get_or_create(
        participa=participa_obj,
        quiz=quiz,
    )
            
    # 3. Processa o formulário de resposta
    if request.method == 'POST':
        form = RespostaQuizForm(request.POST, instance=resposta)
        if form.is_valid():
            resposta = form.save(commit=False)
            
            if hasattr(resposta, 'tentativas'):
                resposta.tentativas += 1
                
            if hasattr(resposta, 'verificar_resposta'):
                resposta.verificar_resposta()
            else:
                resposta.correto = (quiz.valor_minimo <= resposta.valor_resposta <= quiz.valor_maximo)
            resposta.save()
            
            if getattr(resposta, 'correto', False):
                messages.success(request, 'Parabéns! Sua resposta está correta!')
            else:
                messages.warning(request, 'Resposta incorreta. Tente novamente!')
            
            return redirect('app_quiz:urlquiz_detail', cracha=cracha, quiz_numero=quiz_numero)
             
    else:
        form = RespostaQuizForm(instance=resposta)
    
    context = {
        'cracha': cracha,
        'participante': participante,
        'inscricao': inscricao,
        'quiz': quiz,
        'resposta': resposta,
        'form': form,
        'progresso_geral': calcular_progresso_geral(participante)
    }
    
    return render(request, 'app_quiz/quiz_detail.html', context)

def reset_quiz(request, cracha, quiz_numero):
    """Permite resetar um quiz para tentar novamente"""

    inscricao = get_object_or_404(Inscricao, cracha=cracha)
    participante = inscricao.usuario
    
    quiz = get_object_or_404(Quiz, numero=quiz_numero)
    
    resposta = Resposta.objects.filter(
        participa__inscricao=inscricao,
        quiz=quiz,

    ).first()
    
    if resposta:
        resposta.delete()
        messages.info(request, 'Quiz reiniciado. Boa sorte!')
    
    return redirect('app_quiz:urlquiz_detail', cracha=cracha, quiz_numero=quiz_numero)

def identificar_funcionario(request):
    if request.method == 'POST':
        try:
            # Pega o JSON enviado pelo JavaScript
            dados_recebidos = json.loads(request.body)
            codigo = dados_recebidos.get('codigo', '').strip()

            try:
                inscricao = Inscricao.objects.select_related('usuario').get(cracha=codigo)
                usuario = inscricao.usuario
                
                return JsonResponse({
                    "autorizado": True,
                    "id": codigo,
                    "nome": getattr(usuario, 'nome', 'Nome não cadastrado'),
                    "cargo": getattr(usuario, 'cargo', 'Cargo não cadastrado'),
                    "empresa": getattr(usuario, 'empresa', 'Empresa não cadastrada'),
                    "mensagem": "ACESSO LIBERADO"  
                })                    
            
            # Verifica se o código de inscrição existe
            except Inscricao.DoesNotExist:
                print(f"DEBUG - Inscrição não encontrada para o código: '{codigo}'")
                return JsonResponse({
                    "autorizado": False,
                    "id": codigo,
                    "mensagem": "ACESSO NEGADO"
                })
                
        except json.JSONDecodeError:
            return JsonResponse({"mensagem": "Erro nos dados enviados"}, status=400)

    return JsonResponse({"mensagem": "Método não permitido"}, status=405)  

from django.shortcuts import render, redirect
