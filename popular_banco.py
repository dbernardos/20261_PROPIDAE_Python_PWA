import os
import shutil
from datetime import date, datetime, time, timedelta
from decimal import Decimal

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SEA.settings")
django.setup()

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from app_evento.models import (
    Apoiador,
    Atividade,
    Evento,
    Inscricao,
    Participa,
    StatusParticipa,
    tipoAtividade,
    tipoEvento,
)
from app_login.models import Usuario
from app_quiz.models import Quiz, Resposta

User = get_user_model()


# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def atribuir_imagem(instancia, campo: str, origem: str, pasta_destino: str) -> None:
    if not os.path.exists(origem):
        print(f"Aviso: imagem de origem não encontrada em '{origem}'")
        return

    nome_arquivo = os.path.basename(origem)
    destino_dir = os.path.join(settings.MEDIA_ROOT, pasta_destino)
    destino_completo = os.path.join(destino_dir, nome_arquivo)

    os.makedirs(destino_dir, exist_ok=True)
    if not os.path.exists(destino_completo):
        shutil.copy2(origem, destino_completo)

    setattr(instancia, campo, f"{pasta_destino}/{nome_arquivo}")
    instancia.save(update_fields=[campo])


def limpar_banco() -> None:
    print("Limpando dados anteriores do banco de dados...")
    with transaction.atomic():
        for model in (
            Resposta,
            Participa,
            Inscricao,
            Quiz,
            Atividade,
            Evento,
            Apoiador,
            Usuario,
            User,
        ):
            model.objects.all().delete()
    print("Banco limpo!")


def criar_usuario(dados: dict) -> Usuario:
    partes_nome = dados["nome"].split(" ", 1)
    first_name = partes_nome[0]
    last_name = partes_nome[1] if len(partes_nome) > 1 else ""
    is_admin = dados.get("is_admin", False)

    user, created = User.objects.get_or_create(
        username=dados["username"],
        defaults={
            "email": dados["email"],
            "first_name": first_name,
            "last_name": last_name,
            "is_staff": is_admin,
            "is_superuser": is_admin,
        },
    )
    if created:
        user.set_password(dados["senha"])
        user.save()

    usuario, _ = Usuario.objects.get_or_create(
        user_django=user,
        defaults={
            "nome": dados["nome"],
            "email": dados["email"],
            "cpf": dados["cpf"],
            "telefone": dados["telefone"],
            "dataNascimento": dados["nascimento"],
            "cargo": dados["cargo"],
            "formacao": dados["formacao"],
            "empresa": dados["empresa"],
            "biografia": dados["biografia"],
        },
    )
    atribuir_imagem(
        usuario,
        "fotoPerfil",
        f"media/popular_iniciais/perfis/{dados['foto']}",
        "perfis",
    )
    return usuario


def calcular_data_inscricao(evento, dias_antecedencia=3, hora=10, minuto=15):
    data_evento = evento.dataInicio
    if isinstance(data_evento, str):
        data_evento = date.fromisoformat(data_evento)
    elif isinstance(data_evento, datetime):
        data_evento = data_evento.date()

    data_alvo = data_evento - timedelta(days=dias_antecedencia)
    data_hora_inscricao = timezone.make_aware(datetime.combine(data_alvo, time(hora, minuto)))

    agora = timezone.now()
    if data_hora_inscricao > agora:
        data_hora_inscricao = agora - timedelta(days=dias_antecedencia)

    return data_hora_inscricao


def inscrever_e_participar(
    usuario,
    evento,
    atividades_inscritas=None,
    atividades_presentes=None,
    dias_antecedencia=3,
):
    if usuario.id == evento.administrador_id:
        return None

    conjunto_presentes = set(atividades_presentes or [])
    inscricao, _ = Inscricao.objects.get_or_create(
        usuario_id=usuario.id,
        evento=evento,
    )

    data_hora_inscricao = calcular_data_inscricao(evento, dias_antecedencia=dias_antecedencia)
    Inscricao.objects.filter(id=inscricao.id).update(dataHora=data_hora_inscricao)
    inscricao.refresh_from_db()

    for atividade in atividades_inscritas or []:
        esta_presente = atividade in conjunto_presentes
        data_hora_presenca = (atividade.horaInicio + timedelta(minutes=10)) if esta_presente else None
        Participa.objects.update_or_create(
            inscricao=inscricao,
            atividade=atividade,
            defaults={
                "funcao": StatusParticipa.PARTICIPANTE,
                "presente": esta_presente,
                "data_hora_presenca": data_hora_presenca,
            },
        )
    return inscricao


def criar_quiz(atividade, dados: dict) -> Quiz:
    quiz, _ = Quiz.objects.get_or_create(
        atividade=atividade,
        titulo=dados["titulo"],
        defaults={
            "tipo": dados["tipo"],
            "subtitulo": dados.get("subtitulo", ""),
            "pergunta": dados["pergunta"],
            "dica": dados.get("dica", ""),
            "unidade_medida": dados.get("unidade_medida", ""),
            "valor_minimo": dados.get("valor_minimo"),
            "valor_maximo": dados.get("valor_maximo"),
            "valor_ideal": dados.get("valor_ideal"),
            "opcao_a": dados.get("opcao_a"),
            "opcao_b": dados.get("opcao_b"),
            "opcao_c": dados.get("opcao_c"),
            "opcao_d": dados.get("opcao_d"),
            "alternativa_correta": dados.get("alternativa_correta"),
            "ativo": dados.get("ativo", True),
        },
    )
    return quiz


def registrar_resposta(
    usuario,
    atividade,
    quiz,
    valor_resposta=None,
    resposta_texto=None,
):
    if usuario.id == atividade.evento.administrador_id:
        return None

    inscricao = Inscricao.objects.filter(
        usuario_id=usuario.id,
        evento=atividade.evento,
    ).first()

    if not inscricao:
        inscricao = Inscricao.objects.create(
            usuario_id=usuario.id,
            evento=atividade.evento,
        )
        data_hora_inscricao = calcular_data_inscricao(atividade.evento, dias_antecedencia=2)
        Inscricao.objects.filter(id=inscricao.id).update(dataHora=data_hora_inscricao)
        inscricao.refresh_from_db()

    data_hora_presenca = atividade.horaInicio + timedelta(minutes=10)
    participacao, created = Participa.objects.get_or_create(
        inscricao=inscricao,
        atividade=atividade,
        defaults={
            "funcao": StatusParticipa.PARTICIPANTE,
            "presente": True,
            "data_hora_presenca": data_hora_presenca,
        },
    )

    if not created and (not participacao.presente or not participacao.data_hora_presenca):
        participacao.presente = True
        participacao.data_hora_presenca = data_hora_presenca
        participacao.save(update_fields=["presente", "data_hora_presenca"])

    correto = False
    status = "errado"
    valor_decimal = Decimal(str(valor_resposta)) if valor_resposta is not None else None
    resposta_normalizada = resposta_texto.strip().upper() if resposta_texto else None

    if quiz.tipo == "METRICA" and valor_decimal is not None:
        if quiz.valor_minimo <= valor_decimal <= quiz.valor_maximo:
            correto = True
            status = "certo" if valor_decimal == quiz.valor_ideal else "aproximado"
    elif quiz.tipo == "MULTIPLA" and resposta_normalizada:
        if resposta_normalizada == quiz.alternativa_correta:
            correto = True
            status = "certo"

    resposta, _ = Resposta.objects.update_or_create(
        participa=participacao,
        quiz=quiz,
        defaults={
            "valor_resposta": valor_decimal,
            "resposta_texto": resposta_normalizada,
            "correto": correto,
            "completo": True,
            "status": status,
        },
    )
    return resposta


# =============================================================================
# DADOS DE POVOAMENTO
# =============================================================================

