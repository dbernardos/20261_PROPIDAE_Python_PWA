from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .form import UsuarioForm
from django.utils import timezone
from .models import Participante, Quiz, RespostaQuiz, LogAcesso
from .form import ParticipanteForm, RespostaQuizForm
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

def leitor_qrcode(request):
    return render(request, 'leitor_qrcode.html')
    #return render(request, 'leitor_qrcode_copy.html')

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
            participante, created = Participante.objects.get_or_create(
                cracha=cracha,
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
            
            # Registra log de acesso
            LogAcesso.objects.create(
                participante=participante,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            
            # Atualiza último acesso
            participante.ultimo_acesso = timezone.now()
            participante.save()
            
            # Redireciona para página de boas-vindas
            return redirect('boas_vindas', cracha=participante.cracha)
    else:
        form = ParticipanteForm()
    
    return render(request, 'quiz/login_participante.html', {'form': form})

def boas_vindas(request, cracha):
    """Página de boas-vindas com quadro de progresso"""
    participante = get_object_or_404(Participante, cracha=cracha)
    
    # Obtém todos os quizzes ativos
    quizzes = Quiz.objects.filter(ativo=True)
    
    # Calcula progresso para cada quiz
    progresso_quizzes = []
    for quiz in quizzes:
        resposta = RespostaQuiz.objects.filter(
            participante=participante, 
            quiz=quiz
        ).first()
        
        progresso_quizzes.append({
            'quiz': quiz,
            'resposta': resposta,
            'completo': resposta.completo if resposta else False,
            'tentativas': resposta.tentativas if resposta else 0
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

def quiz_detail(request, cracha, quiz_numero):
    """Página detalhada do quiz"""
    participante = get_object_or_404(Participante, cracha=cracha)
    quiz = get_object_or_404(Quiz, numero=quiz_numero, ativo=True)
    
    # Obtém ou cria resposta
    resposta, created = RespostaQuiz.objects.get_or_create(
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
                messages.success(request, f'🎉 Parabéns! Sua resposta está correta!')
            else:
                messages.warning(request, f'❌ Resposta incorreta. Tente novamente!')
            
            return redirect('quiz_detail', cracha=cracha, quiz_numero=quiz_numero)
    else:
        form = RespostaQuizForm(instance=resposta)
    
    context = {
        'participante': participante,
        'quiz': quiz,
        'resposta': resposta,
        'form': form,
        'progresso_geral': participante.get_progresso_geral()
    }
    
    return render(request, 'quiz/quiz_detail.html', context)

def reset_quiz(request, cracha, quiz_numero):
    """Permite resetar um quiz para tentar novamente"""
    participante = get_object_or_404(Participante, cracha=cracha)
    quiz = get_object_or_404(Quiz, numero=quiz_numero)
    
    resposta = RespostaQuiz.objects.filter(
        participante=participante,
        quiz=quiz
    ).first()
    
    if resposta:
        resposta.delete()
        messages.info(request, 'Quiz reiniciado. Boa sorte!')
    
    return redirect('quiz_detail', cracha=cracha, quiz_numero=quiz_numero)


#####

def quiz(request):
    return render(request, 'quiz.html')

def index(request):
    return render(request, 'index.html')

def entrar(request):
    if request.method == "GET":
        return render(request, "entrar.html")
    elif request.method == "POST":
        usuario = request.POST.get("txtUser")
        senha = request.POST.get("txtPass")
        user = authenticate(username=usuario, password=senha)

        if user:
            login(request, user)
            return redirect('urlindex')
        messages.error(request, "Falha na autenticação!")    
        return render(request, 'entrar.html')

def sair(request):
    logout(request)
    return redirect('urlentrar')


# Nosso "banco de dados" simulado
db_funcionarios = {
    "1": {"nome": "João Silva", "cargo": "Desenvolvedor", "empresa": "Weg"},
    "2": {"nome": "Maria Souza", "cargo": "Gerente de Projetos", "empresa": "Weg" },
    "3": {"nome": "Carlos Oliveira", "cargo": "Diretor", "empresa": "Weg"},
}

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