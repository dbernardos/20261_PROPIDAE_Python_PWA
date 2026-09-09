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
    # Administrador 1
    user_admin, created_admin = User.objects.get_or_create(
        username="admin_eventos",
        defaults={
            "email": "admin@sea.com",
            "first_name": "Carlos",
            "last_name": "Eduardo",
            "is_staff": True,
            "is_superuser": True
        }
    )
    if created_admin:
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

    # Administrador 2
    user_admin2, created_admin2 = User.objects.get_or_create(
        username="admin_eventos2",
        defaults={
            "email": "admin2@sea.com",
            "first_name": "Ana",
            "last_name": "Silva",
            "is_staff": True,
            "is_superuser": True
        }
    )
    if created_admin2:
        user_admin2.set_password("admin123")
        user_admin2.save()

    usuario_admin2, _ = Usuario.objects.get_or_create(
        user_django=user_admin2,
        defaults={
            "nome": "Ana Silva",
            "email": "admin2@sea.com",
            "cpf": "222.111.222-33",
            "telefone": "(11) 98888-1111",
            "dataNascimento": date(1999, 10, 11),
            "cargo": "Projetista de Sistemas",
            "formacao": "Engenharia de Computação",
            "empresa": "SEA Corp",
            "biografia": "Gestor do sistema de eventos."
        }
    )

    # Administrador 3
    user_admin3, created_admin3 = User.objects.get_or_create(
        username="admin_eventos3",
        defaults={
            "email": "admin3@sea.com",
            "first_name": "Fernando",
            "last_name": "dos Santos",
            "is_staff": True,
            "is_superuser": True
        }
    )
    if created_admin3:
        user_admin3.set_password("admin123")
        user_admin3.save()

    usuario_admin3, _ = Usuario.objects.get_or_create(
        user_django=user_admin3,
        defaults={
            "nome": "Fernando dos Santos",
            "email": "admin3@sea.com",
            "cpf": "333.222.111-00",
            "telefone": "(11) 97777-0004",
            "dataNascimento": date(1995, 7, 20),
            "cargo": "Adminstrador de Negócios",
            "formacao": "Administração",
            "empresa": "SEA Corp",
            "biografia": "Gestor do sistema de eventos."
        }
    )



    # Palestrante 1
    user_palestrante, created_palestrante = User.objects.get_or_create(
        username="mariana_docente",
        defaults={
            "email": "mariana@universidade.edu.br",
            "first_name": "Mariana",
            "last_name": "Lima"
        }
    )

    if created_palestrante:
        user_palestrante.set_password('palestrante123')
        user_palestrante.save()

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

    # Palestrante 2
    user_palestrante2, created_palestrante2 = User.objects.get_or_create(
        username="joao_docente",
        defaults={
            "email": "joao@universidade.edu.br",
            "first_name": "João",
            "last_name": "Silveira"
        }
    )

    if created_palestrante2:
            user_palestrante2.set_password('palestrante123')
            user_palestrante2.save()
    
    usuario_palestrante2, _ = Usuario.objects.get_or_create(
            user_django=user_palestrante2,
            defaults={
                "nome": "João Silveira",
                "email": "joao@universidade.edu.br",
                "cpf": "222.333.444-55",
                "telefone": "(11) 97777-0004",
                "dataNascimento": date(1992, 7, 20),
                "cargo": "Professor",
                "formacao": "Mestre em Ciência da Dados",
                "empresa": "Tech University",
                "biografia": "Entusiasta de Inteligência Artificial e Análise de Dados."
            }
        )

    # Participante / Aluno 1 
    user_aluno, created_aluno = User.objects.get_or_create(
        username="lucas_aluno",
        defaults={
            "email": "lucas@estudante.edu.br",
            "first_name": "Lucas",
            "last_name": "Mendes"
        }
    )

    if created_aluno:
        user_aluno.set_password('aluno123')
        user_aluno.save()

    usuario_aluno, _ = Usuario.objects.get_or_create(
        user_django=user_aluno,
        defaults={
            "nome": "Lucas Mendes",
            "email": "lucas@estudante.edu.br",
            "cpf": "222.555.444-55",
            "telefone": "(11) 97777-0003",
            "dataNascimento": date(2001, 3, 15),
            "cargo": "Desenvolvedor Junior",
            "formacao": "Graduando em Sistemas de Informação",
            "empresa": "Startup Dev",
            "biografia": "Estudante apaixonado por testes de código e automação."
        }
    )

    # Participante / Aluno 2
    user_aluno2, created_aluno2 = User.objects.get_or_create(
        username="joana_aluno",
        defaults={
            "email": "joana@estudante.edu.br",
            "first_name": "Joana",
            "last_name": "Muller"
        }
    )

    if created_aluno2:
        user_aluno2.set_password('aluno123')
        user_aluno2.save()

    usuario_aluno2, _ = Usuario.objects.get_or_create(
        user_django=user_aluno2,
        defaults={
            "nome": "Joana Muller",
            "email": "joana@estudante.edu.br",
            "cpf": "333.444.555-66",
            "telefone": "(11) 98888-0003",
            "dataNascimento": date(2001, 3, 15),
            "cargo": "Desenvolvedor Junior",
            "formacao": "Graduando em Engenharia de Software",
            "empresa": "",
            "biografia": "Estudante."
        }
    )

    # -------------------------------------------------------------
    # 2. APOIADORES
    # -------------------------------------------------------------
    apoiador_1, _ = Apoiador.objects.get_or_create(nome="Conselho de Tecnologia")
    apoiador_2, _ = Apoiador.objects.get_or_create(nome="Tech Innovation Lab")
    apoiador_3, _ = Apoiador.objects.get_or_create(nome="Instituto Federal de Santa Catarina")

    # -------------------------------------------------------------
    # 3. EVENTO
    # -------------------------------------------------------------


    #evento 1
    hoje = date.today()
    evento, _ = Evento.objects.get_or_create(
        nome="Semana Acadêmica de Tecnologia 2026",
        defaults={
            "administrador": usuario_admin,
            "descricao": "Evento focado em tecnologia, inovação e desafios práticos.",
            "emailContato": "contato@semanaacademica.com",
            "local": "Universidade Tecnologica do Paraná - Curitiba ",
            "dataInicio": hoje,
            "dataFim": hoje + timedelta(days=4),
            "tipoEvento": tipoEvento.SEMANA,
            "eventoMultiplo": True,
            "eventoPublico": True,
        }
    )
    evento.apoiadores.add(apoiador_1, apoiador_2)

    
    #evento 2
    hoje = date.today()
    evento2, _ = Evento.objects.get_or_create(
        nome="Palestra Internacional de Administração 2026",
        defaults={
            "administrador": usuario_admin2,
            "descricao": "Palestra focada em administração, inovação e desafios práticos.",
            "emailContato": "contato@ifsc.com",
            "local": "Instituto Federal de Santa Catarina - Campus Florianópolis",
            "dataInicio": hoje,
            "dataFim": hoje + timedelta(days=4),
            "tipoEvento": tipoEvento.OUTRO,
            "eventoMultiplo": False,
            "eventoPublico": True,
        }
    )
    evento2.apoiadores.add(apoiador_3)

    #evento 3
    hoje = date.today()
    evento3, _ = Evento.objects.get_or_create(
        nome="Fórum de Gestão de Projetos de Tecnologia 2026",
        defaults={
            "administrador": usuario_admin2,
            "descricao": "Fórum dedicado à gestão de projetos em tecnologia.",
            "emailContato": "contato@ifsc.com",
            "local": "Instituto Federal de Santa Catarina - Campus Rau",
            "dataInicio": hoje,
            "dataFim": hoje + timedelta(days=4),
            "tipoEvento": tipoEvento.FORUM,
            "eventoMultiplo": False,
            "eventoPublico": True,
        }
    )
    evento3.apoiadores.add(apoiador_1, apoiador_2, apoiador_3)

    # -------------------------------------------------------------
    # 4. ATIVIDADES
    # -------------------------------------------------------------
    agora = timezone.now()

    #atividade 1
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

    #atividade 2
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

    #atividade 3
    atividade_palestra2, _ = Atividade.objects.get_or_create(
        nome="Palestra Internacional de Administração 2026",
        evento=evento2,
        defaults={
            "descricao": "Palestra focada em administração, inovação e desafios práticos.",
            "tipoAtividade": tipoAtividade.PALESTRA,
            "complementoLocal": "Sala 05 - Bloco C",
            "horaInicio": agora + timedelta(days=1, hours=2),
            "horaFim": agora + timedelta(days=1, hours=6),
            "limitePessoas": 45,
        }
    )

    #atividade 4
    atividade_forum, _ = Atividade.objects.get_or_create(
        nome="Fórum: Gestão de Projetos em Tecnologia",
        evento=evento3,
        defaults={
            "descricao": "Fórum dedicado à gestão de projetos em tecnologia.",
            "tipoAtividade": tipoAtividade.FORUM,
            "complementoLocal": "Auditório Central - Bloco A",
            "horaInicio": agora + timedelta(days=1, hours=2),
            "horaFim": agora + timedelta(days=1, hours=6),
            "limitePessoas": 80,
        }
    )

    # -------------------------------------------------------------
    # 5. INSCRIÇÕES
    # -------------------------------------------------------------

    #inscrição de palestrantes
    inscricao_palestrante, _ = Inscricao.objects.get_or_create(
        usuario_id=usuario_palestrante.id,
        evento=evento
    )

    inscricao_palestrante2, _ = Inscricao.objects.get_or_create(
            usuario_id=usuario_palestrante2.id,
            evento=evento2
    )

    inscricao_palestrante3, _ = Inscricao.objects.get_or_create(
            usuario_id=usuario_palestrante2.id,
            evento=evento3
    )

    #Inscrição de 'alunos'
    inscricao_aluno, _ = Inscricao.objects.get_or_create(
        usuario_id=usuario_aluno.id,
        evento=evento
    )

    inscricao_aluno2, _ = Inscricao.objects.get_or_create(
        usuario_id=usuario_aluno2.id,
        evento=evento
    )

    inscricao_aluno3, _ = Inscricao.objects.get_or_create(
        usuario_id=usuario_aluno2.id,
        evento=evento2
    )




    # -------------------------------------------------------------
    # 6. PARTICIPAÇÕES NAS ATIVIDADES
    # -------------------------------------------------------------

    #Participações de Palestrantes
    Participa.objects.get_or_create(
        inscricao=inscricao_palestrante,
        atividade=atividade_palestra,
        defaults={"funcao": StatusParticipa.PALESTRANTE}
    )

    Participa.objects.get_or_create(
            inscricao=inscricao_palestrante2,
            atividade=atividade_palestra2,
            defaults={"funcao": StatusParticipa.PALESTRANTE}
    )

    #Participações de Alunos / Participantes
    participacao_aluno, _ = Participa.objects.get_or_create(
        inscricao=inscricao_aluno,
        atividade=atividade_palestra,
        defaults={"funcao": StatusParticipa.PARTICIPANTE}
    )

    participacao_aluno2, _ = Participa.objects.get_or_create(
        inscricao=inscricao_aluno2,
        atividade=atividade_palestra,
        defaults={"funcao": StatusParticipa.PARTICIPANTE}
    )

    participacao_aluno3, _ = Participa.objects.get_or_create(
        inscricao=inscricao_aluno2,
        atividade=atividade_oficina,
        defaults={"funcao": StatusParticipa.PARTICIPANTE}
    )

    participacao_aluno4, _ = Participa.objects.get_or_create(
        inscricao=inscricao_aluno3,
        atividade=atividade_palestra2,
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

    quiz_3, _ = Quiz.objects.get_or_create(
            numero=3,
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

    # Resposta 3 (Fora da faixa: incorreto)
    '''    resposta_3, _ = Resposta.objects.get_or_create(
            participa=participacao_aluno2,
            quiz=quiz_3,
            defaults={
                "valor_resposta": Decimal("45.00"),
            }
        )
        resposta_3.verificar_resposta()
    '''

    print("População do banco de dados concluída com sucesso!")

if __name__ == "__main__":
    popular_banco()