DADOS_USUARIOS = {
    # Administradores
    "admin_carlos": {
        "username": "admin_eventos",
        "senha": "ifsc1234",
        "nome": "Carlos Eduardo",
        "email": "admin@sea.com",
        "cpf": "921.370.449-60",
        "telefone": "(11) 99999-0001",
        "nascimento": date(1988, 5, 12),
        "cargo": "Administrador de Sistemas",
        "formacao": "Engenharia de Software",
        "empresa": "SEA Corp",
        "biografia": "Gestor principal do sistema de eventos.",
        "foto": "admin.png",
        "is_admin": True,
    },
    "admin_ana": {
        "username": "admin_eventos2",
        "senha": "ifsc1234",
        "nome": "Ana Silva",
        "email": "admin2@sea.com",
        "cpf": "417.453.189-76",
        "telefone": "(11) 98888-1111",
        "nascimento": date(1999, 10, 11),
        "cargo": "Projetista de Sistemas",
        "formacao": "Engenharia de Computação",
        "empresa": "SEA Corp",
        "biografia": "Gestora do sistema de eventos.",
        "foto": "admin2.png",
        "is_admin": True,
    },
    "admin_fernando": {
        "username": "admin_eventos3",
        "senha": "ifsc1234",
        "nome": "Fernando dos Santos",
        "email": "admin3@sea.com",
        "cpf": "532.729.919-80",
        "telefone": "(11) 97777-0004",
        "nascimento": date(1995, 7, 20),
        "cargo": "Administrador de Negócios",
        "formacao": "Administração",
        "empresa": "SEA Corp",
        "biografia": "Gestor do sistema de eventos.",
        "foto": "admin3.png",
        "is_admin": True,
    },
    "admin_geraldo": {
        "username": "admin_eventos4",
        "senha": "ifsc1234",
        "nome": "Geraldo Gomes",
        "email": "admin4@sea.com",
        "cpf": "155.340.800-43",
        "telefone": "(11) 97777-0005",
        "nascimento": date(1989, 9, 23),
        "cargo": "Administrador de Negócios",
        "formacao": "Administração",
        "empresa": "IFSC",
        "biografia": "Gestor do sistema de eventos.",
        "foto": "admin4.png",
        "is_admin": True,
    },
    # Participantes
    "mariana_lima": {
        "username": "mariana.li",
        "senha": "participante1",
        "nome": "Mariana Lima",
        "email": "mariana.li@universidade.edu.br",
        "cpf": "705.507.149-60",
        "telefone": "(49) 93226-2845",
        "nascimento": date(1992, 8, 24),
        "cargo": "Pesquisadora",
        "formacao": "Doutorado em Ciência da Computação",
        "empresa": "Intelbras",
        "biografia": "Olá! Sou Mariana Lima, Doutora em Ciência da Computação, faço parte da equipe de pesquisa da Intelbras. Sou apaixonada por Inteligência Artificial e Engenharia de Software, dedicando minha carreira a explorar como a tecnologia pode resolver problemas reais e transformar o futuro.",
        "foto": "participante1.png",
    },
    "joao_silveira": {
        "username": "joao.si",
        "senha": "participante2",
        "nome": "João Silveira",
        "email": "joao.si@universidade.edu.br",
        "cpf": "458.696.188-00",
        "telefone": "(49) 3226-2845",
        "nascimento": date(1992, 7, 20),
        "cargo": "Professor",
        "formacao": "Mestre em Ciência de Dados",
        "empresa": "FIAP",
        "biografia": "👨‍🏫 Professor | FIAP\n🎓 Mestre em Ciência de Dados\n📊 Especialista em Análise de Dados",
        "foto": "participante2.png",
    },
    "lucas_mendes": {
        "username": "mendes_lucaaas",
        "senha": "participante3",
        "nome": "Lucas Mendes",
        "email": "lucas.des@estudante.edu.br",
        "cpf": "962.065.259-29",
        "telefone": "(45) 3761-2595",
        "nascimento": date(2001, 3, 15),
        "cargo": "Desenvolvedor Júnior",
        "formacao": "Graduando em Sistemas de Informação",
        "empresa": "Startup Equinox.io",
        "biografia": "Lucas Mendes é graduando em Sistemas de Informação e atua como Desenvolvedor Júnior na Startup Equinox.io.\nApaixonado por qualidade de software, dedica-se a testes de código e automação de processos.",
        "foto": "participante3.png",
    },
    "joana_muller": {
        "username": "joana_m",
        "senha": "participante4",
        "nome": "Joana Muller",
        "email": "joana.muller@estudante.edu.br",
        "cpf": "949.221.639-64",
        "telefone": "(48) 3775-8450",
        "nascimento": date(2000, 3, 15),
        "cargo": "Estudante",
        "formacao": "Graduanda em Engenharia de Software",
        "empresa": "",
        "biografia": "Joana Muller é graduanda em Engenharia de Software.\nApaixonada por desenvolvimento web e metodologias ágeis, dedica-se a projetos acadêmicos e inovação tecnológica.",
        "foto": "participante4.png",
    },
    "sofia_almeida": {
        "username": "sofia_ux",
        "senha": "participante5",
        "nome": "Sofia Almeida",
        "email": "sofia.almeida@gmail.com.br",
        "cpf": "233.324.679-05",
        "telefone": "(47) 99234-1122",
        "nascimento": date(1996, 4, 12),
        "cargo": "Product Designer (UX/UI)",
        "formacao": "Bacharela em Design Digital",
        "empresa": "Neogrid",
        "biografia": "Sofia Almeida é Bacharela em Design Digital e atua como Product Designer na Neogrid.\nEspecialista em experiência do usuário e interfaces acessíveis, transforma problemas complexos em jornadas intuitivas.",
        "foto": "participante5.png",
    },
    "rafael_costa": {
        "username": "dr_rafael_bio",
        "senha": "participante6",
        "nome": "Rafael Costa",
        "email": "rafael.costa96@outlook.com",
        "cpf": "352.314.089-72",
        "telefone": "(41) 98765-4321",
        "nascimento": date(1989, 9, 28),
        "cargo": "Pesquisador em Bioinformática",
        "formacao": "Doutor em Biotecnologia",
        "empresa": "Instituto Pequeno Príncipe",
        "biografia": "Rafael Costa é Doutor em Biotecnologia e atua como Pesquisador em Bioinformática.\nDedica-se à análise de dados genômicos e ao uso de algoritmos para acelerar diagnósticos na área da saúde.",
        "foto": "participante6.png",
    },
    "clara_nogueira": {
        "username": "clara_pm",
        "senha": "participante7",
        "nome": "Clara Nogueira",
        "email": "clara.nogueira@hotmail.com",
        "cpf": "325.744.429-03",
        "telefone": "(11) 98123-9876",
        "nascimento": date(1991, 1, 19),
        "cargo": "Gerente de Produto (PM)",
        "formacao": "MBA em Gestão de Projetos e Inovação",
        "empresa": "Asaas",
        "biografia": "Clara Nogueira possui MBA em Gestão de Projetos e atua como Gerente de Produto no Asaas.\nFocada em métricas de crescimento e metodologias ágeis, lidera equipes multidisciplinares no setor financeiro.",
        "foto": "participante7.png",
    },
    "thiago_martins": {
        "username": "thiago_lgpd",
        "senha": "participante8",
        "nome": "Thiago Martins",
        "email": "thiago.martins.adv@advdigital.com.br",
        "cpf": "086.927.799-54",
        "telefone": "(48) 99654-3210",
        "nascimento": date(1993, 6, 7),
        "cargo": "Consultor de Privacidade e DPO",
        "formacao": "Especialista em Direito Digital",
        "empresa": "RD Station",
        "biografia": "Thiago Martins é Especialista em Direito Digital e atua como Consultor de Privacidade na RD Station.\nAuxilia empresas na adequação à LGPD, governança de dados e segurança jurídica em ambientes digitais.",
        "foto": "participante8.png",
    },
    "fernanda_lima": {
        "username": "fernanda_growth",
        "senha": "participante9",
        "nome": "Fernanda Lima",
        "email": "fernanda.lima@gmail.com",
        "cpf": "045.876.659-32",
        "telefone": "(51) 99345-6789",
        "nascimento": date(1998, 12, 3),
        "cargo": "Analista de Growth Marketing",
        "formacao": "Graduada em Publicidade e Propaganda",
        "empresa": "Resultados Digitais",
        "biografia": "Fernanda Lima é Graduada em Publicidade e Propaganda e atua como Analista de Growth Marketing.\nApaixonada por análise de funil e aquisição de clientes, cria estratégias baseadas em dados para escalar negócios.",
        "foto": "participante9.png",
    },
    "pedro_henrique": {
        "username": "pedro_robotica",
        "senha": "participante10",
        "nome": "Pedro Henrique",
        "email": "pedro.henrique3@estudante.edu.br",
        "cpf": "166.310.429-84",
        "telefone": "(47) 98456-7890",
        "nascimento": date(2002, 8, 21),
        "cargo": "Bolsista de Iniciação Científica",
        "formacao": "Graduando em Engenharia Mecatrônica",
        "empresa": "Laboratório de Robótica UFSC",
        "biografia": "Pedro Henrique é graduando em Engenharia Mecatrônica e bolsista de iniciação científica.\nPesquisa sistemas embarcados e robótica autônoma, participando ativamente de competições universitárias.",
        "foto": "participante10.png",
    },
    "bruno_oliveira": {
        "username": "bruno_agro",
        "senha": "participante11",
        "nome": "Bruno Oliveira",
        "email": "brunoooliveira@gmail.com.br",
        "cpf": "562.363.479-64",
        "telefone": "(62) 99876-5432",
        "nascimento": date(1987, 2, 14),
        "cargo": "Coordenador de Inovação Agro",
        "formacao": "Mestre em Engenharia Agronômica",
        "empresa": "AgroTech Brasil",
        "biografia": "Bruno Oliveira é Mestre em Engenharia Agronômica e Coordenador de Inovação na AgroTech Brasil.\nTrabalha com agricultura de precisão e sensoriamento remoto para promover a sustentabilidade no campo.",
        "foto": "participante11.png",
    },
    "helena_ribeiro": {
        "username": "helena_psico",
        "senha": "participante12",
        "nome": "Helena Ribeiro",
        "email": "helena.ribeiro@rhcultura.com.br",
        "cpf": "364.343.809-50",
        "telefone": "(47) 99145-8822",
        "nascimento": date(1992, 5, 18),
        "cargo": "Psicóloga Organizacional",
        "formacao": "Especialista em Psicologia do Trabalho",
        "empresa": "Consultoria RH Cultura",
        "biografia": "Helena Ribeiro é Especialista em Psicologia do Trabalho e atua como Psicóloga Organizacional.\nDedica-se à saúde mental no ambiente corporativo, desenvolvimento de lideranças e cultura inclusiva.",
        "foto": "participante12.png",
    },
    "mateus_cardoso": {
        "username": "mateus_historia",
        "senha": "participante13",
        "nome": "Mateus Cardoso",
        "email": "mateus.cardoso@museuhistorico.org.br",
        "cpf": "410.119.129-88",
        "telefone": "(48) 98834-5511",
        "nascimento": date(1986, 10, 9),
        "cargo": "Historiador e Curador",
        "formacao": "Doutor em História Social",
        "empresa": "Fundação Cultural Catarinense",
        "biografia": "Mateus Cardoso é Doutor em História Social e atua como Historiador e Curador.\nPesquisa preservação de acervos digitais, memória urbana e políticas públicas de patrimônio cultural.",
        "foto": "participante13.png",
    },
    "juliana_barros": {
        "username": "juliana_socio",
        "senha": "participante14",
        "nome": "Juliana Barros",
        "email": "juliana.barros@observatoriosocial.org.br",
        "cpf": "372.785.819-23",
        "telefone": "(41) 99712-3344",
        "nascimento": date(1994, 7, 25),
        "cargo": "Analista de Impacto Social",
        "formacao": "Mestra em Sociologia Política",
        "empresa": "Instituto Cidades Sustentáveis",
        "biografia": "Juliana Barros é Mestra em Sociologia Política e atua como Analista de Impacto Social.\nTrabalha com indicadores sociais, participação cidadã e avaliação de projetos comunitários.",
        "foto": "participante14.png",
    },
    "gabriel_santos": {
        "username": "gabriel_letras",
        "senha": "participante15",
        "nome": "Gabriel Santos",
        "email": "gabriel.santos@editorasul.com.br",
        "cpf": "756.651.889-56",
        "telefone": "(51) 98421-7788",
        "nascimento": date(1990, 2, 11),
        "cargo": "Editor e Revisor Textual",
        "formacao": "Licenciado em Letras - Português e Inglês",
        "empresa": "Editora Horizonte",
        "biografia": "Gabriel Santos é Licenciado em Letras e atua como Editor e Revisor Textual na Editora Horizonte.\nApaixonado por literatura contemporânea e linguística aplicada, coordena publicações acadêmicas e literárias.",
        "foto": "participante15.jpg",
    },
    "patricia_gomes": {
        "username": "patricia_pedagoga",
        "senha": "participante16",
        "nome": "Patrícia Gomes",
        "email": "patricia.gomes@educacao.edu.br",
        "cpf": "530.981.499-06",
        "telefone": "(47) 99632-9900",
        "nascimento": date(1985, 11, 30),
        "cargo": "Coordenadora Pedagógica",
        "formacao": "Mestra em Educação e Inclusão",
        "empresa": "Colégio Inovação",
        "biografia": "Patrícia Gomes é Mestra em Educação e atua como Coordenadora Pedagógica no Colégio Inovação.\nEspecialista em metodologias ativas e educação inclusiva, apoia docentes na criação de currículos acessíveis.",
        "foto": "participante16.png",
    },
    "rodrigo_melo": {
        "username": "rodrigo_filosofia",
        "senha": "participante17",
        "nome": "Rodrigo Melo",
        "email": "rodrigo.melo@universidade.edu.br",
        "cpf": "987.805.929-45",
        "telefone": "(11) 98234-6677",
        "nascimento": date(1988, 3, 14),
        "cargo": "Professor de Ética e Filosofia",
        "formacao": "Doutor em Filosofia Contemporânea",
        "empresa": "Universidade Federal de Santa Catarina",
        "biografia": "Rodrigo Melo é Doutor em Filosofia Contemporânea e Professor Universitário.\nPesquisa ética aplicada à inteligência artificial, epistemologia e impactos filosóficos da era digital.",
        "foto": "participante17.jpg",
    },
    "amanda_castro": {
        "username": "amanda_social",
        "senha": "participante18",
        "nome": "Amanda Castro",
        "email": "amanda.castro@redesolidaria.ong.br",
        "cpf": "912.166.829-92",
        "telefone": "(49) 99543-2211",
        "nascimento": date(1995, 8, 4),
        "cargo": "Assistente Social",
        "formacao": "Bacharela em Serviço Social",
        "empresa": "ONG Rede Solidária",
        "biografia": "Amanda Castro é Bacharela em Serviço Social e atua na ONG Rede Solidária.\nFocada em direitos humanos e assistência comunitária, coordena programas de acolhimento e geração de renda.",
        "foto": "participante18.png",
    },
    "vinicius_teixeira": {
        "username": "vinicius_jornal",
        "senha": "participante19",
        "nome": "Vinícius Teixeira",
        "email": "vinicius.teixeira@outlook.com.br",
        "cpf": "980.018.659-08",
        "telefone": "(21) 98976-4433",
        "nascimento": date(1997, 9, 17),
        "cargo": "Jornalista Investigativo",
        "formacao": "Bacharel em Jornalismo",
        "empresa": "Portal Brasil com S",
        "biografia": "Vinícius Teixeira é Bacharel em Jornalismo e atua como Jornalista Investigativo.\nEspecializado em jornalismo de dados e checagem de fatos, produz reportagens sobre transparência pública.",
        "foto": "participante19.jpg",
    },
    "larissa_monteiro": {
        "username": "larissa_ri",
        "senha": "participante20",
        "nome": "Larissa Monteiro",
        "email": "larissa.monteiro087@estudante.edu.br",
        "cpf": "973.011.029-84",
        "telefone": "(61) 99123-7744",
        "nascimento": date(2003, 1, 29),
        "cargo": "",
        "formacao": "Graduanda em Relações Internacionais",
        "empresa": "",
        "biografia": "Larissa Monteiro é graduanda em Relações Internacionais e estagiária em Cooperação Internacional.\nInteressada em diplomacia cultural e comércio exterior, participa de simulações da ONU e grupos de pesquisa.",
        "foto": "participante20.png",
    },
     "izaque_Ribeiro": {
        "username": "Izake_colorado",
        "senha": "participante21",
        "nome": "Izaque Ribeiro",
        "email": "izaque.ribas172006@estudante.edu.br",
        "cpf": "367.216.540-91",
        "telefone": "(47) 2651-6761",
        "nascimento": date(2001, 12, 17),
        "cargo": "Chefe do Setor de Fabricação de Baterias de Alta Corrente",
        "formacao": "Analise e Desenvolvimento de Sistemas",
        "empresa": "Weg",
        "biografia": "Izaque Ribeiro é um torcedor fanático do colorado empenhado em seu trabalho e estudos.",
        "foto": "participante21.png",
    },
     "claudio_gabriel": {
        "username": "Izake_colorado",
        "senha": "participante22",
        "nome": "Izaque Ribeiro",
        "email": "claudio.cesar@estudante.edu.br",
        "cpf": "363.101.550-08",
        "telefone": "(47) 2133-0343",
        "nascimento": date(1999, 12, 17),
        "cargo": "Chefe de Estudo de Fabricação de Baterias de Baixa Corrente",
        "formacao": "Estudante",
        "empresa": "IFSC",
        "biografia": "Claudio Gabriel é um estudante assíduo na programação e gosta de RPG.",
        "foto": "participante22.png",
    },
     "leonardo_Rodrigues": {
        "username": "leonardorodri",
        "senha": "participante23",
        "nome": "Leonardo Rodrigues",
        "email": "leo.rodri@estudante.edu.br",
        "cpf": "566.851.930-93",
        "telefone": "(47) 2783-1339",
        "nascimento": date(2001, 7, 18),
        "cargo": "Estudante",
        "formacao": "Analise e Desenvolvimento de Sistemas",
        "empresa": "IFSC",
        "biografia": "Leonardo Rodrigues é um torcedor fanático do Grêmio e empenhado em suas tarefas.",
        "foto": "participante23.png",
    },
     "lucas_kret": {
        "username": "german_lukas",
        "senha": "participante24",
        "nome": "Lucas Kretschmar",
        "email": "lucas.krusadtsamclher@hotmail.com",
        "cpf": "654.505.530-56",
        "telefone": "(47) 3653-0962",
        "nascimento": date(2002, 10, 15),
        "cargo": "CEO da Besteam",
        "formacao": "Analise e Desenvolvimento de Sistemas",
        "empresa": "Weg",
        "biografia": "Lucas Kretschmar é germano-brasileiro natural de Berlim, é trabalhador.",
        "foto": "participante24.png",
    },
    "igor_henry": {
        "username": "higor_jawline",
        "senha": "participante25",
        "nome": "Ighor Henrique",
        "email": "higorheight@gmail.com",
        "cpf": "871.137.090-44",
        "telefone": "(47) 3243-6781",
        "nascimento": date(2003, 12, 18),
        "cargo": "Chefe do Setor de Fabricação Mecânica",
        "formacao": "Analise e Desenvolvimento de Sistemas",
        "empresa": "Weg",
        "biografia": "Ighor Henrique é um marcelandense dedicado.",
        "foto": "participante25.png",
    },
    "daniel_alb": {
        "username": "higor_jline",
        "senha": "participante26",
        "nome": "Daniel Albuquerque",
        "email": "dan@gmail.com",
        "cpf": "066.309.230-22",
        "telefone": "(49) 3587-8814",
        "nascimento": date(2006, 12, 15),
        "cargo": "Estudante",
        "formacao": "Analise e Desenvolvimento de Sistemas",
        "empresa": "IFSC",
        "biografia": "Daniel Albuquerque é um torcedor flamengo e estudante do IF.",
        "foto": "participante26.png",
    },
}

