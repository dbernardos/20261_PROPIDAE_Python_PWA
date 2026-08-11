from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .form import UsuarioForm
from django.utils import timezone
from .models import Participa, Quiz, Resposta, Usuario, Evento, Atividade, Inscricao
from .form import ParticipanteForm, RespostaQuizForm, EventoForm, AtividadeForm
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import rotate_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.cache import never_cache

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
            participante, created = Usuario.objects.get_or_create(
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
            
            # Atualiza último acesso
            participante.ultimo_acesso = timezone.now()
            participante.save()
            
            # Redireciona para página de boas-vindas
            return redirect('boas_vindas', cracha=participante.nome)
    else:
        form = ParticipanteForm()
    
    return render(request, 'quiz/login_participante.html', {'form': form})

def boas_vindas(request, cracha):
    """Página de boas-vindas com quadro de progresso"""
    participante = get_object_or_404(Usuario, nome=cracha)
    
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

@never_cache
@ensure_csrf_cookie
def index(request):
    return render(request, 'index.html')


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

@never_cache
@login_required(login_url='login')
def cadastrar_evento(request, evento_id=None):
    """View para cadastro e edição de evento para o adm logado"""
    evento = get_object_or_404(Evento, id=evento_id) if evento_id else None
    eventos = Evento.objects.all().order_by('-dataInicio')

    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES, instance=evento)

        if form.is_valid():
            evento_salvo = form.save(commit=False)
            if not evento_salvo.pk:
                evento_salvo.administrador = request.user
            evento_salvo.save()

            if evento_id:
                messages.success(request, '🎉 Evento atualizado com sucesso!')
                return redirect('cadastrar_evento')
            else:
                messages.success(request, '🎉 Evento cadastrado com sucesso!')
                return redirect('cadastrar_atividade', evento_id=evento_salvo.id)
    else:
        form = EventoForm(instance=evento)

    context = {
        'form_evento': form,
        'eventos': eventos,
        'editando': bool(evento_id),
        'evento': evento
    }
    return render(request, 'eventos.html', context)

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
@login_required(login_url='login')
def cadastrar_atividade(request, evento_id):
    evento_atual = get_object_or_404(Evento, id=evento_id)
    if request.method == 'POST':
        form = AtividadeForm(request.POST)

        if form.is_valid():
            atividade = form.save(commit=False)
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