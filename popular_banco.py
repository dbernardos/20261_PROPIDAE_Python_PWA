import os
import django
from datetime import date, timedelta
from decimal import Decimal

# Configura o ambiente Django com a settings do seu projeto
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SEA.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth import get_user_model

# TODO: Ajuste as importações de acordo com os nomes dos seus apps
# Exemplo se forem apps separados:
# from app_login.models import Usuario
# from app_evento.models import Apoiador, Evento, Atividade, Inscricao, Participa, tipoEvento, tipoAtividade, StatusParticipa
# from app_quiz.models import Quiz, Resposta

from app_login.models import (
    Usuario,
)

from app_evento.models import (
    Apoiador,
    Evento,
    Atividade,
    Inscricao,
    Participa,
    tipoEvento,
    tipoAtividade,
    StatusParticipa
)

from app_quiz.models import (
    Quiz,
    Resposta
)

User = get_user_model()

def popular_banco():
    print("Iniciando povoamento completo do banco de dados...")

    # -------------------------------------------------------------
    # 1. USUÁRIOS E PERFIS (User + Usuario)
    # -------------------------------------------------------------
    # Administrador
    user_admin, _ = User.objects.get_or_create(
        username="admin_eventos",
        defaults={
            "email": "admin@sea.com",
            "first_name": "Carlos",
            "last_name": "Eduardo",
            "is_staff": True,
            "is_superuser": True
        }
    )
    if not user_admin.has_usable_password():
        user_admin.set_password("admin123")
        user_admin.save()

    usuario_admin, _ = Usuario.objects.get_or_create(
        user_django=user_admin,
        defaults={
            "nome": "Carlos Eduardo",
            "email": "admin@sea.com",
            "cpf": "000.111.222-33",
            "telefone": "(11) 99999-0001",
            "dataNascimento": date(1988, 5, 12),
            "cargo": "Administrador de Sistemas",
            "formacao": "Engenharia de Software",
            "empresa": "SEA Corp",
            "biografia": "Gestor principal do sistema de eventos."
        }
    )

    # Palestrante
    user_palestrante, _ = User.objects.get_or_create(
        username="mariana_docente",
        defaults={
            "email": "mariana@universidade.edu.br",
            "first_name": "Mariana",
            "last_name": "Lima"
        }
    )
    usuario_palestrante, _ = Usuario.objects.get_or_create(
        user_django=user_palestrante,
        defaults={
            "nome": "Mariana Lima",
            "email": "mariana@universidade.edu.br",
            "cpf": "111.222.333-44",
            "telefone": "(11) 98888-0002",
            "dataNascimento": date(1992, 8, 24),
            "cargo": "Professora / Pesquisadora",
            "formacao": "Doutorado em Ciência da Computação",
            "empresa": "Tech University",
            "biografia": "Entusiasta de Inteligência Artificial e Engenharia de Software."
        }
    )

    # Participante / Aluno
    user_aluno, _ = User.objects.get_or_create(
        username="lucas_aluno",
        defaults={
            "email": "lucas@estudante.edu.br",
            "first_name": "Lucas",
            "last_name": "Mendes"
        }
    )
    usuario_aluno, _ = Usuario.objects.get_or_create(
        user_django=user_aluno,
        defaults={
            "nome": "Lucas Mendes",
            "email": "lucas@estudante.edu.br",
            "cpf": "222.333.444-55",
            "telefone": "(11) 97777-0003",
            "dataNascimento": date(2001, 3, 15),
            "cargo": "Desenvolvedor Junior",
            "formacao": "Graduando em Sistemas de Informação",
            "empresa": "Startup Dev",
            "biografia": "Estudante apaixonado por testes de código e automação."
        }
    )

    # -------------------------------------------------------------
    # 2. APOIADORES
    # -------------------------------------------------------------
    apoiador_1, _ = Apoiador.objects.get_or_create(nome="Conselho de Tecnologia")
    apoiador_2, _ = Apoiador.objects.get_or_create(nome="Tech Innovation Lab")

    # -------------------------------------------------------------
    # 3. EVENTO
    # -------------------------------------------------------------
    hoje = date.today()
    evento, _ = Evento.objects.get_or_create(
        nome="Semana Acadêmica de Tecnologia 2026",
        defaults={
            "administrador": usuario_admin.id,
            "descricao": "Evento focado em tecnologia, inovação e desafios práticos.",
            "emailContato": "contato@semanaacademica.com",
            "local": "Campus Central - Bloco A",
            "dataInicio": hoje,
            "dataFim": hoje + timedelta(days=4),
            "tipoEvento": tipoEvento.SEMANA,
            "eventoMultiplo": True,
            "eventoPublico": True,
        }
    )
    evento.apoiadores.add(apoiador_1, apoiador_2)

    # -------------------------------------------------------------
    # 4. ATIVIDADES
    # -------------------------------------------------------------
    agora = timezone.now()

    atividade_palestra, _ = Atividade.objects.get_or_create(
        nome="Keynote: Inteligência Computacional no Diagnóstico",
        evento=evento,
        defaults={
            "descricao": "Palestra introdutória aos desafios tecnológicos atuais.",
            "tipoAtividade": tipoAtividade.PALESTRA,
            "complementoLocal": "Auditório Principal",
            "horaInicio": agora + timedelta(hours=1),
            "horaFim": agora + timedelta(hours=3),
            "limitePessoas": 200,
        }
    )

    atividade_oficina, _ = Atividade.objects.get_or_create(
        nome="Oficina: Desafio Prático de Calibração de Sensores",
        evento=evento,
        defaults={
            "descricao": "Atividade prática de laboratório com aferição de métricas.",
            "tipoAtividade": tipoAtividade.OFICINA,
            "complementoLocal": "Laboratório 04",
            "horaInicio": agora + timedelta(days=1, hours=2),
            "horaFim": agora + timedelta(days=1, hours=6),
            "limitePessoas": 30,
        }
    )

    # -------------------------------------------------------------
    # 5. INSCRIÇÕES
    # -------------------------------------------------------------
    inscricao_palestrante, _ = Inscricao.objects.get_or_create(
        usuario_id=usuario_palestrante.id,
        evento=evento
    )

    inscricao_aluno, _ = Inscricao.objects.get_or_create(
        usuario_id=usuario_aluno.id,
        evento=evento
    )

    # -------------------------------------------------------------
    # 6. PARTICIPAÇÕES NAS ATIVIDADES
    # -------------------------------------------------------------
    Participa.objects.get_or_create(
        inscricao=inscricao_palestrante,
        atividade=atividade_palestra,
        defaults={"funcao": StatusParticipa.PALESTRANTE}
    )

    participacao_aluno, _ = Participa.objects.get_or_create(
        inscricao=inscricao_aluno,
        atividade=atividade_oficina,
        defaults={"funcao": StatusParticipa.PARTICIPANTE}
    )

    # -------------------------------------------------------------
    # 7. QUIZZES / DESAFIOS
    # -------------------------------------------------------------
    quiz_1, _ = Quiz.objects.get_or_create(
        numero=1,
        defaults={
            "atividade": atividade_oficina,
            "titulo": "Aferição de Espessura do Material",
            "subtitulo": "Medição de precisão industrial",
            "pergunta": "Qual a espessura medida da amostra metálica disponibilizada na bancada 02?",
            "dica": "Utilize o paquímetro digital disponível no kit do laboratório.",
            "unidade_medida": "mm",
            "valor_minimo": Decimal("10.00"),
            "valor_maximo": Decimal("10.50"),
            "valor_ideal": Decimal("10.25"),
            "icone": "bi-rulers",
            "ativo": True,
        }
    )

    quiz_2, _ = Quiz.objects.get_or_create(
        numero=2,
        defaults={
            "atividade": atividade_oficina,
            "titulo": "Pesagem de Componente Químico",
            "subtitulo": "Teste de tolerância de dosagem",
            "pergunta": "Informe a massa total do reagente A após o processo de secagem.",
            "dica": "Considere a tara do recipiente de 5 gramas.",
            "unidade_medida": "gramas",
            "valor_minimo": Decimal("48.00"),
            "valor_maximo": Decimal("52.00"),
            "valor_ideal": Decimal("50.00"),
            "icone": "bi-trophy",
            "ativo": True,
        }
    )

    # -------------------------------------------------------------
    # 8. RESPOSTAS DOS QUIZZES
    # -------------------------------------------------------------
    # Resposta 1 (Dentro da faixa: correto)
    resposta_1, _ = Resposta.objects.get_or_create(
        participa=participacao_aluno,
        quiz=quiz_1,
        defaults={
            "valor_resposta": Decimal("10.20"),
        }
    )
    resposta_1.verificar_resposta()

    # Resposta 2 (Fora da faixa: incorreto)
    resposta_2, _ = Resposta.objects.get_or_create(
        participa=participacao_aluno,
        quiz=quiz_2,
        defaults={
            "valor_resposta": Decimal("42.50"),
        }
    )
    resposta_2.verificar_resposta()

    print("População do banco de dados concluída com sucesso!")

if __name__ == "__main__":
    popular_banco()