NOMES_APOIADORES = {
    "conselho_tecnologia": "Conselho de Tecnologia",
    "tech_innovation_lab": "Tech Innovation Lab",
    "ifsc": "Instituto Federal de Santa Catarina",
    "fundacao_pesquisa_saude": "Fundação Catarinense de Pesquisa e Saúde",
    "associacao_energias_limpas": "Associação Sul-Brasileira de Energias Limpas",
    "instituto_direito_digital": "Instituto Brasileiro de Direito Digital (IBDD)",
    "conselho_arquitetura_design": "Conselho de Arquitetura e Design Criativo",
    "cooperativa_agroinova": "Cooperativa AgroInova Sul",
    "federacao_industrias_automacao": "Federação das Indústrias e Automação (FIASC)",
    "secretaria_cultura_turismo": "Secretaria Regional de Cultura e Turismo",
}


# =============================================================================
# FUNÇÃO PRINCIPAL DE POVOAMENTO
# =============================================================================

def popular_banco() -> None:
    limpar_banco()
    print("Iniciando povoamento completo do banco de dados...")

    # 1. Usuários
    usuarios = {
        chave: criar_usuario(dados)
        for chave, dados in DADOS_USUARIOS.items()
    }

    # 2. Apoiadores
    apoiadores = {
        chave: Apoiador.objects.get_or_create(nome=nome)[0]
        for chave, nome in NOMES_APOIADORES.items()
    }

    # 3. Eventos
    agora = timezone.localtime(timezone.now())
    hoje = agora.replace(hour=0, minute=0, second=0, microsecond=0)

    dados_eventos = {
        "semana_tecnologia": {
            "nome": "Semana Acadêmica de Tecnologia 2026",
            "administrador": usuarios["admin_carlos"],
            "descricao": "Evento focado em tecnologia, inovação e desafios práticos.",
            "emailContato": "contato@semanaacademica.com",
            "local": "Universidade Tecnológica do Paraná - Curitiba",
            "dataInicio": hoje - timedelta(days=2),
            "dataFim": hoje + timedelta(days=3),
            "tipoEvento": tipoEvento.SEMANA,
            "apoiadores": ["conselho_tecnologia", "tech_innovation_lab", "ifsc"],
            "banner": "evento1.png",
        },
        "palestra_administracao": {
            "nome": "Palestra Internacional de Administração 2026",
            "administrador": usuarios["admin_carlos"],
            "descricao": "Palestra focada em administração, inovação e desafios práticos.",
            "emailContato": "contato@ifsc.com",
            "local": "Instituto Federal de Santa Catarina - Campus Florianópolis",
            "dataInicio": hoje - timedelta(days=14),
            "dataFim": hoje - timedelta(days=10),
            "tipoEvento": tipoEvento.OUTRO,
            "apoiadores": ["ifsc"],
            "banner": "evento2.png",
        },
        "forum_gestao_projetos": {
            "nome": "Fórum de Gestão de Projetos de Tecnologia 2026",
            "administrador": usuarios["admin_carlos"],
            "descricao": "Fórum dedicado à gestão de projetos em tecnologia.",
            "emailContato": "contato@ifsc.com",
            "local": "Instituto Federal de Santa Catarina - Campus Rau",
            "dataInicio": hoje - timedelta(days=8),
            "dataFim": hoje - timedelta(days=4),
            "tipoEvento": tipoEvento.FORUM,
            "apoiadores": ["conselho_tecnologia", "ifsc"],
            "banner": "evento3.png",
        },
        "congresso_saude_bio": {
            "nome": "Congresso Brasileiro de Saúde e Biotecnologia 2026",
            "administrador": usuarios["admin_carlos"],
            "descricao": "Discussões sobre avanços clínicos, telemedicina e pesquisas em biotecnologia.",
            "emailContato": "contato@saudebio2026.com.br",
            "local": "Universidade Federal de Santa Catarina - Florianópolis",
            "dataInicio": hoje - timedelta(days=2),
            "dataFim": hoje + timedelta(days=3),
            "tipoEvento": tipoEvento.OUTRO,
            "apoiadores": ["fundacao_pesquisa_saude", "tech_innovation_lab"],
            "banner": "evento4.jpg",
        },
        "simposio_energias": {
            "nome": "Simpósio Sul de Energias Renováveis e Sustentabilidade",
            "administrador": usuarios["admin_carlos"],
            "descricao": "Encontro voltado para transição energética, ESG e preservação ambiental.",
            "emailContato": "simposio@energiasul.org.br",
            "local": "Centro de Convenções Expoville - Joinville",
            "dataInicio": hoje - timedelta(days=22),
            "dataFim": hoje - timedelta(days=20),
            "tipoEvento": tipoEvento.SIMPOSIO,
            "apoiadores": ["associacao_energias_limpas"],
            "banner": "evento5.jpg",
        },
        "forum_direito_digital": {
            "nome": "Fórum Nacional de Direito Digital e Proteção de Dados",
            "administrador": usuarios["admin_carlos"],
            "descricao": "Debates sobre LGPD, inteligência artificial e regulação jurídica no ambiente digital.",
            "emailContato": "eventos@direitodigital2026.com",
            "local": "Pontifícia Universidade Católica do Paraná - Curitiba",
            "dataInicio": hoje - timedelta(days=1),
            "dataFim": hoje + timedelta(days=2),
            "tipoEvento": tipoEvento.FORUM,
            "apoiadores": ["instituto_direito_digital", "conselho_tecnologia"],
            "banner": "evento6.jpg",
        },
        "semana_design_arquitetura": {
            "nome": "Semana de Design, Arquitetura e Urbanismo Criativo",
            "administrador": usuarios["admin_carlos"],
            "descricao": "Oficinas práticas, exposições e palestras sobre cidades inteligentes e design de produto.",
            "emailContato": "contato@semanadesign.edu.br",
            "local": "Universidade do Estado de Santa Catarina - Joinville",
            "dataInicio": hoje + timedelta(days=7),
            "dataFim": hoje + timedelta(days=12),
            "tipoEvento": tipoEvento.SEMANA,
            "apoiadores": ["conselho_arquitetura_design"],
            "banner": "evento7.jpg",
        },
        "feira_agronegocio": {
            "nome": "Feira de Inovação no Agronegócio e Agricultura 4.0",
            "administrador": usuarios["admin_ana"],
            "descricao": "Apresentação de drones, automação rural e soluções sustentáveis para o campo.",
            "emailContato": "agro40@feiraagro.com.br",
            "local": "Parque de Exposições Efapi - Chapecó",
            "dataInicio": hoje + timedelta(days=16),
            "dataFim": hoje + timedelta(days=19),
            "tipoEvento": tipoEvento.FEIRA,
            "apoiadores": ["cooperativa_agroinova", "tech_innovation_lab", "associacao_energias_limpas"],
            "banner": "evento8.jpg",
        },
        "semana_engenharia_mecanica": {
            "nome": "Semana de Engenharia Mecânica e Automação Industrial",
            "administrador": usuarios["admin_ana"],
            "descricao": "Minicursos de robótica, manufatura aditiva e visitas técnicas às indústrias da região.",
            "emailContato": "engenharia@ifsc.edu.br",
            "local": "Instituto Federal de Santa Catarina - Campus Jaraguá do Sul",
            "dataInicio": hoje + timedelta(days=25),
            "dataFim": hoje + timedelta(days=29),
            "tipoEvento": tipoEvento.SEMANA,
            "apoiadores": ["federacao_industrias_automacao", "ifsc", "tech_innovation_lab"],
            "banner": "evento9.jpg",
        },
        "forum_gastronomia_turismo": {
            "nome": "Fórum Sul-Brasileiro de Gastronomia e Turismo Cultural",
            "administrador": usuarios["admin_ana"],
            "descricao": "Cozinha show, valorização de ingredientes regionais e estratégias para o turismo local.",
            "emailContato": "contato@gastroturismo.com.br",
            "local": "Parque Vila Germânica - Blumenau",
            "dataInicio": hoje + timedelta(days=38),
            "dataFim": hoje + timedelta(days=40),
            "tipoEvento": tipoEvento.FORUM,
            "apoiadores": [],
            "banner": "evento10.jpg",
        },
        "apresentacao_pi2": {
            "nome": "Apresentação dos Projetos de PI 2",
            "administrador": usuarios["admin_geraldo"],
            "descricao": "Apresentação dos Projetos Integradores das Turmas do terceiro e quarto semestre do Curso Técnico de Desenvolvimento de Sistemas.",
            "emailContato": "contato@ifsc.edu.br",
            "local": "IFSC - RAU",
            "dataInicio": date(2006, 11, 26),
            "dataFim": date(2006, 11, 27),
            "tipoEvento": tipoEvento.OUTRO,
            "apoiadores": ["ifsc"],
            "banner": "evento11.jpg",
        },
    }

    eventos = {}
    for chave, dados_evento in dados_eventos.items():
        evento, _ = Evento.objects.get_or_create(
            nome=dados_evento["nome"],
            defaults={
                "administrador": dados_evento["administrador"],
                "descricao": dados_evento["descricao"],
                "emailContato": dados_evento["emailContato"],
                "local": dados_evento["local"],
                "dataInicio": dados_evento["dataInicio"],
                "dataFim": dados_evento["dataFim"],
                "tipoEvento": dados_evento["tipoEvento"],
            },
        )
        evento.apoiadores.set([apoiadores[chave_ap] for chave_ap in dados_evento["apoiadores"]])
        atribuir_imagem(
            evento,
            "imagemBanner",
            f"media/popular_iniciais/banners/{dados_evento['banner']}",
            "banners",
        )
        eventos[chave] = evento

    # 4. Atividades
    dados_atividades = {
        # Semana Acadêmica de Tecnologia
        "tec_keynote_diagnostico": (
            eventos["semana_tecnologia"],
            "Keynote: Inteligência Computacional no Diagnóstico",
            "Palestra introdutória aos desafios tecnológicos atuais.",
            tipoAtividade.PALESTRA,
            "Auditório Principal",
            agora - timedelta(minutes=30),
            agora + timedelta(hours=2),
            200,
        ),
        "tec_oficina_sensores": (
            eventos["semana_tecnologia"],
            "Oficina: Desafio Prático de Calibração de Sensores",
            "Atividade prática de laboratório com aferição de métricas.",
            tipoAtividade.OFICINA,
            "Laboratório 04",
            agora + timedelta(days=1, hours=2),
            agora + timedelta(days=1, hours=6),
            30,
        ),
        "tec_oficina_docker_k8s": (
            eventos["semana_tecnologia"],
            "Oficina: Arquitetura de Microsserviços com Docker e Kubernetes",
            "Deploy prático de containers e orquestração em ambiente cloud.",
            tipoAtividade.OFICINA,
            "Laboratório de Redes - Bloco B",
            agora - timedelta(days=1, hours=4),
            agora - timedelta(days=1, hours=1),
            35,
        ),
        "tec_forum_carreira_ti": (
            eventos["semana_tecnologia"],
            "Fórum: Carreira Internacional e Trabalho Remoto na Área de TI",
            "Bate-papo com engenheiros de software atuando em empresas globais.",
            tipoAtividade.FORUM,
            "Miniauditório 02",
            agora + timedelta(days=2, hours=1),
            agora + timedelta(days=2, hours=3),
            90,
        ),
        # Palestra Internacional de Administração
        "adm_palestra_internacional": (
            eventos["palestra_administracao"],
            "Palestra Internacional de Administração 2026",
            "Palestra focada em administração, inovação e desafios práticos.",
            tipoAtividade.PALESTRA,
            "Sala 05 - Bloco C",
            agora - timedelta(days=13, hours=3),
            agora - timedelta(days=13, hours=1),
            45,
        ),
        "adm_oficina_okrs": (
            eventos["palestra_administracao"],
            "Oficina: Planejamento Estratégico e OKRs para Startups",
            "Dinâmica prática de definição de metas e indicadores de desempenho.",
            tipoAtividade.OFICINA,
            "Sala de Metodologias Ativas",
            agora - timedelta(days=11, hours=4),
            agora - timedelta(days=11, hours=1),
            30,
        ),
        # Fórum de Gestão de Projetos
        "proj_forum_gestao": (
            eventos["forum_gestao_projetos"],
            "Fórum: Gestão de Projetos em Tecnologia",
            "Fórum dedicado à gestão de projetos em tecnologia.",
            tipoAtividade.FORUM,
            "Auditório Central - Bloco A",
            agora - timedelta(days=7, hours=4),
            agora - timedelta(days=7, hours=1),
            80,
        ),
        "proj_oficina_kanban": (
            eventos["forum_gestao_projetos"],
            "Oficina: Métricas Ágeis, Kanban e Previsibilidade de Entregas",
            "Simulação de fluxo contínuo utilizando Lead Time e Throughput.",
            tipoAtividade.OFICINA,
            "Laboratório 02 - Bloco B",
            agora - timedelta(days=6, hours=3),
            agora - timedelta(days=6),
            40,
        ),
        "proj_palestra_riscos": (
            eventos["forum_gestao_projetos"],
            "Palestra: Gestão de Riscos e Orçamentos em Contratos de Software",
            "Estudos de caso sobre mitigação de escopo aberto e precificação.",
            tipoAtividade.PALESTRA,
            "Auditório Central - Bloco A",
            agora - timedelta(days=5, hours=2),
            agora - timedelta(days=5),
            100,
        ),
        # Congresso de Saúde e Biotecnologia
        "saude_palestra_crispr": (
            eventos["congresso_saude_bio"],
            "Palestra: Edição Genética CRISPR e Terapias Avançadas",
            "Panorama das pesquisas clínicas recentes em terapia gênica.",
            tipoAtividade.PALESTRA,
            "Auditório Garapuvu",
            agora - timedelta(days=1, hours=3),
            agora - timedelta(days=1, hours=1),
            250,
        ),
        "saude_forum_telemedicina": (
            eventos["congresso_saude_bio"],
            "Fórum: Desafios Éticos e Regulatórios da Telemedicina no SUS",
            "Debate com gestores hospitalares e pesquisadores de saúde pública.",
            tipoAtividade.FORUM,
            "Sala Plenária 01",
            agora - timedelta(minutes=45),
            agora + timedelta(hours=2),
            120,
        ),
        "saude_oficina_biosseguranca": (
            eventos["congresso_saude_bio"],
            "Oficina: Biossegurança e Boas Práticas em Laboratório Molecular",
            "Protocolos de contenção e manipulação de amostras biológicas.",
            tipoAtividade.OFICINA,
            "Lab. de Biotecnologia - CCS",
            agora + timedelta(days=1, hours=1),
            agora + timedelta(days=1, hours=4),
            25,
        ),
        "saude_palestra_triagem_ia": (
            eventos["congresso_saude_bio"],
            "Palestra: Inteligência Artificial Aplicada à Triagem Hospitalar",
            "Modelos preditivos para redução de tempo de espera em emergências.",
            tipoAtividade.PALESTRA,
            "Auditório Garapuvu",
            agora + timedelta(days=1, hours=5),
            agora + timedelta(days=1, hours=7),
            250,
        ),
        "saude_oficina_dados_python": (
            eventos["congresso_saude_bio"],
            "Oficina: Análise de Dados Epidemiológicos com Python",
            "Tratamento e visualização de séries temporais do DataSUS.",
            tipoAtividade.OFICINA,
            "Laboratório de Informática 03",
            agora + timedelta(days=2, hours=1),
            agora + timedelta(days=2, hours=4),
            35,
        ),
        # Fórum Nacional de Direito Digital
        "dir_palestra_ia_autoral": (
            eventos["forum_direito_digital"],
            "Palestra: Responsabilidade Civil e Direitos Autorais em Modelos de IA",
            "Análise jurídica sobre treinamento de algoritmos e propriedade intelectual.",
            tipoAtividade.PALESTRA,
            "Auditório Gregor Mendel",
            agora - timedelta(days=1, hours=2),
            agora - timedelta(days=1),
            180,
        ),
        "dir_forum_anpd_lgpd": (
            eventos["forum_direito_digital"],
            "Fórum: Fiscalização da ANPD e Incidentes de Vazamento de Dados",
            "Discussão prática sobre planos de resposta a incidentes sob a LGPD.",
            tipoAtividade.FORUM,
            "Sala de Conferências 02",
            agora - timedelta(minutes=20),
            agora + timedelta(hours=2),
            100,
        ),
        "dir_oficina_ripd": (
            eventos["forum_direito_digital"],
            "Oficina: Elaboração de Relatório de Impacto à Proteção de Dados (RIPD)",
            "Workshop prático de mapeamento de fluxos e matriz de risco.",
            tipoAtividade.OFICINA,
            "Sala 204 - Escola de Direito",
            agora + timedelta(days=1, hours=2),
            agora + timedelta(days=1, hours=5),
            40,
        ),
        # Semana de Design, Arquitetura e Urbanismo
        "des_palestra_cidades_esponja": (
            eventos["semana_design_arquitetura"],
            "Palestra: Cidades Esponja e Drenagem Urbana Sustentável",
            "Soluções arquitetônicas para resiliência climática em centros urbanos.",
            tipoAtividade.PALESTRA,
            "Auditório do Bloco F",
            agora + timedelta(days=7, hours=2),
            agora + timedelta(days=7, hours=4),
            150,
        ),
        "des_oficina_impressao_3d": (
            eventos["semana_design_arquitetura"],
            "Oficina: Prototipagem Rápida com Impressão 3D e Corte a Laser",
            "Fabricação digital de maquetes e modelos físicos de produto.",
            tipoAtividade.OFICINA,
            "FabLab UDESC",
            agora + timedelta(days=8, hours=1),
            agora + timedelta(days=8, hours=5),
            20,
        ),
        "des_oficina_design_systems": (
            eventos["semana_design_arquitetura"],
            "Oficina: Design Systems e Acessibilidade Digital no Figma",
            "Construção de bibliotecas de componentes seguindo diretrizes WCAG.",
            tipoAtividade.OFICINA,
            "Laboratório de Design Digital",
            agora + timedelta(days=9, hours=2),
            agora + timedelta(days=9, hours=5),
            30,
        ),
        "des_forum_mobilidade": (
            eventos["semana_design_arquitetura"],
            "Fórum: Mobilidade Ativa e Requalificação de Espaços Públicos",
            "Mesa-redonda com urbanistas e coletivos locais sobre ciclovias e calçadas.",
            tipoAtividade.FORUM,
            "Espaço de Convivência",
            agora + timedelta(days=9, hours=6),
            agora + timedelta(days=9, hours=8),
            85,
        ),
        "des_palestra_biofilico": (
            eventos["semana_design_arquitetura"],
            "Palestra: Design Biofílico e Conforto Ambiental em Interiores",
            "Integração de iluminação natural, acústica e vegetação em projetos.",
            tipoAtividade.PALESTRA,
            "Auditório do Bloco F",
            agora + timedelta(days=10, hours=2),
            agora + timedelta(days=10, hours=4),
            150,
        ),
        "des_oficina_fotografia": (
            eventos["semana_design_arquitetura"],
            "Oficina: Fotografia de Arquitetura e Composição Visual",
            "Saída fotográfica pelo campus com foco em perspectiva e luz natural.",
            tipoAtividade.OFICINA,
            "Hall Principal",
            agora + timedelta(days=11, hours=1),
            agora + timedelta(days=11, hours=4),
            25,
        ),
        # Feira de Inovação no Agronegócio
        "agro_oficina_drones_ndvi": (
            eventos["feira_agronegocio"],
            "Oficina: Mapeamento Aéreo com Drones e Índice NDVI",
            "Processamento de imagens multiespectrais para monitoramento de lavouras.",
            tipoAtividade.OFICINA,
            "Pista de Demonstração Externa",
            agora + timedelta(days=16, hours=2),
            agora + timedelta(days=16, hours=5),
            40,
        ),
        "agro_forum_iot_rural": (
            eventos["feira_agronegocio"],
            "Fórum: Conectividade Rural (IoT/LoRaWAN) e Automação na Suinocultura",
            "Painel sobre telemetria de climatização e rastreabilidade no oeste catarinense.",
            tipoAtividade.FORUM,
            "Pavilhão 02 - Arena Agro",
            agora + timedelta(days=18, hours=3),
            agora + timedelta(days=18, hours=5),
            140,
        ),
        # Semana de Engenharia Mecânica e Automação
        "eng_oficina_clps": (
            eventos["semana_engenharia_mecanica"],
            "Oficina: Programação de CLPs e Redes Industriais Profinet",
            "Configuração de controladores lógicos programáveis em bancada didática.",
            tipoAtividade.OFICINA,
            "Lab. de Automação Industrial",
            agora + timedelta(days=25, hours=2),
            agora + timedelta(days=25, hours=6),
            24,
        ),
        "eng_palestra_manutencao_ia": (
            eventos["semana_engenharia_mecanica"],
            "Palestra: Manutenção Preditiva com Análise de Vibração e IA",
            "Monitoramento de motores elétricos e redutores na indústria 4.0.",
            tipoAtividade.PALESTRA,
            "Auditório IFSC Jaraguá",
            agora + timedelta(days=26, hours=3),
            agora + timedelta(days=26, hours=5),
            160,
        ),
        "eng_oficina_simulacao_fea": (
            eventos["semana_engenharia_mecanica"],
            "Oficina: Simulação Estrutural por Elementos Finitos (FEA)",
            "Análise de tensões e deformações em componentes mecânicos.",
            tipoAtividade.OFICINA,
            "Laboratório de CAD/CAE",
            agora + timedelta(days=27, hours=2),
            agora + timedelta(days=27, hours=5),
            30,
        ),
        "eng_forum_descarbonizacao": (
            eventos["semana_engenharia_mecanica"],
            "Fórum: Eficiência Energética e Descarbonização na Indústria Metalmecânica",
            "Debate com engenheiros industriais da região sobre matriz energética limpa.",
            tipoAtividade.FORUM,
            "Auditório IFSC Jaraguá",
            agora + timedelta(days=28, hours=4),
            agora + timedelta(days=28, hours=6),
            120,
        ),
        # Fórum de Gastronomia e Turismo
        "gastro_oficina_fermentacao": (
            eventos["forum_gastronomia_turismo"],
            "Oficina: Fermentação Natural e Panificação Artesanal com Grãos Locais",
            "Cozinha show prática com técnicas de levain e farinhas regionais.",
            tipoAtividade.OFICINA,
            "Setor 1 - Cozinha Experimental",
            agora + timedelta(days=39, hours=2),
            agora + timedelta(days=39, hours=5),
            35,
        ),
        # Apresentação dos Projetos de PI 2
        "pi2_apresentacao_dia1": (
            eventos["apresentacao_pi2"],
            "Primeiro dia de Apresentação dos Projetos do Projeto Integrador I e II",
            "Apresentação dos Projetos Integradores I e II.",
            tipoAtividade.OUTRO,
            "Auditório - Bloco A",
            hoje + timedelta(hours=14),
            hoje + timedelta(hours=17),
            60,
        ),
        "pi2_apresentacao_dia2": (
            eventos["apresentacao_pi2"],
            "Segundo dia de Apresentação dos Projetos do Projeto Integrador I e II",
            "Apresentação dos Projetos Integradores I e II.",
            tipoAtividade.OUTRO,
            "Auditório - Bloco A",
            hoje + timedelta(days=1, hours=14),
            hoje + timedelta(days=1, hours=17),
            60,
        ),
    }

    atividades = {}
    for chave, (evento, nome, descricao, tipo_atividade, local, hora_inicio, hora_fim, limite_pessoas) in dados_atividades.items():
        atividades[chave], _ = Atividade.objects.get_or_create(
            nome=nome,
            evento=evento,
            defaults={
                "descricao": descricao,
                "tipoAtividade": tipo_atividade,
                "complementoLocal": local,
                "horaInicio": hora_inicio,
                "horaFim": hora_fim,
                "limitePessoas": limite_pessoas,
            },
        )

    # 5. Inscrições e Participações:
    # (chave_usuario, chave_evento, chaves_atividades_inscritas, chaves_atividades_presentes)
    inscricoes_config = [
        # Administradores
        ("admin_ana", "semana_tecnologia", ["tec_keynote_diagnostico", "tec_oficina_docker_k8s"], ["tec_keynote_diagnostico"]),
        ("admin_ana", "forum_direito_digital", ["dir_palestra_ia_autoral"], []),
        ("admin_fernando", "palestra_administracao", ["adm_palestra_internacional", "adm_oficina_okrs"], ["adm_palestra_internacional"]),
        ("admin_fernando", "forum_gestao_projetos", ["proj_forum_gestao", "proj_palestra_riscos"], []),
        # Semana Acadêmica de Tecnologia
        ("mariana_lima", "semana_tecnologia", ["tec_keynote_diagnostico", "tec_oficina_docker_k8s", "tec_forum_carreira_ti"], ["tec_keynote_diagnostico", "tec_oficina_docker_k8s"]),
        ("joao_silveira", "semana_tecnologia", ["tec_keynote_diagnostico", "tec_oficina_sensores", "tec_oficina_docker_k8s"], ["tec_oficina_sensores"]),
        ("lucas_mendes", "semana_tecnologia", ["tec_keynote_diagnostico", "tec_oficina_docker_k8s", "tec_forum_carreira_ti"], ["tec_oficina_docker_k8s"]),
        ("joana_muller", "semana_tecnologia", ["tec_keynote_diagnostico", "tec_oficina_sensores", "tec_oficina_docker_k8s", "tec_forum_carreira_ti"], ["tec_keynote_diagnostico", "tec_oficina_sensores"]),
        ("sofia_almeida", "semana_tecnologia", ["tec_keynote_diagnostico", "tec_oficina_sensores", "tec_oficina_docker_k8s"], ["tec_oficina_sensores"]),
        ("pedro_henrique", "semana_tecnologia", ["tec_keynote_diagnostico", "tec_oficina_sensores"], ["tec_oficina_sensores"]),
        ("rodrigo_melo", "semana_tecnologia", ["tec_keynote_diagnostico", "tec_forum_carreira_ti"], []),
        ("thiago_martins", "semana_tecnologia", ["tec_keynote_diagnostico", "tec_oficina_docker_k8s"], []),
        # Palestra Internacional de Administração
        ("joao_silveira", "palestra_administracao", ["adm_palestra_internacional"], []),
        ("sofia_almeida", "palestra_administracao", ["adm_palestra_internacional", "adm_oficina_okrs"], []),
        ("clara_nogueira", "palestra_administracao", ["adm_palestra_internacional", "adm_oficina_okrs"], ["adm_palestra_internacional", "adm_oficina_okrs"]),
        ("fernanda_lima", "palestra_administracao", ["adm_palestra_internacional", "adm_oficina_okrs"], ["adm_palestra_internacional"]),
        ("helena_ribeiro", "palestra_administracao", ["adm_palestra_internacional", "adm_oficina_okrs"], []),
        ("gabriel_santos", "palestra_administracao", ["adm_palestra_internacional"], []),
        # Fórum de Gestão de Projetos
        ("joao_silveira", "forum_gestao_projetos", ["proj_forum_gestao", "proj_oficina_kanban"], ["proj_forum_gestao"]),
        ("lucas_mendes", "forum_gestao_projetos", ["proj_forum_gestao", "proj_oficina_kanban"], ["proj_oficina_kanban"]),
        ("joana_muller", "forum_gestao_projetos", ["proj_oficina_kanban", "proj_palestra_riscos"], []),
        ("clara_nogueira", "forum_gestao_projetos", ["proj_forum_gestao", "proj_oficina_kanban", "proj_palestra_riscos"], ["proj_forum_gestao", "proj_oficina_kanban"]),
        ("patricia_gomes", "forum_gestao_projetos", ["proj_oficina_kanban", "proj_palestra_riscos"], []),
        ("helena_ribeiro", "forum_gestao_projetos", ["proj_forum_gestao"], []),
        # Congresso de Saúde e Biotecnologia
        ("rafael_costa", "congresso_saude_bio", ["saude_palestra_crispr", "saude_forum_telemedicina", "saude_oficina_biosseguranca", "saude_palestra_triagem_ia", "saude_oficina_dados_python"], ["saude_palestra_crispr", "saude_forum_telemedicina", "saude_oficina_biosseguranca", "saude_oficina_dados_python"]),
        ("mariana_lima", "congresso_saude_bio", ["saude_palestra_crispr", "saude_forum_telemedicina", "saude_palestra_triagem_ia"], ["saude_palestra_crispr"]),
        ("joao_silveira", "congresso_saude_bio", ["saude_palestra_crispr", "saude_forum_telemedicina", "saude_oficina_dados_python"], ["saude_oficina_dados_python"]),
        ("amanda_castro", "congresso_saude_bio", ["saude_palestra_crispr", "saude_forum_telemedicina"], []),
        ("vinicius_teixeira", "congresso_saude_bio", ["saude_forum_telemedicina", "saude_oficina_dados_python"], []),
        # Simpósio de Energias Renováveis (sem atividades)
        ("bruno_oliveira", "simposio_energias", [], []),
        ("juliana_barros", "simposio_energias", [], []),
        ("larissa_monteiro", "simposio_energias", [], []),
        # Fórum Nacional de Direito Digital
        ("thiago_martins", "forum_direito_digital", ["dir_palestra_ia_autoral", "dir_forum_anpd_lgpd", "dir_oficina_ripd"], ["dir_palestra_ia_autoral", "dir_forum_anpd_lgpd", "dir_oficina_ripd"]),
        ("rodrigo_melo", "forum_direito_digital", ["dir_palestra_ia_autoral", "dir_forum_anpd_lgpd"], ["dir_palestra_ia_autoral"]),
        ("vinicius_teixeira", "forum_direito_digital", ["dir_palestra_ia_autoral", "dir_forum_anpd_lgpd"], []),
        ("clara_nogueira", "forum_direito_digital", ["dir_forum_anpd_lgpd", "dir_oficina_ripd"], ["dir_oficina_ripd"]),
        ("juliana_barros", "forum_direito_digital", ["dir_palestra_ia_autoral", "dir_forum_anpd_lgpd"], []),
        # Eventos Futuros
        ("sofia_almeida", "semana_design_arquitetura", ["des_oficina_impressao_3d", "des_oficina_design_systems", "des_palestra_biofilico", "des_oficina_fotografia"], []),
        ("juliana_barros", "semana_design_arquitetura", ["des_palestra_cidades_esponja", "des_forum_mobilidade"], []),
        ("mateus_cardoso", "semana_design_arquitetura", ["des_palestra_cidades_esponja", "des_forum_mobilidade", "des_oficina_fotografia"], []),
        ("patricia_gomes", "semana_design_arquitetura", ["des_oficina_design_systems"], []),
        ("joana_muller", "semana_design_arquitetura", ["des_oficina_design_systems"], []),
        ("bruno_oliveira", "feira_agronegocio", ["agro_oficina_drones_ndvi", "agro_forum_iot_rural"], []),
        ("pedro_henrique", "feira_agronegocio", ["agro_oficina_drones_ndvi", "agro_forum_iot_rural"], []),
        ("larissa_monteiro", "feira_agronegocio", ["agro_forum_iot_rural"], []),
        ("pedro_henrique", "semana_engenharia_mecanica", ["eng_oficina_clps", "eng_palestra_manutencao_ia", "eng_oficina_simulacao_fea", "eng_forum_descarbonizacao"], []),
        ("mariana_lima", "semana_engenharia_mecanica", ["eng_palestra_manutencao_ia"], []),
        ("bruno_oliveira", "semana_engenharia_mecanica", ["eng_forum_descarbonizacao"], []),
        ("mateus_cardoso", "forum_gastronomia_turismo", ["gastro_oficina_fermentacao"], []),
        ("larissa_monteiro", "forum_gastronomia_turismo", ["gastro_oficina_fermentacao"], []),
        ("gabriel_santos", "forum_gastronomia_turismo", ["gastro_oficina_fermentacao"], []),
        ("fernanda_lima", "forum_gastronomia_turismo", [], []),
    ]

    for chave_usuario, chave_evento, chaves_atividades, chaves_presencas in inscricoes_config:
        inscrever_e_participar(
            usuarios[chave_usuario],
            eventos[chave_evento],
            atividades_inscritas=[atividades[k] for k in chaves_atividades],
            atividades_presentes=[atividades[k] for k in chaves_presencas],
        )

    # 6. Quizzes
    dados_quizzes = {
        "quiz_redes_neurais_diagnostico": (
            "tec_keynote_diagnostico",
            {
                "titulo": "Arquitetura de Redes Neurais em Diagnóstico",
                "tipo": "MULTIPLA",
                "subtitulo": "Fundamentos de Visão Computacional Médica",
                "pergunta": "Qual arquitetura de Deep Learning é mais utilizada para segmentação de imagens médicas (como ressonâncias e tomografias)?",
                "dica": "Possui formato simétrico em 'U' com conexões de salto (skip connections).",
                "opcao_a": "U-Net",
                "opcao_b": "ARIMA",
                "opcao_c": "K-Means",
                "opcao_d": "Random Forest",
                "alternativa_correta": "A",
            },
        ),
        "quiz_metrica_triagem_clinica": (
            "tec_keynote_diagnostico",
            {
                "titulo": "Métrica de Avaliação em Exames Clínicos",
                "tipo": "MULTIPLA",
                "subtitulo": "Sensibilidade vs. Especificidade",
                "pergunta": "Em um sistema de triagem médica, qual métrica deve ser priorizada para evitar falsos negativos em doenças graves?",
                "dica": "Pense na capacidade do modelo de detectar todos os pacientes realmente doentes.",
                "opcao_a": "Acurácia global",
                "opcao_b": "Recall (Sensibilidade)",
                "opcao_c": "Tempo de inferência",
                "opcao_d": "Compressão de modelo",
                "alternativa_correta": "B",
            },
        ),
        "quiz_espessura_material": (
            "tec_oficina_sensores",
            {
                "titulo": "Aferição de Espessura do Material",
                "tipo": "METRICA",
                "subtitulo": "Medição de precisão industrial",
                "pergunta": "Qual a espessura medida da amostra metálica disponibilizada na bancada 02?",
                "dica": "Utilize o paquímetro digital disponível no kit do laboratório.",
                "unidade_medida": "mm",
                "valor_minimo": Decimal("10.00"),
                "valor_maximo": Decimal("10.50"),
                "valor_ideal": Decimal("10.25"),
            },
        ),
        "quiz_pesagem_reagente": (
            "tec_oficina_sensores",
            {
                "titulo": "Pesagem de Componente Químico",
                "tipo": "METRICA",
                "subtitulo": "Teste de tolerância de dosagem",
                "pergunta": "Informe a massa total do reagente A após o processo de secagem.",
                "dica": "Considere a tara do recipiente de 5 gramas.",
                "unidade_medida": "gramas",
                "valor_minimo": Decimal("48.00"),
                "valor_maximo": Decimal("52.00"),
                "valor_ideal": Decimal("50.00"),
            },
        ),
        "quiz_tensao_sensor": (
            "tec_oficina_sensores",
            {
                "titulo": "Tensão de Saída do Sensor Calibrado",
                "tipo": "METRICA",
                "subtitulo": "Leitura no multímetro de bancada",
                "pergunta": "Meça a tensão de saída (em Volts) do sensor óptico sob iluminação padrão de 500 lux.",
                "dica": "Aguarde 10 segundos para estabilização térmica do circuito.",
                "unidade_medida": "V",
                "valor_minimo": Decimal("3.20"),
                "valor_maximo": Decimal("3.40"),
                "valor_ideal": Decimal("3.30"),
            },
        ),
        "quiz_pods_kubernetes": (
            "tec_oficina_docker_k8s",
            {
                "titulo": "Orquestração de Pods no Kubernetes",
                "tipo": "MULTIPLA",
                "subtitulo": "Conceitos fundamentais de cluster",
                "pergunta": "Qual objeto do Kubernetes garante que um número específico de réplicas de um Pod esteja sempre em execução?",
                "dica": "É gerenciado indiretamente pelo Deployment.",
                "opcao_a": "ConfigMap",
                "opcao_b": "Ingress",
                "opcao_c": "ReplicaSet",
                "opcao_d": "Secret",
                "alternativa_correta": "C",
            },
        ),
        "quiz_memoria_container": (
            "tec_oficina_docker_k8s",
            {
                "titulo": "Consumo de Memória do Container",
                "tipo": "METRICA",
                "subtitulo": "Monitoramento com docker stats",
                "pergunta": "Qual o pico de consumo de memória RAM (em MB) da API após o teste de carga de 1.000 requisições?",
                "dica": "Observe a coluna MEM USAGE no terminal.",
                "unidade_medida": "MB",
                "valor_minimo": Decimal("140.00"),
                "valor_maximo": Decimal("165.00"),
                "valor_ideal": Decimal("152.00"),
            },
        ),
        "quiz_governanca_corporativa": (
            "adm_palestra_internacional",
            {
                "titulo": "Indicadores de Governança Corporativa",
                "tipo": "MULTIPLA",
                "subtitulo": "Gestão contemporânea",
                "pergunta": "Qual pilar de ESG trata diretamente da transparência fiscal, ética empresarial e composição do conselho?",
                "dica": "Refere-se à letra 'G' da sigla.",
                "opcao_a": "Ambiental",
                "opcao_b": "Social",
                "opcao_c": "Governança",
                "opcao_d": "Operacional",
                "alternativa_correta": "C",
            },
        ),
        "quiz_estruturacao_krs": (
            "adm_oficina_okrs",
            {
                "titulo": "Estruturação de Key Results",
                "tipo": "MULTIPLA",
                "subtitulo": "Metodologia OKR",
                "pergunta": "Qual característica é obrigatória em um bom Resultado-Chave (Key Result)?",
                "dica": "Se não pode ser medido, não é um KR.",
                "opcao_a": "Ser subjetivo e inspiracional",
                "opcao_b": "Ser quantificável e mensurável",
                "opcao_c": "Ser definido exclusivamente pelo RH",
                "opcao_d": "Não possuir prazo definido",
                "alternativa_correta": "B",
            },
        ),
        "quiz_atingimento_meta_okr": (
            "adm_oficina_okrs",
            {
                "titulo": "Cálculo de Atingimento de Meta",
                "tipo": "METRICA",
                "subtitulo": "Estudo de caso Startup Alpha",
                "pergunta": "Com base na planilha do exercício, qual o percentual médio de atingimento dos 3 KRs do trimestre?",
                "dica": "Some os percentuais individuais e divida por 3.",
                "unidade_medida": "%",
                "valor_minimo": Decimal("74.00"),
                "valor_maximo": Decimal("76.00"),
                "valor_ideal": Decimal("75.00"),
            },
        ),
        "quiz_lei_little_lead_time": (
            "proj_oficina_kanban",
            {
                "titulo": "Lei de Little na Prática",
                "tipo": "METRICA",
                "subtitulo": "Cálculo de Lead Time",
                "pergunta": "Se o WIP médio da equipe é de 12 itens e o Throughput é de 3 itens/dia, qual o Lead Time médio em dias?",
                "dica": "Fórmula: Lead Time = WIP / Throughput.",
                "unidade_medida": "dias",
                "valor_minimo": Decimal("3.80"),
                "valor_maximo": Decimal("4.20"),
                "valor_ideal": Decimal("4.00"),
            },
        ),
        "quiz_limite_wip_kanban": (
            "proj_oficina_kanban",
            {
                "titulo": "Limite de Trabalho em Progresso (WIP)",
                "tipo": "MULTIPLA",
                "subtitulo": "Fluxo puxado",
                "pergunta": "Qual é o principal objetivo de limitar o WIP em um quadro Kanban?",
                "dica": "Foca em terminar tarefas antes de começar novas.",
                "opcao_a": "Aumentar a quantidade de reuniões diárias",
                "opcao_b": "Evitar gargalos e reduzir o tempo de ciclo (Cycle Time)",
                "opcao_c": "Eliminar a necessidade de testes",
                "opcao_d": "Distribuir tarefas igualmente por hora",
                "alternativa_correta": "B",
            },
        ),
        "quiz_mecanismo_crispr": (
            "saude_palestra_crispr",
            {
                "titulo": "Mecanismo CRISPR-Cas9",
                "tipo": "MULTIPLA",
                "subtitulo": "Biologia Molecular",
                "pergunta": "Qual é a função da enzima Cas9 no sistema CRISPR-Cas9?",
                "dica": "Atua como uma 'tesoura molecular'.",
                "opcao_a": "Transportar aminoácidos no ribossomo",
                "opcao_b": "Realizar a clivagem (corte) da dupla fita de DNA no alvo guiado",
                "opcao_c": "Sintetizar lipídios de membrana",
                "opcao_d": "Degradar proteínas mal dobradas",
                "alternativa_correta": "B",
            },
        ),
        "quiz_temperatura_ultrafreezer": (
            "saude_oficina_biosseguranca",
            {
                "titulo": "Temperatura de Armazenamento de Reagentes",
                "tipo": "METRICA",
                "subtitulo": "Controle de cadeia fria",
                "pergunta": "Qual a temperatura interna aferida no ultrafreezer da Bancada 01 durante a inspeção?",
                "dica": "Valores padrão de ultrafreezeres ficam próximos a -80 °C.",
                "unidade_medida": "°C",
                "valor_minimo": Decimal("-82.00"),
                "valor_maximo": Decimal("-78.00"),
                "valor_ideal": Decimal("-80.00"),
            },
        ),
        "quiz_nivel_biosseguranca": (
            "saude_oficina_biosseguranca",
            {
                "titulo": "Nível de Biossegurança (NB)",
                "tipo": "MULTIPLA",
                "subtitulo": "Classificação de risco biológico",
                "pergunta": "Qual nível de biossegurança é exigido para manipulação de agentes com risco individual moderado e risco comunitário limitado?",
                "dica": "É o nível padrão da maioria dos laboratórios clínicos hospitalares.",
                "opcao_a": "NB-1",
                "opcao_b": "NB-2",
                "opcao_c": "NB-3",
                "opcao_d": "NB-4",
                "alternativa_correta": "B",
            },
        ),
        "quiz_tempo_autoclave": (
            "saude_oficina_biosseguranca",
            {
                "titulo": "Tempo de Esterilização em Autoclave",
                "tipo": "METRICA",
                "subtitulo": "Protocolo padrão a 121 °C",
                "pergunta": "Informe o tempo mínimo (em minutos) de exposição a 121 °C para esterilização padrão de vidrarias.",
                "dica": "Valor clássico de referência em microbiologia.",
                "unidade_medida": "minutos",
                "valor_minimo": Decimal("15.00"),
                "valor_maximo": Decimal("20.00"),
                "valor_ideal": Decimal("15.00"),
            },
        ),
        "quiz_taxa_incidencia_sul": (
            "saude_oficina_dados_python",
            {
                "titulo": "Taxa de Incidência Calculada",
                "tipo": "METRICA",
                "subtitulo": "Análise do dataset CSV fornecido",
                "pergunta": "Qual foi a taxa de incidência por 100 mil habitantes encontrada para a região Sul em 2025?",
                "dica": "Filtre pela coluna UF in ['PR', 'SC', 'RS'] no notebook.",
                "unidade_medida": "casos/100k",
                "valor_minimo": Decimal("124.00"),
                "valor_maximo": Decimal("126.00"),
                "valor_ideal": Decimal("125.40"),
            },
        ),
        "quiz_bases_legais_lgpd": (
            "dir_oficina_ripd",
            {
                "titulo": "Bases Legais da LGPD",
                "tipo": "MULTIPLA",
                "subtitulo": "Artigo 7º da Lei 13.709/2018",
                "pergunta": "Qual base legal exige a elaboração de um Relatório de Impacto à Proteção de Dados (RIPD) quando solicitada pela ANPD?",
                "dica": "Base legal frequentemente usada em marketing e prevenção a fraudes, que exige teste de balanceamento.",
                "opcao_a": "Cumprimento de obrigação legal",
                "opcao_b": "Legítimo interesse do controlador",
                "opcao_c": "Execução de contrato",
                "opcao_d": "Tutela da saúde",
                "alternativa_correta": "B",
            },
        ),
        "quiz_prazo_comunicacao_anpd": (
            "dir_oficina_ripd",
            {
                "titulo": "Prazo de Comunicação de Incidente",
                "tipo": "METRICA",
                "subtitulo": "Resolução CD/ANPD nº 15/2024",
                "pergunta": "Qual o prazo máximo (em dias úteis) para o controlador comunicar à ANPD um incidente de segurança relevante?",
                "dica": "Atualizado pela resolução recente da ANPD.",
                "unidade_medida": "dias úteis",
                "valor_minimo": Decimal("3.00"),
                "valor_maximo": Decimal("3.00"),
                "valor_ideal": Decimal("3.00"),
            },
        ),
        "quiz_temperatura_extrusao_pla": (
            "des_oficina_impressao_3d",
            {
                "titulo": "Temperatura de Extrusão PLA",
                "tipo": "METRICA",
                "subtitulo": "Preparação de impressora 3D",
                "pergunta": "Qual a temperatura ideal do bico extrusor (em °C) para impressão em filamento PLA padrão?",
                "dica": "Consulte a etiqueta do carretel na bancada do FabLab.",
                "unidade_medida": "°C",
                "valor_minimo": Decimal("195.00"),
                "valor_maximo": Decimal("215.00"),
                "valor_ideal": Decimal("205.00"),
            },
        ),
        "quiz_contraste_wcag": (
            "des_oficina_design_systems",
            {
                "titulo": "Contraste Mínimo WCAG AA",
                "tipo": "METRICA",
                "subtitulo": "Acessibilidade visual",
                "pergunta": "Qual a razão de contraste mínima exigida pelo padrão WCAG 2.1 nível AA para textos normais?",
                "dica": "Informe apenas o primeiro número da proporção X:1.",
                "unidade_medida": ":1",
                "valor_minimo": Decimal("4.50"),
                "valor_maximo": Decimal("4.50"),
                "valor_ideal": Decimal("4.50"),
            },
        ),
        "quiz_indice_ndvi_soja": (
            "agro_oficina_drones_ndvi",
            {
                "titulo": "Interpretação do Índice NDVI",
                "tipo": "METRICA",
                "subtitulo": "Vigor vegetativo",
                "pergunta": "Em uma lavoura de soja saudável em pleno desenvolvimento vegetativo, qual o valor esperado de NDVI?",
                "dica": "Varia entre -1 e +1; vegetação densa fica próxima ao limite superior.",
                "unidade_medida": "NDVI",
                "valor_minimo": Decimal("0.70"),
                "valor_maximo": Decimal("0.90"),
                "valor_ideal": Decimal("0.82"),
            },
        ),
        "quiz_linguagem_ladder_na": (
            "eng_oficina_clps",
            {
                "titulo": "Linguagem Ladder - Contato Normalmente Aberto",
                "tipo": "MULTIPLA",
                "subtitulo": "Norma IEC 61131-3",
                "pergunta": "Na programação em Ladder, qual símbolo representa um contato normalmente aberto (NA)?",
                "dica": "Não possui barra diagonal cortando o símbolo.",
                "opcao_a": "--| |--",
                "opcao_b": "--|/|--",
                "opcao_c": "--( )--",
                "opcao_d": "--(R)--",
                "alternativa_correta": "A",
            },
        ),
    }

    quizzes = {
        chave: criar_quiz(atividades[chave_atividade], dados_quiz)
        for chave, (chave_atividade, dados_quiz) in dados_quizzes.items()
    }

    # 7. Respostas:
    # (chave_usuario, chave_atividade, chave_quiz, valor_resposta, resposta_texto)
    respostas_config = [
        # Semana Acadêmica de Tecnologia - Oficina de Sensores
        ("joana_muller", "tec_oficina_sensores", "quiz_espessura_material", "10.20", None),
        ("joana_muller", "tec_oficina_sensores", "quiz_pesagem_reagente", "42.50", None),
        ("joana_muller", "tec_oficina_sensores", "quiz_tensao_sensor", "3.30", None),
        ("joao_silveira", "tec_oficina_sensores", "quiz_espessura_material", "10.25", None),
        ("joao_silveira", "tec_oficina_sensores", "quiz_pesagem_reagente", "49.80", None),
        ("joao_silveira", "tec_oficina_sensores", "quiz_tensao_sensor", "3.28", None),
        ("sofia_almeida", "tec_oficina_sensores", "quiz_espessura_material", "11.10", None),
        ("sofia_almeida", "tec_oficina_sensores", "quiz_pesagem_reagente", "50.00", None),
        # Semana Acadêmica de Tecnologia - Keynote
        ("mariana_lima", "tec_keynote_diagnostico", "quiz_redes_neurais_diagnostico", None, "A"),
        ("mariana_lima", "tec_keynote_diagnostico", "quiz_metrica_triagem_clinica", None, "B"),
        ("joana_muller", "tec_keynote_diagnostico", "quiz_redes_neurais_diagnostico", None, "A"),
        ("joana_muller", "tec_keynote_diagnostico", "quiz_metrica_triagem_clinica", None, "A"),
        ("admin_ana", "tec_keynote_diagnostico", "quiz_redes_neurais_diagnostico", None, "A"),
        # Semana Acadêmica de Tecnologia - Oficina Docker/K8s
        ("mariana_lima", "tec_oficina_docker_k8s", "quiz_pods_kubernetes", None, "C"),
        ("mariana_lima", "tec_oficina_docker_k8s", "quiz_memoria_container", "150.00", None),
        ("lucas_mendes", "tec_oficina_docker_k8s", "quiz_pods_kubernetes", None, "C"),
        ("lucas_mendes", "tec_oficina_docker_k8s", "quiz_memoria_container", "180.00", None),
        # Palestra Internacional de Administração
        ("clara_nogueira", "adm_palestra_internacional", "quiz_governanca_corporativa", None, "C"),
        ("fernanda_lima", "adm_palestra_internacional", "quiz_governanca_corporativa", None, "C"),
        ("admin_fernando", "adm_palestra_internacional", "quiz_governanca_corporativa", None, "A"),
        ("clara_nogueira", "adm_oficina_okrs", "quiz_estruturacao_krs", None, "B"),
        ("clara_nogueira", "adm_oficina_okrs", "quiz_atingimento_meta_okr", "75.00", None),
        # Fórum de Gestão de Projetos
        ("clara_nogueira", "proj_oficina_kanban", "quiz_lei_little_lead_time", "4.00", None),
        ("clara_nogueira", "proj_oficina_kanban", "quiz_limite_wip_kanban", None, "B"),
        ("lucas_mendes", "proj_oficina_kanban", "quiz_lei_little_lead_time", "3.90", None),
        ("lucas_mendes", "proj_oficina_kanban", "quiz_limite_wip_kanban", None, "B"),
        # Congresso de Saúde e Biotecnologia
        ("rafael_costa", "saude_palestra_crispr", "quiz_mecanismo_crispr", None, "B"),
        ("mariana_lima", "saude_palestra_crispr", "quiz_mecanismo_crispr", None, "B"),
        ("rafael_costa", "saude_oficina_biosseguranca", "quiz_temperatura_ultrafreezer", "-80.00", None),
        ("rafael_costa", "saude_oficina_biosseguranca", "quiz_nivel_biosseguranca", None, "B"),
        ("rafael_costa", "saude_oficina_biosseguranca", "quiz_tempo_autoclave", "15.00", None),
        ("rafael_costa", "saude_oficina_dados_python", "quiz_taxa_incidencia_sul", "125.40", None),
        ("joao_silveira", "saude_oficina_dados_python", "quiz_taxa_incidencia_sul", "124.80", None),
        # Fórum Nacional de Direito Digital
        ("thiago_martins", "dir_oficina_ripd", "quiz_bases_legais_lgpd", None, "B"),
        ("thiago_martins", "dir_oficina_ripd", "quiz_prazo_comunicacao_anpd", "3.00", None),
        ("clara_nogueira", "dir_oficina_ripd", "quiz_bases_legais_lgpd", None, "B"),
        ("clara_nogueira", "dir_oficina_ripd", "quiz_prazo_comunicacao_anpd", "5.00", None),
    ]

    for chave_usuario, chave_atividade, chave_quiz, valor_resposta, texto_resposta in respostas_config:
        registrar_resposta(
            usuarios[chave_usuario],
            atividades[chave_atividade],
            quizzes[chave_quiz],
            valor_resposta=valor_resposta,
            resposta_texto=texto_resposta,
        )

    print("População do banco de dados concluída com sucesso!")


if __name__ == "__main__":
    popular_banco()