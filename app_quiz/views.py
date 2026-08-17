from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from django.contrib import messages

from django.utils import timezone
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import rotate_token
from django.views.decorators.csrf import ensure_csrf_cookie

#from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .models import Quiz, Resposta
from .form import RespostaQuizForm

# Nosso "banco de dados" simulado
# -----------------------------------------------
db_funcionarios = {
    "1": {"nome": "João Silva", "cargo": "Desenvolvedor", "empresa": "Weg"},
    "2": {"nome": "Maria Souza", "cargo": "Gerente de Projetos", "empresa": "Weg" },
    "3": {"nome": "Carlos Oliveira", "cargo": "Diretor", "empresa": "Weg"},
}

# Create your QUIZ views here.
# -----------------------------------------------
def boas_vindas(request, cracha):
    """Página de boas-vindas com quadro de progresso"""
    Usuario = get_user_model()
    participante = get_object_or_404(Usuario, username=cracha)
    
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
    
    return render(request, 'app_quiz/boas_vindas.html', context)


def leitor_qrcode(request):
    return render(request, 'app_quiz/leitor_qrcode.html')


def quiz_detail(request, cracha, quiz_numero):
    """Página detalhada do quiz"""
    Usuario = get_user_model()
    participante = get_object_or_404(Usuario, username=cracha)
    #participante = get_object_or_404(Usuario, username=cracha)
    #participante = get_object_or_404(Participante, cracha=cracha)
    quiz = get_object_or_404(Quiz, numero=quiz_numero, ativo=True)
    
    # Obtém ou cria resposta
    resposta, created = Resposta.objects.get_or_create(
        participante=participante,
        quiz=quiz
    )
    
    if request.method == 'POST':
        form = RespostaQuizForm(request.POST, instance=resposta)
        if form.is_valid():
            resposta = form.save(commit=False)
            resposta.tentativas += 1
            resposta.verificar_resposta()
            resposta.save()
            
            if resposta.correto:
                messages.success(request, f'Parabéns! Sua resposta está correta!')
            else:
                messages.warning(request, f'Resposta incorreta. Tente novamente!')
            
            return redirect('app_quiz:urlquiz_detail', cracha=cracha, quiz_numero=quiz_numero)
    else:
        form = RespostaQuizForm(instance=resposta)
    
    context = {
        'participante': participante,
        'quiz': quiz,
        'resposta': resposta,
        'form': form,
        'progresso_geral': participante.get_progresso_geral()
    }
    
    return render(request, 'app_quiz/quiz_detail.html', context)

def reset_quiz(request, cracha, quiz_numero):
    """Permite resetar um quiz para tentar novamente"""
    Usuario = get_user_model()
    participante = get_object_or_404(Usuario, username=cracha)
    #participante = get_object_or_404(Participante, cracha=cracha)
    quiz = get_object_or_404(Quiz, numero=quiz_numero)
    
    resposta = Resposta.objects.filter(
        participante=participante,
        quiz=quiz
    ).first()
    
    if resposta:
        resposta.delete()
        messages.info(request, 'Quiz reiniciado. Boa sorte!')
    
    return redirect('app_quiz:urlquiz_detail', cracha=cracha, quiz_numero=quiz_numero)


#####

def quiz(request):
    return render(request, 'app_quiz/quiz.html')


#@csrf_exempt
def identificar_funcionario(request):
    
    print(f"DEBUG - Método recebido: {request.method}")
    print(f"DEBUG - Headers: {request.headers}")
    print(f"DEBUG - Body: {request.body}")

    if request.method == 'POST':
        print("entrou no primeiro IF")
        try:
            # Pega o JSON enviado pelo JavaScript do celular
            dados_recebidos = json.loads(request.body)
            codigo = dados_recebidos.get('codigo', '')

            print(f"DEBUG - Código recebido da câmera: '{codigo}'")
            codigo = codigo.strip()
            # Verifica se o código existe no dicionário
            if codigo in db_funcionarios:
                print("entrou no segundo IF - código encontrado")
                dados = db_funcionarios[codigo]
                return JsonResponse({
                    "autorizado": True,
                    "id": codigo,
                    "nome": dados["nome"],
                    "cargo": dados["cargo"],
                    "empresa": dados["empresa"],
                    "mensagem": "ACESSO LIBERADO"
                })

            else:
                print("entrou no else - código não encontrado")
                return JsonResponse({
                    "autorizado": False,
                    "id": codigo,
                    "mensagem": "ACESSO NEGADO"
                })
        except json.JSONDecodeError:
            return JsonResponse({"mensagem": "Erro nos dados enviados"}, status=400)

    return JsonResponse({"mensagem": "Método não permitido"}, status=405)  


from django.shortcuts import render, redirect
