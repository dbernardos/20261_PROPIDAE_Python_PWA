from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

import json
from django.http import JsonResponse

from .models import Quiz, Resposta
from .form import RespostaQuizForm, CadastroQuizForm
from app_evento.models import Inscricao, Participa, Atividade 
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch

from django.utils import timezone
from django.db import models  
from django.db.models import Max
from django.urls import reverse


# Views do Quiz.
# -----------------------------------------------


def boas_vindas(request, cracha, atividade_id):
    """Página de boas-vindas"""
    # Busca a inscrição no app_evento usando o crachá
    inscricao = get_object_or_404(Inscricao, cracha=cracha)
    
    # Extrai o participante (Usuário) a partir da inscrição
    participante = inscricao.usuario 
    atividade = get_object_or_404(Atividade, id=atividade_id)
    
    print(f">>>>> Inscrição encontrada: {inscricao} participante: {participante}")
    
    # Obtém todos os quizzes ativos
    quizzes = Quiz.objects.filter(ativo=True)
    
    context = {
        'cracha': cracha,
        'participante': participante,
        'inscricao': inscricao,
        'atividade': atividade,
        'quizzes': quizzes,
        'evento': atividade.evento,
    }
    
    return render(request, 'app_quiz/boas_vindas.html', context)

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
          # Define o número do quiz como o próximo número disponível na atividade
          ultimo_numero = Quiz.objects.filter(atividade=atividade).aggregate(max_numero=models.Max('numero'))['max_numero'] or 0
          quiz_salvo.numero = ultimo_numero + 1
      
      quiz_salvo.save()
      messages.success(
          request,
          f'Quiz {"atualizado" if editando else "cadastrado"} com sucesso!',
      )
      return redirect(
          'app_evento:urldet_myevento',
          evento_id=quiz_salvo.atividade.evento.id,
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

    if acao == 'toggle_status':
      quiz.ativo = not quiz.ativo
      quiz.save()
      status_txt = 'ativado' if quiz.ativo else 'desativado'
      messages.success(request, f'Quiz "{quiz.titulo}" foi {status_txt}!')

    elif acao == 'excluir':
      quiz.delete()
      messages.success(request, 'Quiz excluído com sucesso!')

    return redirect('app_quiz:urlgerenciar_quizzes', atividade_id=atividade.id)

  # Identificação dinâmica do accessor ('respostas' ou 'resposta_set')
  accessor = Resposta._meta.get_field('quiz').remote_field.get_accessor_name()

  # Busca dos Quizzes 
  quizzes = Quiz.objects.filter(atividade=atividade).prefetch_related(
      Prefetch(
          accessor,
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

'''
def quizzes(request, cracha):
    """Página que lista todos os quizzes disponíveis na atividade"""
    inscricao = get_object_or_404(Inscricao, cracha=cracha)
    # quiz = get_object_or_404(Quiz, cracha=cracha)
    participante = inscricao.usuario 
    # quizzes = Quiz.objects.filter(ativo=True)
    
    # Filtra apenas os quizzes vinculados à inscrição E que estejam ativos
    quizzes = ( Quiz.objects.filter
               (atividade__participa__inscricao=inscricao, ativo=True)
               .order_by('numero').distinct()       
    )
    
    context = {
        'cracha': cracha,
        'participante': participante,
        'inscricao': inscricao,
        'quizzes': quizzes
    }
    
    return render(request, 'app_quiz/quizzes.html', context)
'''

#Talvez para substituir o Quizzes??
def quizzes_atividade(request, cracha, atividade_id):
    """Página que lista apenas os quizzes da atividade em que foi feito o check-in"""
    inscricao = get_object_or_404(Inscricao, cracha=cracha)
    participante = inscricao.usuario 
    atividade = get_object_or_404(Atividade, id=atividade_id)
    
    # Garante que ele só veja os quizzes se a presença estiver como True
    participacao = get_object_or_404(Participa, inscricao=inscricao, atividade=atividade)
    if not participacao.presente:
        messages.error(request, "Você precisa registrar presença pelo Leitor QR Code primeiro.")
        return redirect('app_quiz:urlboas_vindas', cracha=cracha)

    # Filtra APENAS os quizzes vinculados a ESTA atividade E que estejam ativos
    quizzes = Quiz.objects.filter(
        atividade=atividade, 
        ativo=True
    ).order_by('numero').distinct()
    
    quizzes_respondidos = Resposta.objects.filter(
        participa=participacao,
        completo=True
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


def leitor_qrcode(request, codigo_leitor):
    atividade = get_object_or_404(Atividade, codigo_leitor=codigo_leitor)
    
    context = {
        'atividade': atividade,
    }
    return render(request, 'app_quiz/leitor_qrcode.html', context)



def quiz_detail(request, cracha, quiz_id):
    """Página detalhada do quiz"""
    # Busca a inscrição pelo crachá e obtém o usuário associado
    inscricao = get_object_or_404(Inscricao, cracha=cracha)
    participante = inscricao.usuario 

    quiz = get_object_or_404(Quiz, id=quiz_id, ativo=True)
    
    if not quiz.ativo:
        messages.warning(
            request, 'Este desafio está temporariamente desativado pelo organizador.'
        )
        return redirect('app_quiz:urlquizzes_atividade', cracha=cracha)
    
    # Obtém a relação Participa
    participa_obj, created = Participa.objects.get_or_create(
      inscricao=inscricao,
      atividade=quiz.atividade,
    )
    
    resposta, created = Resposta.objects.get_or_create(
        participa=participa_obj,
        quiz=quiz,
    )
    
            

    if resposta.completo and request.method == 'POST':
        messages.warning(request, 'Você já respondeu a este desafio e não pode enviá-lo novamente.')
        return redirect('app_quiz:urlpagina_leitor', codigo_leitor=quiz.atividade.codigo_leitor)
        
    if request.method == 'POST':
        form = RespostaQuizForm(request.POST, instance=resposta)
        if form.is_valid():
            resposta = form.save(commit=False)
        
            resposta.correto = (quiz.valor_minimo <= resposta.valor_resposta <= quiz.valor_maximo)
            resposta.completo = True 
            resposta.save()
                
            messages.success(request, f'Resposta do Desafio {quiz.numero} registrada com sucesso!')
                
            return redirect('app_quiz:urlpagina_leitor', codigo_leitor=quiz.atividade.codigo_leitor)
                
    else:
        form = RespostaQuizForm(instance=resposta)
    
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

def reset_quiz(request, cracha, quiz_id):
    """Permite resetar um quiz para tentar novamente"""

    inscricao = get_object_or_404(Inscricao, cracha=cracha)
    participante = inscricao.usuario
    
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    resposta = Resposta.objects.filter(
        participa__inscricao=inscricao,
        quiz=quiz,

    ).first()
    
    if resposta:
        resposta.delete()
        messages.info(request, 'Quiz reiniciado. Boa sorte!')
    
    return redirect('app_quiz:urlquiz_detail', cracha=cracha, quiz_id=quiz.id)

def leitor_identificar(request):
    if request.method == 'POST':
        try:
            # Pega o JSON enviado pelo JavaScript
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
                return JsonResponse({
                    'autorizado': False, 'mensagem': 'QR Code não cadastrado.'} 
                )
            try:
                if atividade_param.isdigit():
                    participacao = Participa.objects.get(
                        inscricao=inscricao, atividade_id=int(atividade_param)
                    )
                    
                else:
                    participacao = Participa.objects.get(inscricao=inscricao, atividade_id=atividade_id)
                    participacao.presente = True
            except Participa.DoesNotExist:
                return JsonResponse({
                    "autorizado": False,
                    "mensagem": "Acesso negado. Este participante não está inscrito nesta atividade."  
                })   
             
            
            agora = timezone.now()
            participacao.presente = True
            participacao.data_hora_presenca = agora
            participacao.save()
            
            url_destino = reverse('app_quiz:urlboas_vindas', kwargs={
                'cracha': codigo,
                'atividade_id': participacao.atividade_id,
            })
                                  
            return JsonResponse({
                "autorizado": True,
                "id": codigo,
                "mensagem": f'Presença confirmada às ({agora.strftime("%H:%M:%S")})',
                "redirect_url": url_destino
            })      
                
        except json.JSONDecodeError:
            return JsonResponse({"mensagem": "Dados Inválidos"}, status=400)

    return JsonResponse({"mensagem": "Método não permitido"}, status=405)  

from django.shortcuts import render, redirect

