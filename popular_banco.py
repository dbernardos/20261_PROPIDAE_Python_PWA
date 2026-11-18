import os
import django
from datetime import date, timedelta
from decimal import Decimal
from django.core.files import File
from django.conf import settings
import shutil

# Configura o ambiente Django com a settings do seu projeto
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SEA.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth import get_user_model

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

def atribuir_imagem_do_disco(instancia, nome_campo, caminho_origem, pasta_destino):
    if not os.path.exists(caminho_origem):
        print(f"Aviso: Imagem de origem não encontrada em '{caminho_origem}'")
        return

    nome_arquivo = os.path.basename(caminho_origem)
    pasta_destino_completa = os.path.join(settings.MEDIA_ROOT, pasta_destino)
    caminho_destino_completo = os.path.join(pasta_destino_completa, nome_arquivo)
    caminho_relativo_banco = f"{pasta_destino}/{nome_arquivo}"

    os.makedirs(pasta_destino_completa, exist_ok=True)

    if not os.path.exists(caminho_destino_completo):
        shutil.copy2(caminho_origem, caminho_destino_completo)
        print(f"Novo arquivo copiado para {pasta_destino}/: {nome_arquivo}")
    else:
        print(f"Arquivo já existe em {pasta_destino}/: {nome_arquivo} (cópia ignorada)")

    setattr(instancia, nome_campo, caminho_relativo_banco)
    instancia.save(update_fields=[nome_campo])
        

User = get_user_model()

def popular_banco():
    print("Iniciando povoamento completo do banco de dados...")

    # -------------------------------------------------------------
    # 1. USUÁRIOS E PERFIS (User + Usuario)
    # -------------------------------------------------------------
    
    # ADMINISTRADOR 1
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
        user_admin.set_password("ifsc1234")
        user_admin.save()

    usuario_admin, _ = Usuario.objects.get_or_create(
        user_django=user_admin,
        defaults={
            "nome": "Carlos Eduardo",
            "email": "admin@sea.com",
            "cpf": "921.370.449-60",
            "telefone": "(11) 99999-0001",
            "dataNascimento": date(1988, 5, 12),
            "cargo": "Administrador de Sistemas",
            "formacao": "Engenharia de Software",
            "empresa": "SEA Corp",
            "biografia": "Gestor principal do sistema de eventos."
        }
    )
    
    atribuir_imagem_do_disco(usuario_admin, 'fotoPerfil', 'media/popular_iniciais/perfis/admin.png', 'perfis')

    # ADMINISTRADOR 2
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
        user_admin2.set_password("ifsc1234")
        user_admin2.save()

    usuario_admin2, _ = Usuario.objects.get_or_create(
        user_django=user_admin2,
        defaults={
            "nome": "Ana Silva",
            "email": "admin2@sea.com",
            "cpf": "417.453.189-76",
            "telefone": "(11) 98888-1111",
            "dataNascimento": date(1999, 10, 11),
            "cargo": "Projetista de Sistemas",
            "formacao": "Engenharia de Computação",
            "empresa": "SEA Corp",
            "biografia": "Gestor do sistema de eventos."
        }
    )
    atribuir_imagem_do_disco(usuario_admin2, 'fotoPerfil', 'media/popular_iniciais/perfis/admin2.png', 'perfis')
    
    # ADMINISTRADOR 3
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
        user_admin3.set_password("ifsc1234")
        user_admin3.save()

    usuario_admin3, _ = Usuario.objects.get_or_create(
        user_django=user_admin3,
        defaults={
            "nome": "Fernando dos Santos",
            "email": "admin3@sea.com",
            "cpf": "532.729.919-80",
            "telefone": "(11) 97777-0004",
            "dataNascimento": date(1995, 7, 20),
            "cargo": "Adminstrador de Negócios",
            "formacao": "Administração",
            "empresa": "SEA Corp",
            "biografia": "Gestor do sistema de eventos."
        }
    )
    atribuir_imagem_do_disco(usuario_admin3, 'fotoPerfil', 'media/popular_iniciais/perfis/admin3.png', 'perfis')


    # ADMINISTRADOR 4
    user_admin4, created_admin4 = User.objects.get_or_create(
        username="admin_eventos4",
        defaults={
            "email": "admin4@sea.com",
            "first_name": "Geraldo",
            "last_name": "Gomes",
            "is_staff": True,
            "is_superuser": True
        }
    )
    if created_admin4:
        user_admin4.set_password("ifsc1234")
        user_admin4.save()

    usuario_admin4, _ = Usuario.objects.get_or_create(
        user_django=user_admin4,
        defaults={
            "nome": "Geraldo Gomes",
            "email": "admin4@sea.com",
            "cpf": "155.340.800-43",
            "telefone": "(11) 97777-0004",
            "dataNascimento": date(1995, 7, 20),
            "cargo": "Adminstrador de Negócios",
            "formacao": "Administração",
            "empresa": "IFSC",
            "biografia": "Gestor do sistema de eventos."
        }
    )
    atribuir_imagem_do_disco(usuario_admin4, 'fotoPerfil', 'media/popular_iniciais/perfis/admin4.png', 'perfis')

    #####################
    
    # PARTICIPANTE 1
    user_participante1, created_participante1 = User.objects.get_or_create(
        username="mariana.li",
        defaults={
            "email": "mariana.li@universidade.edu.br",
            "first_name": "Mariana",
            "last_name": "Lima"
        }
    )

    if created_participante1:
        user_participante1.set_password('participante1')
        user_participante1.save()

    usuario_participante1, _ = Usuario.objects.get_or_create(
        user_django=user_participante1,
        defaults={
            "nome": "Mariana Lima",
            "email": "mariana.li@universidade.edu.br",
            "cpf": "705.507.149-60",
            "telefone": "(49) 93226-2845",
            "dataNascimento": date(1992, 8, 24),
            "cargo": "Pesquisadora",
            "formacao": "Doutorado em Ciência da Computação",
            "empresa": "Intelbras",
            "biografia": "Olá! Sou Mariana Lima, Doutora em Ciência da Computação, faço parte da equipe de pesquisa da Intelbras. Sou apaixonada por Inteligência Artificial e Engenharia de Software, dedicando minha carreira a explorar como a tecnologia pode resolver problemas reais e transformar o futuro."
        }
    )
    atribuir_imagem_do_disco(usuario_participante1, 'fotoPerfil', 'media/popular_iniciais/perfis/participante1.png', 'perfis')
    
    
    # PARTICIPANTE 2
    user_participante2, created_participante2 = User.objects.get_or_create(
        username="joao.si",
        defaults={
            "email": "joao.si@universidade.edu.br",
            "first_name": "João",
            "last_name": "Silveira"
        }
    )

    if created_participante2:
            user_participante2.set_password('participante2')
            user_participante2.save()
    
    usuario_participante2, _ = Usuario.objects.get_or_create(
            user_django=user_participante2,
            defaults={
                "nome": "João Silveira",
                "email": "joao.si@universidade.edu.br",
                "cpf": "458.696.188-00",
                "telefone": "(49) 3226-2845",
                "dataNascimento": date(1992, 7, 20),
                "cargo": "Professor",
                "formacao": "Mestre em Ciência da Dados",
                "empresa": "FIAP",
                "biografia": " 👨‍🏫 Professor | FIAP\n🎓 Mestre em Ciência de Dados\n📊  Especialista em Análise de Dados"               
            }
        )
    atribuir_imagem_do_disco(usuario_participante2, 'fotoPerfil', 'media/popular_iniciais/perfis/participante2.png', 'perfis')
    
    
    # PARTICIPANTE 3
    user_participante3, created_participante3 = User.objects.get_or_create(
        username="mendes_lucaaas",
        defaults={
            "email": "lucas.des@estudante.edu.br",
            "first_name": "Lucas",
            "last_name": "Mendes"
        }
    )

    if created_participante3:
        user_participante3.set_password('participante3')
        user_participante3.save()

    usuario_participante3, _ = Usuario.objects.get_or_create(
        user_django=user_participante3,
        defaults={
            "nome": "Lucas Mendes",
            "email": "lucas.des@estudante.edu.br",
            "cpf": "962.065.259-29",
            "telefone": "(45) 3761-2595",
            "dataNascimento": date(2001, 3, 15),
            "cargo": "Desenvolvedor Junior",
            "formacao": "Graduando em Sistemas de Informação",
            "empresa": "Startup Equinox.io",
            "biografia": "Lucas Mendes é graduando em Sistemas de Informação e atua como Desenvolvedor Júnior na Startup Equinox.io.\nApaixonado por qualidade de software, dedica-se a testes de código e automação de processos."
        }
    )
    atribuir_imagem_do_disco(usuario_participante3, 'fotoPerfil', 'media/popular_iniciais/perfis/participante3.png', 'perfis')
    
    
    # PARTICIPANTE 4
    user_participante4, created_participante4 = User.objects.get_or_create(
        username="joana_m",
        defaults={
            "email": "joana.muller@estudante.edu.br",
            "first_name": "Joana",
            "last_name": "Muller"
        }
    )

    if created_participante4:
        user_participante4.set_password('participante4')
        user_participante4.save()

    usuario_participante4, _ = Usuario.objects.get_or_create(
        user_django=user_participante4,
        defaults={
            "nome": "Joana Muller",
            "email": "joana.muller@estudante.edu.br",
            "cpf": "949.221.639-64",
            "telefone": "(48) 3775-8450",
            "dataNascimento": date(2000, 3, 15),
            "cargo": "Estudante",
            "formacao": "Graduanda em Engenharia de Software",
            "empresa": "",
            "biografia": "Joana Muller é graduanda em Engenharia de Software.\nApaixonada por desenvolvimento web e metodologias ágeis, dedica-se a projetos acadêmicos e inovação tecnológica."
        }
    )
    atribuir_imagem_do_disco(usuario_participante4, 'fotoPerfil', 'media/popular_iniciais/perfis/participante4.png', 'perfis')
    
    # PARTICIPANTE 5
    user_participante5, created_participante5 = User.objects.get_or_create(
        username="sofia_ux",
        defaults={
            "email": "sofia.almeida@gmail.com.br",
            "first_name": "Sofia",
            "last_name": "Almeida"
        }
    )
    if created_participante5:
        user_participante5.set_password('participante5')
        user_participante5.save()

    usuario_participante5, _ = Usuario.objects.get_or_create(
        user_django=user_participante5,
        defaults={
            "nome": "Sofia Almeida",
            "email": "sofia.almeida@gmail.com.br",
            "cpf": "233.324.679-05",
            "telefone": "(47) 99234-1122",
            "dataNascimento": date(1996, 4, 12),
            "cargo": "Product Designer (UX/UI)",
            "formacao": "Bacharela em Design Digital",
            "empresa": "Neogrid",
            "biografia": "Sofia Almeida é Bacharela em Design Digital e atua como Product Designer na Neogrid.\nEspecialista em experiência do usuário e interfaces acessíveis, transforma problemas complexos em jornadas intuitivas."
        }
    )
    atribuir_imagem_do_disco(usuario_participante5, 'fotoPerfil', 'media/popular_iniciais/perfis/participante5.png', 'perfis')
    
    # PARTICIPANTE 6 
    user_participante6, created_participante6 = User.objects.get_or_create(
        username="dr_rafael_bio",
        defaults={
            "email": "rafael.costa96@outlook.com",
            "first_name": "Rafael",
            "last_name": "Costa"
        }
    )
    if created_participante6:
        user_participante6.set_password('participante6')
        user_participante6.save()

    usuario_participante6, _ = Usuario.objects.get_or_create(
        user_django=user_participante6,
        defaults={
            "nome": "Rafael Costa",
            "email": "rafael.costa96@outlook.com",
            "cpf": "352.314.089-72",
            "telefone": "(41) 98765-4321",
            "dataNascimento": date(1989, 9, 28),
            "cargo": "Pesquisador em Bioinformática",
            "formacao": "Doutor em Biotecnologia",
            "empresa": "Instituto Pequeno Príncipe",
            "biografia": "Rafael Costa é Doutor em Biotecnologia e atua como Pesquisador em Bioinformática.\nDedica-se à análise de dados genômicos e ao uso de algoritmos para acelerar diagnósticos na área da saúde."
        }
    )
    atribuir_imagem_do_disco(usuario_participante6, 'fotoPerfil', 'media/popular_iniciais/perfis/participante6.png', 'perfis')
    
    # PARTICIPANTE 7 
    user_participante7, created_participante7 = User.objects.get_or_create(
        username="clara_pm",
        defaults={
            "email": "clara.nogueirassa15@hotmail.com",
            "first_name": "Clara",
            "last_name": "Nogueira"
        }
    )
    if created_participante7:
        user_participante7.set_password('participante7')
        user_participante7.save()

    usuario_participante7, _ = Usuario.objects.get_or_create(
        user_django=user_participante7,
        defaults={
            "nome": "Clara Nogueira",
            "email": "clara.nogueira@hotmail.com",
            "cpf": "325.744.429-03",
            "telefone": "(11) 98123-9876",
            "dataNascimento": date(1991, 1, 19),
            "cargo": "Gerente de Produto (PM)",
            "formacao": "MBA em Gestão de Projetos e Inovação",
            "empresa": "Asaas",
            "biografia": "Clara Nogueira possui MBA em Gestão de Projetos e atua como Gerente de Produto no Asaas.\nFocada em métricas de crescimento e metodologias ágeis, lidera equipes multidisciplinares no setor financeiro."
        }
    )
    atribuir_imagem_do_disco(usuario_participante7, 'fotoPerfil', 'media/popular_iniciais/perfis/participante7.png', 'perfis')
    
    # PARTICIPANTE 8 
    user_participante8, created_participante8 = User.objects.get_or_create(
        username="thiago_lgpd",
        defaults={
            "email": "thiago.martins.adv@advdigital.com.br",
            "first_name": "Thiago",
            "last_name": "Martins"
        }
    )
    if created_participante8:
        user_participante8.set_password('participante8')
        user_participante8.save()

    usuario_participante8, _ = Usuario.objects.get_or_create(
        user_django=user_participante8,
        defaults={
            "nome": "Thiago Martins",
            "email": "thiago.martins.adv@advdigital.com.br",
            "cpf": "086.927.799-54",
            "telefone": "(48) 99654-3210",
            "dataNascimento": date(1993, 6, 7),
            "cargo": "Consultor de Privacidade e DPO",
            "formacao": "Especialista em Direito Digital",
            "empresa": "RD Station",
            "biografia": "Thiago Martins é Especialista em Direito Digital e atua como Consultor de Privacidade na RD Station.\nAuxilia empresas na adequação à LGPD, governança de dados e segurança jurídica em ambientes digitais."
        }
    )
    atribuir_imagem_do_disco(usuario_participante8, 'fotoPerfil', 'media/popular_iniciais/perfis/participante8.png', 'perfis')

    # PARTICIPANTE 9
    user_participante9, created_participante9 = User.objects.get_or_create(
        username="fernanda_growth",
        defaults={
            "email": "fernanda.lima@gmail.com",
            "first_name": "Fernanda",
            "last_name": "Lima"
        }
    )
    if created_participante9:
        user_participante9.set_password('participante9')
        user_participante9.save()

    usuario_participante9, _ = Usuario.objects.get_or_create(
        user_django=user_participante9,
        defaults={
            "nome": "Fernanda Lima",
            "email": "fernanda.lima@gmail.com",
            "cpf": "045.876.659-32",
            "telefone": "(51) 99345-6789",
            "dataNascimento": date(1998, 12, 3),
            "cargo": "Analista de Growth Marketing",
            "formacao": "Graduada em Publicidade e Propaganda",
            "empresa": "Resultados Digitais",
            "biografia": "Fernanda Lima é Graduada em Publicidade e Propaganda e atua como Analista de Growth Marketing.\nApaixonada por análise de funil e aquisição de clientes, cria estratégias baseadas em dados para escalar negócios."
        }
    )
    atribuir_imagem_do_disco(usuario_participante9, 'fotoPerfil', 'media/popular_iniciais/perfis/participante9.png', 'perfis')
    
    
    # PARTICIPANTE 10 
    user_participante10, created_participante10 = User.objects.get_or_create(
        username="pedro_robotica",
        defaults={
            "email": "pedro.henrique3@estudante.edu.br",
            "first_name": "Pedro",
            "last_name": "Henrique"
        }
    )
    if created_participante10:
        user_participante10.set_password('participante10')
        user_participante10.save()

    usuario_participante10, _ = Usuario.objects.get_or_create(
        user_django=user_participante10,
        defaults={
            "nome": "Pedro Henrique",
            "email": "pedro.henrique3@estudante.edu.br",
            "cpf": "166.310.429-84",
            "telefone": "(47) 98456-7890",
            "dataNascimento": date(2002, 8, 21),
            "cargo": "Bolsista de Iniciação Científica",
            "formacao": "Graduando em Engenharia Mecatrônica",
            "empresa": "Laboratório de Robótica UFSC",
            "biografia": "Pedro Henrique é graduando em Engenharia Mecatrônica e bolsista de iniciação científica.\nPesquisa sistemas embarcados e robótica autônoma, participando ativamente de competições universitárias."
        }
    )
    atribuir_imagem_do_disco(usuario_participante10, 'fotoPerfil', 'media/popular_iniciais/perfis/participante10.png', 'perfis')
    
    # PARTICIPANTE 11 
    user_participante11, created_participante11 = User.objects.get_or_create(
        username="bruno_agro",
        defaults={
            "email": "brunoooliveira@gmail.com.br",
            "first_name": "Bruno",
            "last_name": "Oliveira"
        }
    )
    if created_participante11:
        user_participante11.set_password('participante11')
        user_participante11.save()

    usuario_participante11, _ = Usuario.objects.get_or_create(
        user_django=user_participante11,
        defaults={
            "nome": "Bruno Oliveira",
            "email": "brunoooliveira@gmail.com.br",
            "cpf": "562.363.479-64",
            "telefone": "(62) 99876-5432",
            "dataNascimento": date(1987, 2, 14),
            "cargo": "Coordenador de Inovação Agro",
            "formacao": "Mestre em Engenharia Agronômica",
            "empresa": "AgroTech Brasil",
            "biografia": "Bruno Oliveira é Mestre em Engenharia Agronômica e Coordenador de Inovação na AgroTech Brasil.\nTrabalha com agricultura de precisão e sensoriamento remoto para promover a sustentabilidade no campo."
        }
    )
    atribuir_imagem_do_disco(usuario_participante11, 'fotoPerfil', 'media/popular_iniciais/perfis/participante11.png', 'perfis')
    
     # PARTICIPANTE 12 
    user_participante12, created_participante12 = User.objects.get_or_create(
        username="helena_psico",
        defaults={
            "email": "helena.ribeiro@rhcultura.com.br",
            "first_name": "Helena",
            "last_name": "Ribeiro"
        }
    )
    if created_participante12:
        user_participante12.set_password('participante2')
        user_participante12.save()

    usuario_participante12, _ = Usuario.objects.get_or_create(
        user_django=user_participante12,
        defaults={
            "nome": "Helena Ribeiro",
            "email": "helena.ribeiro@rhcultura.com.br",
            "cpf": "364.343.809-50",
            "telefone": "(47) 99145-8822",
            "dataNascimento": date(1992, 5, 18),
            "cargo": "Psicóloga Organizacional",
            "formacao": "Especialista em Psicologia do Trabalho",
            "empresa": "Consultoria RH Cultura",
            "biografia": "Helena Ribeiro é Especialista em Psicologia do Trabalho e atua como Psicóloga Organizacional.\nDedica-se à saúde mental no ambiente corporativo, desenvolvimento de lideranças e cultura inclusiva."
        }
    )
    atribuir_imagem_do_disco(usuario_participante12, 'fotoPerfil', 'media/popular_iniciais/perfis/participante2.png', 'perfis')
    
    
    # PARTICIPANTE 13 
    user_participante13, created_participante13 = User.objects.get_or_create(
        username="mateus_historia",
        defaults={
            "email": "mateus.cardoso@museuhistorico.org.br",
            "first_name": "Mateus",
            "last_name": "Cardoso"
        }
    )
    if created_participante13:
        user_participante13.set_password('participante3')
        user_participante13.save()

    usuario_participante13, _ = Usuario.objects.get_or_create(
        user_django=user_participante13,
        defaults={
            "nome": "Mateus Cardoso",
            "email": "mateus.cardoso@museuhistorico.org.br",
            "cpf": "410.119.129-88",
            "telefone": "(48) 98834-5511",
            "dataNascimento": date(1986, 10, 9),
            "cargo": "Historiador e Curador",
            "formacao": "Doutor em História Social",
            "empresa": "Fundação Cultural Catarinense",
            "biografia": "Mateus Cardoso é Doutor em História Social e atua como Historiador e Curador.\nPesquisa preservação de acervos digitais, memória urbana e políticas públicas de patrimônio cultural."
        }
    )
    atribuir_imagem_do_disco(usuario_participante13, 'fotoPerfil', 'media/popular_iniciais/perfis/participante3.png', 'perfis')
    

    # PARTICIPANTE 14  
    user_participante14, created_participante14 = User.objects.get_or_create(
        username="juliana_socio",
        defaults={
            "email": "juliana.barros@observatoriosocial.org.br",
            "first_name": "Juliana",
            "last_name": "Barros"
        }
    )
    if created_participante14:
        user_participante14.set_password('participante14')
        user_participante14.save()

    usuario_participante14, _ = Usuario.objects.get_or_create(
        user_django=user_participante14,
        defaults={
            "nome": "Juliana Barros",
            "email": "juliana.barros@observatoriosocial.org.br",
            "cpf": "372.785.819-23",
            "telefone": "(41) 99712-3344",
            "dataNascimento": date(1994, 7, 25),
            "cargo": "Analista de Impacto Social",
            "formacao": "Mestra em Sociologia Política",
            "empresa": "Instituto Cidades Sustentáveis",
            "biografia": "Juliana Barros é Mestra em Sociologia Política e atua como Analista de Impacto Social.\nTrabalha com indicadores sociais, participação cidadã e avaliação de projetos comunitários."
        }
    )
    atribuir_imagem_do_disco(usuario_participante14, 'fotoPerfil', 'media/popular_iniciais/perfis/participante14.png', 'perfis')
    
    
    # PARTICIPANTE 15 
    user_participante15, created_participante15 = User.objects.get_or_create(
        username="gabriel_letras",
        defaults={
            "email": "gabriel.santos@editorasul.com.br",
            "first_name": "Gabriel",
            "last_name": "Santos"
        }
    )
    if created_participante15:
        user_participante15.set_password('participante15')
        user_participante15.save()

    usuario_participante15, _ = Usuario.objects.get_or_create(
        user_django=user_participante15,
        defaults={
            "nome": "Gabriel Santos",
            "email": "gabriel.santos@editorasul.com.br",
            "cpf": "756.651.889-56",
            "telefone": "(51) 98421-7788",
            "dataNascimento": date(1990, 2, 11),
            "cargo": "Editor e Revisor Textual",
            "formacao": "Licenciado em Letras - Português e Inglês",
            "empresa": "Editora Horizonte",
            "biografia": "Gabriel Santos é Licenciado em Letras e atua como Editor e Revisor Textual na Editora Horizonte.\nApaixonado por literatura contemporânea e linguística aplicada, coordena publicações acadêmicas e literárias."
        }
    )
    atribuir_imagem_do_disco(usuario_participante15, 'fotoPerfil', 'media/popular_iniciais/perfis/participante15.jpg', 'perfis')
    
    # PARTICIPANTE 16 
    user_participante16, created_participante16 = User.objects.get_or_create(
        username="patricia_pedagoga",
        defaults={
            "email": "patricia.gomes@educacao.edu.br",
            "first_name": "Patrícia",
            "last_name": "Gomes"
        }
    )
    if created_participante16:
        user_participante16.set_password('participante16')
        user_participante16.save()

    usuario_participante16, _ = Usuario.objects.get_or_create(
        user_django=user_participante16,
        defaults={
            "nome": "Patrícia Gomes",
            "email": "patricia.gomes@educacao.edu.br",
            "cpf": "530.981.499-06",
            "telefone": "(47) 99632-9900",
            "dataNascimento": date(1985, 11, 30),
            "cargo": "Coordenadora Pedagógica",
            "formacao": "Mestra em Educação e Inclusão",
            "empresa": "Colégio Inovação",
            "biografia": "Patrícia Gomes é Mestra em Educação e atua como Coordenadora Pedagógica no Colégio Inovação.\nEspecialista em metodologias ativas e educação inclusiva, apoia docentes na criação de currículos acessíveis."
        }
    )
    atribuir_imagem_do_disco(usuario_participante16, 'fotoPerfil', 'media/popular_iniciais/perfis/participante16.png', 'perfis')
    
    # PARTICIPANTE 17
    user_participante17, created_participante17 = User.objects.get_or_create(
        username="rodrigo_filosofia",
        defaults={
            "email": "rodrigo.melo@universidade.edu.br",
            "first_name": "Rodrigo",
            "last_name": "Melo"
        }
    )
    if created_participante17:
        user_participante17.set_password('participante17')
        user_participante17.save()

    usuario_participante17, _ = Usuario.objects.get_or_create(
        user_django=user_participante17,
        defaults={
            "nome": "Rodrigo Melo",
            "email": "rodrigo.melo@universidade.edu.br",
            "cpf": "987.805.929-45",
            "telefone": "(11) 98234-6677",
            "dataNascimento": date(1988, 3, 14),
            "cargo": "Professor de Ética e Filosofia",
            "formacao": "Doutor em Filosofia Contemporânea",
            "empresa": "Universidade Federal De Santa Catarina",
            "biografia": "Rodrigo Melo é Doutor em Filosofia Contemporânea e Professor Universitário.\nPesquisa ética aplicada à inteligência artificial, epistemologia e impactos filosóficos da era digital."
        }
    )
    atribuir_imagem_do_disco(usuario_participante17, 'fotoPerfil', 'media/popular_iniciais/perfis/participante17.jpg', 'perfis')
    
    # PARTICIPANTE 18
    user_participante18, created_participante18 = User.objects.get_or_create(
        username="amanda_social",
        defaults={
            "email": "amanda.castro@redesolidaria.ong.br",
            "first_name": "Amanda",
            "last_name": "Castro"
        }
    )
    if created_participante18:
        user_participante18.set_password('participante18')
        user_participante18.save()

    usuario_participante18, _ = Usuario.objects.get_or_create(
        user_django=user_participante18,
        defaults={
            "nome": "Amanda Castro",
            "email": "amanda.castro@redesolidaria.ong.br",
            "cpf": "912.166.829-92",
            "telefone": "(49) 99543-2211",
            "dataNascimento": date(1995, 8, 4),
            "cargo": "Assistente Social",
            "formacao": "Bacharela em Serviço Social",
            "empresa": "ONG Rede Solidária",
            "biografia": "Amanda Castro é Bacharela em Serviço Social e atua na ONG Rede Solidária.\nFocada em direitos humanos e assistência comunitária, coordena programas de acolhimento e geração de renda."
        }
    )
    atribuir_imagem_do_disco(usuario_participante18, 'fotoPerfil', 'media/popular_iniciais/perfis/participante18.png', 'perfis')
    
    # PARTICIPANTE 19 
    user_participante19, created_participante19 = User.objects.get_or_create(
        username="vinicius_jornal",
        defaults={
            "email": "vinicius.teixeira@outlook.com.br",
            "first_name": "Vinícius",
            "last_name": "Teixeira"
        }
    )
    if created_participante19:
        user_participante19.set_password('participante19')
        user_participante19.save()

    usuario_participante19, _ = Usuario.objects.get_or_create(
        user_django=user_participante19,
        defaults={
            "nome": "Vinícius Teixeira",
            "email": "vinicius.teixeira@outlook.com.br",
            "cpf": "980.018.659-08",
            "telefone": "(21) 98976-4433",
            "dataNascimento": date(1997, 9, 17),
            "cargo": "Jornalista Investigativo",
            "formacao": "Bacharel em Jornalismo",
            "empresa": "Portal Brasil com S",
            "biografia": "Vinícius Teixeira é Bacharel em Jornalismo e atua como Jornalista Investigativo.\nEspecializado em jornalismo de dados e checagem de fatos, produz reportagens sobre transparência pública."
        }
    )
    atribuir_imagem_do_disco(usuario_participante19, 'fotoPerfil', 'media/popular_iniciais/perfis/participante19.jpg', 'perfis')
    
    # PARTICIPANTE 20 
    user_participante20, created_participante20 = User.objects.get_or_create(
        username="larissa_ri",
        defaults={
            "email": "larissa.monteiro087@estudante.edu.br",
            "first_name": "Larissa",
            "last_name": "Monteiro"
        }
    )
    if created_participante20:
            user_participante20.set_password('participante20')
            user_participante20.save()
            
    usuario_participante20, _ = Usuario.objects.get_or_create(
        user_django=user_participante20,
        defaults={
            "nome": "Larissa Monteiro",
            "email": "larissa.monteiro087@estudante.edu.br",
            "cpf": "973.011.029-84",
            "telefone": "(61) 99123-7744",
            "dataNascimento": date(2003, 1, 29),
            "cargo": "",
            "formacao": "Graduanda em Relações Internacionais",
            "empresa": "",
            "biografia": "Larissa Monteiro é graduanda em Relações Internacionais e estagiária em Cooperação Internacional.\nInteressada em diplomacia cultural e comércio exterior, participa de simulações da ONU e grupos de pesquisa."
        }
    )    
    atribuir_imagem_do_disco(usuario_participante20, 'fotoPerfil', 'media/popular_iniciais/perfis/participante20.png', 'perfis')
    
    
    
    # -------------------------------------------------------------
    # 2. APOIADORES
    # -------------------------------------------------------------
    apoiador_1, _ = Apoiador.objects.get_or_create(nome="Conselho de Tecnologia")
    apoiador_2, _ = Apoiador.objects.get_or_create(nome="Tech Innovation Lab")
    apoiador_3, _ = Apoiador.objects.get_or_create(nome="Instituto Federal de Santa Catarina")
    apoiador_4, _ = Apoiador.objects.get_or_create(nome="Fundação Catarinense de Pesquisa e Saúde")
    apoiador_5, _ = Apoiador.objects.get_or_create(nome="Associação Sul-Brasileira de Energias Limpas")
    apoiador_6, _ = Apoiador.objects.get_or_create(nome="Instituto Brasileiro de Direito Digital (IBDD)")
    apoiador_7, _ = Apoiador.objects.get_or_create(nome="Conselho de Arquitetura e Design Criativo")
    apoiador_8, _ = Apoiador.objects.get_or_create(nome="Cooperativa AgroInova Sul")
    apoiador_9, _ = Apoiador.objects.get_or_create(nome="Federação das Indústrias e Automação (FIASC)")
    apoiador_10, _ = Apoiador.objects.get_or_create(nome="Secretaria Regional de Cultura e Turismo")

    # -------------------------------------------------------------
    # 3. EVENTO
    # -------------------------------------------------------------

    hoje = date.today()
    
    #EVENTO 1 - Em andamento (3 apoiadores)
    evento1, _ = Evento.objects.get_or_create(
        nome="Semana Acadêmica de Tecnologia 2026",
        defaults={
            "administrador": usuario_admin,
            "descricao": "Evento focado em tecnologia, inovação e desafios práticos.",
            "emailContato": "contato@semanaacademica.com",
            "local": "Universidade Tecnologica do Paraná - Curitiba ",
            "dataInicio": hoje - timedelta(days=2),
            "dataFim": hoje + timedelta(days=3),
            "tipoEvento": tipoEvento.SEMANA,
        }
    )
    evento1.apoiadores.set([apoiador_1, apoiador_2, apoiador_3])
    atribuir_imagem_do_disco(evento1, 'imagemBanner', 'media/popular_iniciais/banners/evento1.png', 'banners')

    # EVENTO 2 - Já encerrado (1 apoiador)
    evento2, _ = Evento.objects.get_or_create(
        nome="Palestra Internacional de Administração 2026",
        defaults={
            "administrador": usuario_admin,
            "descricao": "Palestra focada em administração, inovação e desafios práticos.",
            "emailContato": "contato@ifsc.com",
            "local": "Instituto Federal de Santa Catarina - Campus Florianópolis",
            "dataInicio": hoje - timedelta(days=14),
            "dataFim": hoje - timedelta(days=10),
            "tipoEvento": tipoEvento.OUTRO,
        }
    )
    evento2.apoiadores.set([apoiador_3])
    atribuir_imagem_do_disco(evento2, 'imagemBanner', 'media/popular_iniciais/banners/evento2.png', 'banners')

    # EVENTO 3 - Já encerrado (2 apoiadores)
    evento3, _ = Evento.objects.get_or_create(
        nome="Fórum de Gestão de Projetos de Tecnologia 2026",
        defaults={
            "administrador": usuario_admin,
            "descricao": "Fórum dedicado à gestão de projetos em tecnologia.",
            "emailContato": "contato@ifsc.com",
            "local": "Instituto Federal de Santa Catarina - Campus Rau",
            "dataInicio": hoje - timedelta(days=8),
            "dataFim": hoje - timedelta(days=4),
            "tipoEvento": tipoEvento.FORUM,
        }
    )
    evento3.apoiadores.set([apoiador_1, apoiador_3])
    atribuir_imagem_do_disco(evento3, 'imagemBanner', 'media/popular_iniciais/banners/evento3.png', 'banners')

    # EVENTO 4 - Saúde - Em andamento (2 apoiadores)
    evento4, _ = Evento.objects.get_or_create(
        nome="Congresso Brasileiro de Saúde e Biotecnologia 2026",
        defaults={
            "administrador": usuario_admin,
            "descricao": "Discussões sobre avanços clínicos, telemedicina e pesquisas em biotecnologia.",
            "emailContato": "contato@saudebio2026.com.br",
            "local": "Universidade Federal de Santa Catarina - Florianópolis",
            "dataInicio": hoje - timedelta(days=2),
            "dataFim": hoje + timedelta(days=3),
            "tipoEvento": tipoEvento.OUTRO,
        }
    )
    evento4.apoiadores.set([apoiador_4, apoiador_2])
    atribuir_imagem_do_disco(evento4, 'imagemBanner', 'media/popular_iniciais/banners/evento4.jpg', 'banners')

    # EVENTO 5 - Meio Ambiente - Já encerrado (1 apoiador)
    evento5, _ = Evento.objects.get_or_create(
        nome="Simpósio Sul de Energias Renováveis e Sustentabilidade",
        defaults={
            "administrador": usuario_admin,
            "descricao": "Encontro voltado para transição energética, ESG e preservação ambiental.",
            "emailContato": "simposio@energiasul.org.br",
            "local": "Centro de Convenções Expoville - Joinville",
            "dataInicio": hoje - timedelta(days=22),
            "dataFim": hoje - timedelta(days=20),
            "tipoEvento": tipoEvento.SIMPOSIO,
        }
    )
    evento5.apoiadores.set([apoiador_5])
    atribuir_imagem_do_disco(evento5, 'imagemBanner', 'media/popular_iniciais/banners/evento5.jpg', 'banners')

    # EVENTO 6 - Direito - Em andamento (2 apoiadores)
    evento6, _ = Evento.objects.get_or_create(
        nome="Fórum Nacional de Direito Digital e Proteção de Dados",
        defaults={
            "administrador": usuario_admin,
            "descricao": "Debates sobre LGPD, inteligência artificial e regulação jurídica no ambiente digital.",
            "emailContato": "eventos@direitodigital2026.com",
            "local": "Pontifícia Universidade Católica do Paraná - Curitiba",
            "dataInicio": hoje - timedelta(days=1),
            "dataFim": hoje + timedelta(days=2),
            "tipoEvento": tipoEvento.FORUM,
        }
    )
    evento6.apoiadores.set([apoiador_6, apoiador_1])
    atribuir_imagem_do_disco(evento6, 'imagemBanner', 'media/popular_iniciais/banners/evento6.jpg', 'banners')

    # EVENTO 7 - Design e Arquitetura - Futuro (1 apoiador)
    evento7, _ = Evento.objects.get_or_create(
        nome="Semana de Design, Arquitetura e Urbanismo Criativo",
        defaults={
            "administrador": usuario_admin,
            "descricao": "Oficinas práticas, exposições e palestras sobre cidades inteligentes e design de produto.",
            "emailContato": "contato@semanadesign.edu.br",
            "local": "Universidade do Estado de Santa Catarina - Joinville",
            "dataInicio": hoje + timedelta(days=7),
            "dataFim": hoje + timedelta(days=12),
            "tipoEvento": tipoEvento.SEMANA,
        }
    )
    evento7.apoiadores.set([apoiador_7])
    atribuir_imagem_do_disco(evento7, 'imagemBanner', 'media/popular_iniciais/banners/evento7.jpg', 'banners')

    # EVENTO 8 - Agronegócio - Futuro (3 apoiadores)
    evento8, _ = Evento.objects.get_or_create(
        nome="Feira de Inovação no Agronegócio e Agricultura 4.0",
        defaults={
            "administrador": usuario_admin2,
            "descricao": "Apresentação de drones, automação rural e soluções sustentáveis para o campo.",
            "emailContato": "agro40@feiraagro.com.br",
            "local": "Parque de Exposições Efapi - Chapecó",
            "dataInicio": hoje + timedelta(days=16),
            "dataFim": hoje + timedelta(days=19),
            "tipoEvento": tipoEvento.FEIRA,
        }
    )
    evento8.apoiadores.set([apoiador_8, apoiador_2, apoiador_5])
    atribuir_imagem_do_disco(evento8, 'imagemBanner', 'media/popular_iniciais/banners/evento8.jpg', 'banners')

    # EVENTO 9 - Engenharia e Indústria - Futuro (3 apoiadores)
    evento9, _ = Evento.objects.get_or_create(
        nome="Semana de Engenharia Mecânica e Automação Industrial",
        defaults={
            "administrador": usuario_admin2,
            "descricao": "Minicursos de robótica, manufatura aditiva e visitas técnicas às indústrias da região.",
            "emailContato": "engenharia@ifsc.edu.br",
            "local": "Instituto Federal de Santa Catarina - Campus Jaraguá do Sul",
            "dataInicio": hoje + timedelta(days=25),
            "dataFim": hoje + timedelta(days=29),
            "tipoEvento": tipoEvento.SEMANA,
        }
    )
    evento9.apoiadores.set([apoiador_9, apoiador_3, apoiador_2])
    atribuir_imagem_do_disco(evento9, 'imagemBanner', 'media/popular_iniciais/banners/evento9.jpg', 'banners')

    # EVENTO 10 - Gastronomia e Turismo - Futuro (0 apoiadores - estado vazio)
    evento10, _ = Evento.objects.get_or_create(
        nome="Fórum Sul-Brasileiro de Gastronomia e Turismo Cultural",
        defaults={
            "administrador": usuario_admin2,
            "descricao": "Cozinha show, valorização de ingredientes regionais e estratégias para o turismo local.",
            "emailContato": "contato@gastroturismo.com.br",
            "local": "Parque Vila Germânica - Blumenau",
            "dataInicio": hoje + timedelta(days=38),
            "dataFim": hoje + timedelta(days=40),
            "tipoEvento": tipoEvento.FORUM,
        }
    )
    evento10.apoiadores.clear()  # 0 apoiadores propositalmente (apoiador_10 fica disponível para testes de vínculo)
    atribuir_imagem_do_disco(evento10, 'imagemBanner', 'media/popular_iniciais/banners/evento10.jpg', 'banners')


    # EVENTO 11 - PI 2
    evento11, _ = Evento.objects.get_or_create(
        nome="Apresentação dos Projetos de PI 2",
        defaults={
            "administrador": usuario_admin4,
            "descricao": "Cozinha show, valorização de ingredientes regionais e estratégias para o turismo local.",
            "emailContato": "contato@ifsc.edu.br",
            "local": "IFSC - RAU ",
            "dataInicio": hoje,
            "dataFim": hoje + timedelta(days=2),
            "tipoEvento": tipoEvento.OUTRO,
        }
    )
    evento11.apoiadores.clear()  # 0 apoiadores propositalmente (apoiador_11 fica disponível para testes de vínculo)
    atribuir_imagem_do_disco(evento11, 'imagemBanner', 'media/popular_iniciais/banners/evento10.jpg', 'banners')

    #====================================
     # ATIVIDADES
    #===================================
    agora = timezone.now()

    # =============================================================
    # EVENTO 1: Semana Acadêmica de Tecnologia 2026 (4 atividades)
    # Período: hoje - 2d até hoje + 2d (Em andamento)
    # =============================================================
    atividade_palestra, _ = Atividade.objects.get_or_create(
        nome="Keynote: Inteligência Computacional no Diagnóstico",
        evento=evento1,
        defaults={
            "descricao": "Palestra introdutória aos desafios tecnológicos atuais.",
            "tipoAtividade": tipoAtividade.PALESTRA,
            "complementoLocal": "Auditório Principal",
            "horaInicio": agora - timedelta(minutes=30),
            "horaFim": agora + timedelta(hours=2),
            "limitePessoas": 200,
        }
    )
    
    atividade_oficina, _ = Atividade.objects.get_or_create(
        nome="Oficina: Desafio Prático de Calibração de Sensores",
        evento=evento1,
        defaults={
            "descricao": "Atividade prática de laboratório com aferição de métricas.",
            "tipoAtividade": tipoAtividade.OFICINA,
            "complementoLocal": "Laboratório 04",
            "horaInicio": agora + timedelta(days=1, hours=2),
            "horaFim": agora + timedelta(days=1, hours=6),
            "limitePessoas": 30,
        }
    )

    atividade_ev1_3, _ = Atividade.objects.get_or_create(
        nome="Oficina: Arquitetura de Microsserviços com Docker e Kubernetes",
        evento=evento1,
        defaults={
            "descricao": "Deploy prático de containers e orquestração em ambiente cloud.",
            "tipoAtividade": tipoAtividade.OFICINA,
            "complementoLocal": "Laboratório de Redes - Bloco B",
            "horaInicio": agora - timedelta(days=1, hours=4),
            "horaFim": agora - timedelta(days=1, hours=1),
            "limitePessoas": 35,
        }
    )

    atividade_ev1_4, _ = Atividade.objects.get_or_create(
        nome="Fórum: Carreira Internacional e Trabalho Remoto na Área de TI",
        evento=evento1,
        defaults={
            "descricao": "Bate-papo com engenheiros de software atuando em empresas globais.",
            "tipoAtividade": tipoAtividade.FORUM,
            "complementoLocal": "Miniauditório 02",
            "horaInicio": agora + timedelta(days=2, hours=1),
            "horaFim": agora + timedelta(days=2, hours=3),
            "limitePessoas": 90,
        }
    )

    # =============================================================
    # EVENTO 2: Palestra Internacional de Administração 2026 (2 atividades)
    # Período: hoje - 14d até hoje - 10d (Encerrado)
    # =============================================================
    atividade_palestra2, _ = Atividade.objects.get_or_create(
        nome="Palestra Internacional de Administração 2026",
        evento=evento2,
        defaults={
            "descricao": "Palestra focada em administração, inovação e desafios práticos.",
            "tipoAtividade": tipoAtividade.PALESTRA,
            "complementoLocal": "Sala 05 - Bloco C",
            "horaInicio": agora - timedelta(days=13, hours=3),
            "horaFim": agora - timedelta(days=13, hours=1),
            "limitePessoas": 45,
        }
    )

    atividade_ev2_2, _ = Atividade.objects.get_or_create(
        nome="Oficina: Planejamento Estratégico e OKRs para Startups",
        evento=evento2,
        defaults={
            "descricao": "Dinâmica prática de definição de metas e indicadores de desempenho.",
            "tipoAtividade": tipoAtividade.OFICINA,
            "complementoLocal": "Sala de Metodologias Ativas",
            "horaInicio": agora - timedelta(days=11, hours=4),
            "horaFim": agora - timedelta(days=11, hours=1),
            "limitePessoas": 30,
        }
    )

    # =============================================================
    # EVENTO 3: Fórum de Gestão de Projetos de Tecnologia 2026 (3 atividades)
    # Período: hoje - 8d até hoje - 4d (Encerrado)
    # =============================================================
    atividade_forum, _ = Atividade.objects.get_or_create(
        nome="Fórum: Gestão de Projetos em Tecnologia",
        evento=evento3,
        defaults={
            "descricao": "Fórum dedicado à gestão de projetos em tecnologia.",
            "tipoAtividade": tipoAtividade.FORUM,
            "complementoLocal": "Auditório Central - Bloco A",
            "horaInicio": agora - timedelta(days=7, hours=4),
            "horaFim": agora - timedelta(days=7, hours=1),
            "limitePessoas": 80,
        }
    )

    atividade_ev3_2, _ = Atividade.objects.get_or_create(
        nome="Oficina: Métricas Ágeis, Kanban e Previsibilidade de Entregas",
        evento=evento3,
        defaults={
            "descricao": "Simulação de fluxo contínuo utilizando Lead Time e Throughput.",
            "tipoAtividade": tipoAtividade.OFICINA,
            "complementoLocal": "Laboratório 02 - Bloco B",
            "horaInicio": agora - timedelta(days=6, hours=3),
            "horaFim": agora - timedelta(days=6),
            "limitePessoas": 40,
        }
    )

    atividade_ev3_3, _ = Atividade.objects.get_or_create(
        nome="Palestra: Gestão de Riscos e Orçamentos em Contratos de Software",
        evento=evento3,
        defaults={
            "descricao": "Estudos de caso sobre mitigação de escopo aberto e precificação.",
            "tipoAtividade": tipoAtividade.PALESTRA,
            "complementoLocal": "Auditório Central - Bloco A",
            "horaInicio": agora - timedelta(days=5, hours=2),
            "horaFim": agora - timedelta(days=5),
            "limitePessoas": 100,
        }
    )

    # =============================================================
    # EVENTO 4: Congresso Brasileiro de Saúde e Biotecnologia 2026 (5 atividades)
    # Período: hoje - 1d até hoje + 2d (Em andamento)
    # =============================================================
    atividade_ev4_1, _ = Atividade.objects.get_or_create(
        nome="Palestra: Edição Genética CRISPR e Terapias Avançadas",
        evento=evento4,
        defaults={
            "descricao": "Panorama das pesquisas clínicas recentes em terapia gênica.",
            "tipoAtividade": tipoAtividade.PALESTRA,
            "complementoLocal": "Auditório Garapuvu",
            "horaInicio": agora - timedelta(days=1, hours=3),
            "horaFim": agora - timedelta(days=1, hours=1),
            "limitePessoas": 250,
        }
    )

    atividade_ev4_2, _ = Atividade.objects.get_or_create(
        nome="Fórum: Desafios Éticos e Regulatórios da Telemedicina no SUS",
        evento=evento4,
        defaults={
            "descricao": "Debate com gestores hospitalares e pesquisadores de saúde pública.",
            "tipoAtividade": tipoAtividade.FORUM,
            "complementoLocal": "Sala Plenária 01",
            "horaInicio": agora - timedelta(minutes=45),
            "horaFim": agora + timedelta(hours=2),
            "limitePessoas": 120,
        }
    )

    atividade_ev4_3, _ = Atividade.objects.get_or_create(
        nome="Oficina: Biossegurança e Boas Práticas em Laboratório Molecular",
        evento=evento4,
        defaults={
            "descricao": "Protocolos de contenção e manipulação de amostras biológicas.",
            "tipoAtividade": tipoAtividade.OFICINA,
            "complementoLocal": "Lab. de Biotecnologia - CCS",
            "horaInicio": agora + timedelta(days=1, hours=1),
            "horaFim": agora + timedelta(days=1, hours=4),
            "limitePessoas": 25,
        }
    )

    atividade_ev4_4, _ = Atividade.objects.get_or_create(
        nome="Palestra: Inteligência Artificial Aplicada à Triagem Hospitalar",
        evento=evento4,
        defaults={
            "descricao": "Modelos preditivos para redução de tempo de espera em emergências.",
            "tipoAtividade": tipoAtividade.PALESTRA,
            "complementoLocal": "Auditório Garapuvu",
            "horaInicio": agora + timedelta(days=1, hours=5),
            "horaFim": agora + timedelta(days=1, hours=7),
            "limitePessoas": 250,
        }
    )

    atividade_ev4_5, _ = Atividade.objects.get_or_create(
        nome="Oficina: Análise de Dados Epidemiológicos com Python",
        evento=evento4,
        defaults={
            "descricao": "Tratamento e visualização de séries temporais do DataSUS.",
            "tipoAtividade": tipoAtividade.OFICINA,
            "complementoLocal": "Laboratório de Informática 03",
            "horaInicio": agora + timedelta(days=2, hours=1),
            "horaFim": agora + timedelta(days=2, hours=4),
            "limitePessoas": 35,
        }
    )

    # =============================================================
    # EVENTO 5: Simpósio Sul de Energias Renováveis e Sustentabilidade (0 atividades)
    # Período: hoje - 22d até hoje - 20d (Encerrado - Evento sem atividades cadastradas)
    # =============================================================
    # Nenhuma atividade criada propositalmente para testar o estado vazio (0 atividades).

    # =============================================================
    # EVENTO 6: Fórum Nacional de Direito Digital e Proteção de Dados (3 atividades)
    # Período: hoje - 1d até hoje + 1d (Em andamento)
    # =============================================================
    atividade_ev6_1, _ = Atividade.objects.get_or_create(
        nome="Palestra: Responsabilidade Civil e Direitos Autorais em Modelos de IA",
        evento=evento6,
        defaults={
            "descricao": "Análise jurídica sobre treinamento de algoritmos e propriedade intelectual.",
            "tipoAtividade": tipoAtividade.PALESTRA,
            "complementoLocal": "Auditório Gregor Mendel",
            "horaInicio": agora - timedelta(days=1, hours=2),
            "horaFim": agora - timedelta(days=1),
            "limitePessoas": 180,
        }
    )

    atividade_ev6_2, _ = Atividade.objects.get_or_create(
        nome="Fórum: Fiscalização da ANPD e Incidentes de Vazamento de Dados",
        evento=evento6,
        defaults={
            "descricao": "Discussão prática sobre planos de resposta a incidentes sob a LGPD.",
            "tipoAtividade": tipoAtividade.FORUM,
            "complementoLocal": "Sala de Conferências 02",
            "horaInicio": agora - timedelta(minutes=20),
            "horaFim": agora + timedelta(hours=2),
            "limitePessoas": 100,
        }
    )

    atividade_ev6_3, _ = Atividade.objects.get_or_create(
        nome="Oficina: Elaboração de Relatório de Impacto à Proteção de Dados (RIPD)",
        evento=evento6,
        defaults={
            "descricao": "Workshop prático de mapeamento de fluxos e matriz de risco.",
            "tipoAtividade": tipoAtividade.OFICINA,
            "complementoLocal": "Sala 204 - Escola de Direito",
            "horaInicio": agora + timedelta(days=1, hours=2),
            "horaFim": agora + timedelta(days=1, hours=5),
            "limitePessoas": 40,
        }
    )

    # =============================================================
    # EVENTO 7: Semana de Design, Arquitetura e Urbanismo Criativo (6 atividades)
    # Período: hoje + 7d até hoje + 11d (Futuro)
    # =============================================================
    atividade_ev7_1, _ = Atividade.objects.get_or_create(
        nome="Palestra: Cidades Esponja e Drenagem Urbana Sustentável",
        evento=evento7,
        defaults={
            "descricao": "Soluções arquitetônicas para resiliência climática em centros urbanos.",
            "tipoAtividade": tipoAtividade.PALESTRA,
            "complementoLocal": "Auditório do Bloco F",
            "horaInicio": agora + timedelta(days=7, hours=2),
            "horaFim": agora + timedelta(days=7, hours=4),
            "limitePessoas": 150,
        }
    )

    atividade_ev7_2, _ = Atividade.objects.get_or_create(
        nome="Oficina: Prototipagem Rápida com Impressão 3D e Corte a Laser",
        evento=evento7,
        defaults={
            "descricao": "Fabricação digital de maquetes e modelos físicos de produto.",
            "tipoAtividade": tipoAtividade.OFICINA,
            "complementoLocal": "FabLab UDESC",
            "horaInicio": agora + timedelta(days=8, hours=1),
            "horaFim": agora + timedelta(days=8, hours=5),
            "limitePessoas": 20,
        }
    )

    atividade_ev7_3, _ = Atividade.objects.get_or_create(
        nome="Oficina: Design Systems e Acessibilidade Digital no Figma",
        evento=evento7,
        defaults={
            "descricao": "Construção de bibliotecas de componentes seguindo diretrizes WCAG.",
            "tipoAtividade": tipoAtividade.OFICINA,
            "complementoLocal": "Laboratório de Design Digital",
            "horaInicio": agora + timedelta(days=9, hours=2),
            "horaFim": agora + timedelta(days=9, hours=5),
            "limitePessoas": 30,
        }
    )

    atividade_ev7_4, _ = Atividade.objects.get_or_create(
        nome="Fórum: Mobilidade Ativa e Requalificação de Espaços Públicos",
        evento=evento7,
        defaults={
            "descricao": "Mesa-redonda com urbanistas e coletivos locais sobre ciclovias e calçadas.",
            "tipoAtividade": tipoAtividade.FORUM,
            "complementoLocal": "Espaço de Convivência",
            "horaInicio": agora + timedelta(days=9, hours=6),
            "horaFim": agora + timedelta(days=9, hours=8),
            "limitePessoas": 85,
        }
    )

    atividade_ev7_5, _ = Atividade.objects.get_or_create(
        nome="Palestra: Design Biofílico e Conforto Ambiental em Interiores",
        evento=evento7,
        defaults={
            "descricao": "Integração de iluminação natural, acústica e vegetação em projetos.",
            "tipoAtividade": tipoAtividade.PALESTRA,
            "complementoLocal": "Auditório do Bloco F",
            "horaInicio": agora + timedelta(days=10, hours=2),
            "horaFim": agora + timedelta(days=10, hours=4),
            "limitePessoas": 150,
        }
    )

    atividade_ev7_6, _ = Atividade.objects.get_or_create(
        nome="Oficina: Fotografia de Arquitetura e Composição Visual",
        evento=evento7,
        defaults={
            "descricao": "Saída fotográfica pelo campus com foco em perspectiva e luz natural.",
            "tipoAtividade": tipoAtividade.OFICINA,
            "complementoLocal": "Hall Principal",
            "horaInicio": agora + timedelta(days=11, hours=1),
            "horaFim": agora + timedelta(days=11, hours=4),
            "limitePessoas": 25,
        }
    )

    # =============================================================
    # EVENTO 8: Feira de Inovação no Agronegócio e Agricultura 4.0 (2 atividades)
    # Período: hoje + 16d até hoje + 19d (Futuro)
    # =============================================================
    atividade_ev8_1, _ = Atividade.objects.get_or_create(
        nome="Oficina: Mapeamento Aéreo com Drones e Índice NDVI",
        evento=evento8,
        defaults={
            "descricao": "Processamento de imagens multiespectrais para monitoramento de lavouras.",
            "tipoAtividade": tipoAtividade.OFICINA,
            "complementoLocal": "Pista de Demonstração Externa",
            "horaInicio": agora + timedelta(days=16, hours=2),
            "horaFim": agora + timedelta(days=16, hours=5),
            "limitePessoas": 40,
        }
    )

    atividade_ev8_2, _ = Atividade.objects.get_or_create(
        nome="Fórum: Conectividade Rural (IoT/LoRaWAN) e Automação na Suinocultura",
        evento=evento8,
        defaults={
            "descricao": "Painel sobre telemetria de climatização e rastreabilidade no oeste catarinense.",
            "tipoAtividade": tipoAtividade.FORUM,
            "complementoLocal": "Pavilhão 02 - Arena Agro",
            "horaInicio": agora + timedelta(days=18, hours=3),
            "horaFim": agora + timedelta(days=18, hours=5),
            "limitePessoas": 140,
        }
    )

    # =============================================================
    # EVENTO 9: Semana de Engenharia Mecânica e Automação Industrial (4 atividades)
    # Período: hoje + 25d até hoje + 29d (Futuro)
    # =============================================================
    atividade_ev9_1, _ = Atividade.objects.get_or_create(
        nome="Oficina: Programação de CLPs e Redes Industriais Profinet",
        evento=evento9,
        defaults={
            "descricao": "Configuração de controladores lógicos programáveis em bancada didática.",
            "tipoAtividade": tipoAtividade.OFICINA,
            "complementoLocal": "Lab. de Automação Industrial",
            "horaInicio": agora + timedelta(days=25, hours=2),
            "horaFim": agora + timedelta(days=25, hours=6),
            "limitePessoas": 24,
        }
    )

    atividade_ev9_2, _ = Atividade.objects.get_or_create(
        nome="Palestra: Manutenção Preditiva com Análise de Vibração e IA",
        evento=evento9,
        defaults={
            "descricao": "Monitoramento de motores elétricos e redutores na indústria 4.0.",
            "tipoAtividade": tipoAtividade.PALESTRA,
            "complementoLocal": "Auditório IFSC Jaraguá",
            "horaInicio": agora + timedelta(days=26, hours=3),
            "horaFim": agora + timedelta(days=26, hours=5),
            "limitePessoas": 160,
        }
    )

    atividade_ev9_3, _ = Atividade.objects.get_or_create(
        nome="Oficina: Simulação Estrutural por Elementos Finitos (FEA)",
        evento=evento9,
        defaults={
            "descricao": "Análise de tensões e deformações em componentes mecânicos.",
            "tipoAtividade": tipoAtividade.OFICINA,
            "complementoLocal": "Laboratório de CAD/CAE",
            "horaInicio": agora + timedelta(days=27, hours=2),
            "horaFim": agora + timedelta(days=27, hours=5),
            "limitePessoas": 30,
        }
    )

    atividade_ev9_4, _ = Atividade.objects.get_or_create(
        nome="Fórum: Eficiência Energética e Descarbonização na Indústria Metalmecânica",
        evento=evento9,
        defaults={
            "descricao": "Debate com engenheiros industriais da região sobre matriz energética limpa.",
            "tipoAtividade": tipoAtividade.FORUM,
            "complementoLocal": "Auditório IFSC Jaraguá",
            "horaInicio": agora + timedelta(days=28, hours=4),
            "horaFim": agora + timedelta(days=28, hours=6),
            "limitePessoas": 120,
        }
    )

    # =============================================================
    # EVENTO 10: Fórum Sul-Brasileiro de Gastronomia e Turismo Cultural (1 atividade)
    # Período: hoje + 38d até hoje + 40d (Futuro)
    # =============================================================
    atividade_ev10_1, _ = Atividade.objects.get_or_create(
        nome="Oficina: Fermentação Natural e Panificação Artesanal com Grãos Locais",
        evento=evento10,
        defaults={
            "descricao": "Cozinha show prática com técnicas de levain e farinhas regionais.",
            "tipoAtividade": tipoAtividade.OFICINA,
            "complementoLocal": "Setor 1 - Cozinha Experimental",
            "horaInicio": agora + timedelta(days=39, hours=2),
            "horaFim": agora + timedelta(days=39, hours=5),
            "limitePessoas": 35,
        }
    )
    
    # =============================================================
    # EVENTO 11: PI 1 e 2
    # =============================================================
    atividade_ev10_1, _ = Atividade.objects.get_or_create(
        nome="Primeiro dia de Apresentação dos Projetos do Projeto Integrador I e II",
        evento=evento10,
        defaults={
            "descricao": " Apresentação dos Projetos do Projeto",
            "tipoAtividade": tipoAtividade.OUTRO,
            "complementoLocal": "Auditório - Bloco A",
            "horaInicio": hoje + timedelta(hours=14),
            "horaFim": hoje + timedelta(hours=17),
            "limitePessoas": 60,
        }
    )

    # -------------------------------------------------------------
    # 5. INSCRIÇÕES E 6. PARTICIPAÇÕES NAS ATIVIDADES
    # -------------------------------------------------------------

    Participa.objects.all().delete()

    def inscrever_e_participar(usuario, evento_obj, atividades_lista=None, presentes_lista=None):
        """
        Cria a inscrição (com código de crachá) e vincula o participante às atividades.
        Administradores (staff/superuser) não recebem crachá e não participam como inscritos.
        """
        if usuario.user_django.is_staff or usuario.user_django.is_superuser:
            return None

        presentes_set = set(presentes_lista or [])
        inscricao = Inscricao.objects.create(
            usuario_id=usuario.id,
            evento=evento_obj
        )
        if atividades_lista:
            for atv in atividades_lista:
                esta_presente = atv in presentes_set
                dt_presenca = (atv.horaInicio + timedelta(minutes=10)) if esta_presente else None

                Participa.objects.create(
                    inscricao=inscricao,
                    atividade=atv,
                    funcao=StatusParticipa.PARTICIPANTE,
                    presente=esta_presente,
                    data_hora_presenca=dt_presenca,
                )
        return inscricao

    # =============================================================
    # INSCRIÇÕES DE ADMINISTRADORES
    # =============================================================
    inscrever_e_participar(usuario_admin, evento9, [atividade_ev9_2])  # Futuro -> Não iniciado
    inscrever_e_participar(usuario_admin, evento8, [atividade_ev8_2])  # Futuro -> Não iniciado

    inscricao_admin2 = inscrever_e_participar(
        usuario_admin2, evento1,
        [atividade_palestra, atividade_ev1_3],
        presentes_lista=[atividade_palestra]  # Presente na palestra, Ausente na ev1_3 (ontem)
    )
    inscrever_e_participar(usuario_admin2, evento6, [atividade_ev6_1])  # Ausente (ontem)

    inscricao_admin = inscrever_e_participar(
        usuario_admin3, evento2,
        [atividade_palestra2, atividade_ev2_2],
        presentes_lista=[atividade_palestra2]  # Presente na palestra2, Ausente na ev2_2
    )
    inscrever_e_participar(
        usuario_admin3, evento3,
        [atividade_forum, atividade_ev3_3],
        presentes_lista=[]  # Ausente em ambas
    )

    # =============================================================
    # EVENTO 1 - Semana Acadêmica de Tecnologia 2026 (Em andamento)
    # =============================================================
    # atividade_palestra: Acontecendo AGORA (mistura de Presente e Em Espera)
    # atividade_ev1_3: Ocorreu ONTEM (mistura de Presente e Ausente)
    # atividade_oficina / atividade_ev1_4: AMANHÃ / +2d (Não iniciado)
    inscricao_participante1 = inscrever_e_participar(
        usuario_participante1, evento1,
        [atividade_palestra, atividade_ev1_3, atividade_ev1_4],
        presentes_lista=[atividade_palestra, atividade_ev1_3]  # Presente em ambas
    )
    inscrever_e_participar(
        usuario_participante2, evento1,
        [atividade_palestra, atividade_oficina, atividade_ev1_3],
        presentes_lista=[atividade_oficina]  # Em Espera na palestra (agora) | Ausente na ev1_3 (ontem)
    )
    inscrever_e_participar(
        usuario_participante3, evento1,
        [atividade_palestra, atividade_ev1_3, atividade_ev1_4],
        presentes_lista=[atividade_ev1_3]  # Em Espera na palestra (agora) | Presente na ev1_3 (ontem)
    )
    inscricao_participante4 = inscrever_e_participar(
        usuario_participante4, evento1,
        [atividade_palestra, atividade_oficina, atividade_ev1_3, atividade_ev1_4],
        presentes_lista=[atividade_palestra, atividade_oficina]  # Ausente na ev1_3 (ontem)
    )
    inscricao_participante5 = inscrever_e_participar(
        usuario_participante5, evento1,
        [atividade_palestra, atividade_oficina, atividade_ev1_3],
        presentes_lista=[atividade_oficina]  # Em Espera na palestra (agora) | Ausente na ev1_3 (ontem)
    )
    inscrever_e_participar(
        usuario_participante10, evento1,
        [atividade_palestra, atividade_oficina],
        presentes_lista=[atividade_oficina]  # Em Espera na palestra (agora)
    )
    inscrever_e_participar(
        usuario_participante17, evento1,
        [atividade_palestra, atividade_ev1_4],
        presentes_lista=[]  # Em Espera na palestra (agora) | Não iniciado na ev1_4
    )
    inscrever_e_participar(
        usuario_participante8, evento1,
        [atividade_palestra, atividade_ev1_3],
        presentes_lista=[]  # Em Espera na palestra (agora) | Ausente na ev1_3 (ontem)
    )

    # =============================================================
    # EVENTO 2 - Palestra Internacional de Administração 2026 (Encerrado)
    # =============================================================
    inscricao_participante2 = inscrever_e_participar(
        usuario_participante2, evento2,
        [atividade_palestra2],
        presentes_lista=[]  # Ausente
    )
    inscricao_participante6 = inscrever_e_participar(
        usuario_participante5, evento2,
        [atividade_palestra2, atividade_ev2_2],
        presentes_lista=[]  # Ausente em ambas
    )
    inscrever_e_participar(
        usuario_participante7, evento2,
        [atividade_palestra2, atividade_ev2_2],
        presentes_lista=[atividade_palestra2, atividade_ev2_2]  # Presente em ambas
    )
    inscrever_e_participar(
        usuario_participante9, evento2,
        [atividade_palestra2, atividade_ev2_2],
        presentes_lista=[atividade_palestra2]  # Presente na palestra2 | Ausente na ev2_2
    )
    inscrever_e_participar(
        usuario_participante12, evento2,
        [atividade_palestra2, atividade_ev2_2],
        presentes_lista=[]  # Ausente em ambas
    )
    inscrever_e_participar(
        usuario_participante15, evento2,
        [atividade_palestra2],
        presentes_lista=[]  # Ausente
    )

    # =============================================================
    # EVENTO 3 - Fórum de Gestão de Projetos de Tecnologia 2026 (Encerrado)
    # =============================================================
    inscricao_participante3 = inscrever_e_participar(
        usuario_participante2, evento3,
        [atividade_forum, atividade_ev3_2],
        presentes_lista=[atividade_forum]  # Presente no fórum | Ausente na ev3_2
    )
    inscrever_e_participar(
        usuario_participante3, evento3,
        [atividade_forum, atividade_ev3_2],
        presentes_lista=[atividade_ev3_2]  # Ausente no fórum | Presente na ev3_2
    )
    inscrever_e_participar(
        usuario_participante4, evento3,
        [atividade_ev3_2, atividade_ev3_3],
        presentes_lista=[]  # Ausente em ambas
    )
    inscrever_e_participar(
        usuario_participante7, evento3,
        [atividade_forum, atividade_ev3_2, atividade_ev3_3],
        presentes_lista=[atividade_forum, atividade_ev3_2]  # Ausente na ev3_3
    )
    inscrever_e_participar(
        usuario_participante16, evento3,
        [atividade_ev3_2, atividade_ev3_3],
        presentes_lista=[]  # Ausente em ambas
    )
    inscrever_e_participar(
        usuario_participante12, evento3,
        [atividade_forum],
        presentes_lista=[]  # Ausente
    )

    # =============================================================
    # EVENTO 4 - Congresso Brasileiro de Saúde e Biotecnologia 2026 (Em andamento)
    # =============================================================
    # atividade_ev4_1: ONTEM | atividade_ev4_2: AGORA | ev4_3, ev4_4, ev4_5: AMANHÃ / +2d
    inscrever_e_participar(
        usuario_participante6, evento4,
        [atividade_ev4_1, atividade_ev4_2, atividade_ev4_3, atividade_ev4_4, atividade_ev4_5],
        presentes_lista=[atividade_ev4_1, atividade_ev4_2, atividade_ev4_3, atividade_ev4_5]
    )
    inscrever_e_participar(
        usuario_participante1, evento4,
        [atividade_ev4_1, atividade_ev4_2, atividade_ev4_4],
        presentes_lista=[atividade_ev4_1]  # Presente ontem | Em Espera agora (ev4_2) | Não iniciado (ev4_4)
    )
    inscrever_e_participar(
        usuario_participante2, evento4,
        [atividade_ev4_1, atividade_ev4_2, atividade_ev4_5],
        presentes_lista=[atividade_ev4_5]  # Ausente ontem (ev4_1) | Em Espera agora (ev4_2)
    )
    inscrever_e_participar(
        usuario_participante18, evento4,
        [atividade_ev4_1, atividade_ev4_2],
        presentes_lista=[]  # Ausente ontem (ev4_1) | Em Espera agora (ev4_2)
    )
    inscrever_e_participar(
        usuario_participante19, evento4,
        [atividade_ev4_2, atividade_ev4_5],
        presentes_lista=[]  # Em Espera agora (ev4_2) | Não iniciado (ev4_5)
    )

    # =============================================================
    # EVENTO 5 - Simpósio Sul de Energias Renováveis (0 atividades)
    # =============================================================
    inscrever_e_participar(usuario_participante11, evento5)
    inscrever_e_participar(usuario_participante14, evento5)
    inscrever_e_participar(usuario_participante20, evento5)

    # =============================================================
    # EVENTO 6 - Fórum Nacional de Direito Digital (Em andamento)
    # =============================================================
    # atividade_ev6_1: ONTEM | atividade_ev6_2: AGORA | atividade_ev6_3: AMANHÃ
    inscrever_e_participar(
        usuario_participante8, evento6,
        [atividade_ev6_1, atividade_ev6_2, atividade_ev6_3],
        presentes_lista=[atividade_ev6_1, atividade_ev6_2, atividade_ev6_3]
    )
    inscrever_e_participar(
        usuario_participante17, evento6,
        [atividade_ev6_1, atividade_ev6_2],
        presentes_lista=[atividade_ev6_1]  # Presente ontem | Em Espera agora (ev6_2)
    )
    inscrever_e_participar(
        usuario_participante19, evento6,
        [atividade_ev6_1, atividade_ev6_2],
        presentes_lista=[]  # Ausente ontem (ev6_1) | Em Espera agora (ev6_2)
    )
    inscrever_e_participar(
        usuario_participante7, evento6,
        [atividade_ev6_2, atividade_ev6_3],
        presentes_lista=[atividade_ev6_3]  # Em Espera agora (ev6_2)
    )
    inscrever_e_participar(
        usuario_participante14, evento6,
        [atividade_ev6_1, atividade_ev6_2],
        presentes_lista=[]  # Ausente ontem | Em Espera agora
    )

    # =============================================================
    # EVENTOS 7, 8, 9 e 10 - Futuros (Todos ficam como "Não iniciado")
    # =============================================================
    inscrever_e_participar(usuario_participante5, evento7, [atividade_ev7_2, atividade_ev7_3, atividade_ev7_5, atividade_ev7_6])
    inscrever_e_participar(usuario_participante14, evento7, [atividade_ev7_1, atividade_ev7_4])
    inscrever_e_participar(usuario_participante13, evento7, [atividade_ev7_1, atividade_ev7_4, atividade_ev7_6])
    inscrever_e_participar(usuario_participante16, evento7, [atividade_ev7_3])
    inscrever_e_participar(usuario_participante4, evento7, [atividade_ev7_3])

    inscrever_e_participar(usuario_participante11, evento8, [atividade_ev8_1, atividade_ev8_2])
    inscrever_e_participar(usuario_participante10, evento8, [atividade_ev8_1, atividade_ev8_2])
    inscrever_e_participar(usuario_participante20, evento8, [atividade_ev8_2])

    inscrever_e_participar(usuario_participante10, evento9, [atividade_ev9_1, atividade_ev9_2, atividade_ev9_3, atividade_ev9_4])
    inscrever_e_participar(usuario_participante1, evento9, [atividade_ev9_2])
    inscrever_e_participar(usuario_participante11, evento9, [atividade_ev9_4])

    inscrever_e_participar(usuario_participante13, evento10, [atividade_ev10_1])
    inscrever_e_participar(usuario_participante20, evento10, [atividade_ev10_1])
    inscrever_e_participar(usuario_participante15, evento10, [atividade_ev10_1])
    inscrever_e_participar(usuario_participante9, evento10)

    # -------------------------------------------------------------
    # 7. QUIZZES / DESAFIOS (0 a 3 por atividade)
    # -------------------------------------------------------------
    Quiz.objects.all().delete()

    def criar_quiz(atividade_obj, titulo, tipo, pergunta, **kwargs):
        """Cria o quiz deixando o save() do model definir o numero sequencial por atividade."""
        quiz, _ = Quiz.objects.get_or_create(
            atividade=atividade_obj,
            titulo=titulo,
            defaults={
                "tipo": tipo,
                "subtitulo": kwargs.get("subtitulo", ""),
                "pergunta": pergunta,
                "dica": kwargs.get("dica", ""),
                "unidade_medida": kwargs.get("unidade_medida", ""),
                "valor_minimo": kwargs.get("valor_minimo"),
                "valor_maximo": kwargs.get("valor_maximo"),
                "valor_ideal": kwargs.get("valor_ideal"),
                "opcao_a": kwargs.get("opcao_a"),
                "opcao_b": kwargs.get("opcao_b"),
                "opcao_c": kwargs.get("opcao_c"),
                "opcao_d": kwargs.get("opcao_d"),
                "alternativa_correta": kwargs.get("alternativa_correta"),
                "ativo": kwargs.get("ativo", True),
            }
        )
        return quiz

    # =============================================================
    # EVENTO 1 - Semana Acadêmica de Tecnologia 2026
    # =============================================================
    # Atividade 1 (atividade_palestra): 2 quizzes (Múltipla Escolha)
    q_ev1_p1 = criar_quiz(
        atividade_palestra,
        titulo="Arquitetura de Redes Neurais em Diagnóstico",
        tipo="MULTIPLA",
        subtitulo="Fundamentos de Visão Computacional Médica",
        pergunta="Qual arquitetura de Deep Learning é mais utilizada para segmentação de imagens médicas (como ressonâncias e tomografias)?",
        dica="Possui formato simétrico em 'U' com conexões de salto (skip connections).",
        opcao_a="U-Net",
        opcao_b="ARIMA",
        opcao_c="K-Means",
        opcao_d="Random Forest",
        alternativa_correta="A",
    )

    q_ev1_p2 = criar_quiz(
        atividade_palestra,
        titulo="Métrica de Avaliação em Exames Clínicos",
        tipo="MULTIPLA",
        subtitulo="Sensibilidade vs. Especificidade",
        pergunta="Em um sistema de triagem médica, qual métrica deve ser priorizada para evitar falsos negativos em doenças graves?",
        dica="Pense na capacidade do modelo de detectar todos os pacientes realmente doentes.",
        opcao_a="Acurácia global",
        opcao_b="Recall (Sensibilidade)",
        opcao_c="Tempo de inferência",
        opcao_d="Compressão de modelo",
        alternativa_correta="B",
    )

    # Atividade 2 (atividade_oficina): 3 quizzes (Métrica - seus originais + 1)
    quiz_1 = criar_quiz(
        atividade_oficina,
        titulo="Aferição de Espessura do Material",
        tipo="METRICA",
        subtitulo="Medição de precisão industrial",
        pergunta="Qual a espessura medida da amostra metálica disponibilizada na bancada 02?",
        dica="Utilize o paquímetro digital disponível no kit do laboratório.",
        unidade_medida="mm",
        valor_minimo=Decimal("10.00"),
        valor_maximo=Decimal("10.50"),
        valor_ideal=Decimal("10.25"),
    )

    quiz_2 = criar_quiz(
        atividade_oficina,
        titulo="Pesagem de Componente Químico",
        tipo="METRICA",
        subtitulo="Teste de tolerância de dosagem",
        pergunta="Informe a massa total do reagente A após o processo de secagem.",
        dica="Considere a tara do recipiente de 5 gramas.",
        unidade_medida="gramas",
        valor_minimo=Decimal("48.00"),
        valor_maximo=Decimal("52.00"),
        valor_ideal=Decimal("50.00"),
    )

    quiz_3 = criar_quiz(
        atividade_oficina,
        titulo="Tensão de Saída do Sensor Calibrado",
        tipo="METRICA",
        subtitulo="Leitura no multímetro de bancada",
        pergunta="Meça a tensão de saída (em Volts) do sensor óptico sob iluminação padrão de 500 lux.",
        dica="Aguarde 10 segundos para estabilização térmica do circuito.",
        unidade_medida="V",
        valor_minimo=Decimal("3.20"),
        valor_maximo=Decimal("3.40"),
        valor_ideal=Decimal("3.30"),
    )

    # Atividade 3 (atividade_ev1_3 - Docker/K8s): 2 quizzes
    q_ev1_3_1 = criar_quiz(
        atividade_ev1_3,
        titulo="Orquestração de Pods no Kubernetes",
        tipo="MULTIPLA",
        subtitulo="Conceitos fundamentais de cluster",
        pergunta="Qual objeto do Kubernetes garante que um número específico de réplicas de um Pod esteja sempre em execução?",
        dica="É gerenciado indiretamente pelo Deployment.",
        opcao_a="ConfigMap",
        opcao_b="Ingress",
        opcao_c="ReplicaSet",
        opcao_d="Secret",
        alternativa_correta="C",
    )

    q_ev1_3_2 = criar_quiz(
        atividade_ev1_3,
        titulo="Consumo de Memória do Container",
        tipo="METRICA",
        subtitulo="Monitoramento com docker stats",
        pergunta="Qual o pico de consumo de memória RAM (em MB) da API após o teste de carga de 1.000 requisições?",
        dica="Observe a coluna MEM USAGE no terminal.",
        unidade_medida="MB",
        valor_minimo=Decimal("140.00"),
        valor_maximo=Decimal("165.00"),
        valor_ideal=Decimal("152.00"),
    )

    # Atividade 4 (atividade_ev1_4 - Fórum Carreira): 0 quizzes (proposital)

    # =============================================================
    # EVENTO 2 - Palestra Internacional de Administração 2026 (Encerrado)
    # =============================================================
    # atividade_palestra2: 1 quiz
    q_ev2_1 = criar_quiz(
        atividade_palestra2,
        titulo="Indicadores de Governança Corporativa",
        tipo="MULTIPLA",
        subtitulo="Gestão contemporânea",
        pergunta="Qual pilar de ESG trata diretamente da transparência fiscal, ética empresarial e composição do conselho?",
        dica="Refere-se à letra 'G' da sigla.",
        opcao_a="Ambiental",
        opcao_b="Social",
        opcao_c="Governança",
        opcao_d="Operacional",
        alternativa_correta="C",
    )

    # atividade_ev2_2 (Oficina OKRs): 2 quizzes
    q_ev2_2_1 = criar_quiz(
        atividade_ev2_2,
        titulo="Estruturação de Key Results",
        tipo="MULTIPLA",
        subtitulo="Metodologia OKR",
        pergunta="Qual característica é obrigatória em um bom Resultado-Chave (Key Result)?",
        dica="Se não pode ser medido, não é um KR.",
        opcao_a="Ser subjetivo e inspiracional",
        opcao_b="Ser quantificável e mensurável",
        opcao_c="Ser definido exclusivamente pelo RH",
        opcao_d="Não possuir prazo definido",
        alternativa_correta="B",
    )

    q_ev2_2_2 = criar_quiz(
        atividade_ev2_2,
        titulo="Cálculo de Atingimento de Meta",
        tipo="METRICA",
        subtitulo="Estudo de caso Startup Alpha",
        pergunta="Com base na planilha do exercício, qual o percentual médio de atingimento dos 3 KRs do trimestre?",
        dica="Some os percentuais individuais e divida por 3.",
        unidade_medida="%",
        valor_minimo=Decimal("74.00"),
        valor_maximo=Decimal("76.00"),
        valor_ideal=Decimal("75.00"),
    )

    # =============================================================
    # EVENTO 3 - Fórum de Gestão de Projetos de Tecnologia 2026 (Encerrado)
    # =============================================================
    # atividade_forum: 0 quizzes
    # atividade_ev3_2 (Oficina Kanban): 2 quizzes
    q_ev3_2_1 = criar_quiz(
        atividade_ev3_2,
        titulo="Lei de Little na Prática",
        tipo="METRICA",
        subtitulo="Cálculo de Lead Time",
        pergunta="Se o WIP médio da equipe é de 12 itens e o Throughput é de 3 itens/dia, qual o Lead Time médio em dias?",
        dica="Fórmula: Lead Time = WIP / Throughput.",
        unidade_medida="dias",
        valor_minimo=Decimal("3.80"),
        valor_maximo=Decimal("4.20"),
        valor_ideal=Decimal("4.00"),
    )

    q_ev3_2_2 = criar_quiz(
        atividade_ev3_2,
        titulo="Limite de Trabalho em Progresso (WIP)",
        tipo="MULTIPLA",
        subtitulo="Fluxo puxado",
        pergunta="Qual é o principal objetivo de limitar o WIP em um quadro Kanban?",
        dica="Foca em terminar tarefas antes de começar novas.",
        opcao_a="Aumentar a quantidade de reuniões diárias",
        opcao_b="Evitar gargalos e reduzir o tempo de ciclo (Cycle Time)",
        opcao_c="Eliminar a necessidade de testes",
        opcao_d="Distribuir tarefas igualmente por hora",
        alternativa_correta="B",
    )

    # atividade_ev3_3: 0 quizzes

    # =============================================================
    # EVENTO 4 - Congresso Brasileiro de Saúde e Biotecnologia 2026
    # =============================================================
    # atividade_ev4_1 (CRISPR): 1 quiz
    q_ev4_1 = criar_quiz(
        atividade_ev4_1,
        titulo="Mecanismo CRISPR-Cas9",
        tipo="MULTIPLA",
        subtitulo="Biologia Molecular",
        pergunta="Qual é a função da enzima Cas9 no sistema CRISPR-Cas9?",
        dica="Atua como uma 'tesoura molecular'.",
        opcao_a="Transportar aminoácidos no ribossomo",
        opcao_b="Realizar a clivagem (corte) da dupla fita de DNA no alvo guiado",
        opcao_c="Sintetizar lipídios de membrana",
        opcao_d="Degradar proteínas mal dobradas",
        alternativa_correta="B",
    )

    # atividade_ev4_2 (Fórum Telemedicina): 0 quizzes
    # atividade_ev4_3 (Oficina Biossegurança): 3 quizzes
    q_ev4_3_1 = criar_quiz(
        atividade_ev4_3,
        titulo="Temperatura de Armazenamento de Reagentes",
        tipo="METRICA",
        subtitulo="Controle de cadeia fria",
        pergunta="Qual a temperatura interna aferida no ultrafreezer da Bancada 01 durante a inspeção?",
        dica="Valores padrão de ultrafreezeres ficam próximos a -80 °C.",
        unidade_medida="°C",
        valor_minimo=Decimal("-82.00"),
        valor_maximo=Decimal("-78.00"),
        valor_ideal=Decimal("-80.00"),
    )

    q_ev4_3_2 = criar_quiz(
        atividade_ev4_3,
        titulo="Nível de Biossegurança (NB)",
        tipo="MULTIPLA",
        subtitulo="Classificação de risco biológico",
        pergunta="Qual nível de biossegurança é exigido para manipulação de agentes com risco individual moderado e risco comunitário limitado?",
        dica="É o nível padrão da maioria dos laboratórios clínicos hospitalares.",
        opcao_a="NB-1",
        opcao_b="NB-2",
        opcao_c="NB-3",
        opcao_d="NB-4",
        alternativa_correta="B",
    )

    q_ev4_3_3 = criar_quiz(
        atividade_ev4_3,
        titulo="Tempo de Esterilização em Autoclave",
        tipo="METRICA",
        subtitulo="Protocolo padrão a 121 °C",
        pergunta="Informe o tempo mínimo (em minutos) de exposição a 121 °C para esterilização padrão de vidrarias.",
        dica="Valor clássico de referência em microbiologia.",
        unidade_medida="minutos",
        valor_minimo=Decimal("15.00"),
        valor_maximo=Decimal("20.00"),
        valor_ideal=Decimal("15.00"),
    )

    # atividade_ev4_4: 0 quizzes
    # atividade_ev4_5 (Oficina Python DataSUS): 1 quiz
    q_ev4_5_1 = criar_quiz(
        atividade_ev4_5,
        titulo="Taxa de Incidência Calculada",
        tipo="METRICA",
        subtitulo="Análise do dataset CSV fornecido",
        pergunta="Qual foi a taxa de incidência por 100 mil habitantes encontrada para a região Sul em 2025?",
        dica="Filtre pela coluna UF in ['PR', 'SC', 'RS'] no notebook.",
        unidade_medida="casos/100k",
        valor_minimo=Decimal("124.00"),
        valor_maximo=Decimal("126.00"),
        valor_ideal=Decimal("125.40"),
    )

    # =============================================================
    # EVENTO 6 - Fórum Nacional de Direito Digital e Proteção de Dados
    # =============================================================
    # atividade_ev6_1: 0 quizzes
    # atividade_ev6_2: 0 quizzes
    # atividade_ev6_3 (Oficina RIPD): 2 quizzes
    q_ev6_3_1 = criar_quiz(
        atividade_ev6_3,
        titulo="Bases Legais da LGPD",
        tipo="MULTIPLA",
        subtitulo="Artigo 7º da Lei 13.709/2018",
        pergunta="Qual base legal exige a elaboração de um Relatório de Impacto à Proteção de Dados (RIPD) quando solicitada pela ANPD?",
        dica="Base legal frequentemente usada em marketing e prevenção a fraudes, que exige teste de balanceamento.",
        opcao_a="Cumprimento de obrigação legal",
        opcao_b="Legítimo interesse do controlador",
        opcao_c="Execução de contrato",
        opcao_d="Tutela da saúde",
        alternativa_correta="B",
    )

    q_ev6_3_2 = criar_quiz(
        atividade_ev6_3,
        titulo="Prazo de Comunicação de Incidente",
        tipo="METRICA",
        subtitulo="Resolução CD/ANPD nº 15/2024",
        pergunta="Qual o prazo máximo (em dias úteis) para o controlador comunicar à ANPD um incidente de segurança relevante?",
        dica="Atualizado pela resolução recente da ANPD.",
        unidade_medida="dias úteis",
        valor_minimo=Decimal("3.00"),
        valor_maximo=Decimal("3.00"),
        valor_ideal=Decimal("3.00"),
    )

    # =============================================================
    # EVENTO 7 - Semana de Design, Arquitetura e Urbanismo (Futuro)
    # =============================================================
    # atividade_ev7_2 (FabLab): 1 quiz (sem respostas ainda, pois é futuro)
    q_ev7_2_1 = criar_quiz(
        atividade_ev7_2,
        titulo="Temperatura de Extrusão PLA",
        tipo="METRICA",
        subtitulo="Preparação de impressora 3D",
        pergunta="Qual a temperatura ideal do bico extrusor (em °C) para impressão em filamento PLA padrão?",
        dica="Consulte a etiqueta do carretel na bancada do FabLab.",
        unidade_medida="°C",
        valor_minimo=Decimal("195.00"),
        valor_maximo=Decimal("215.00"),
        valor_ideal=Decimal("205.00"),
    )

    # atividade_ev7_3 (Design Systems): 1 quiz (sem respostas ainda)
    q_ev7_3_1 = criar_quiz(
        atividade_ev7_3,
        titulo="Contraste Mínimo WCAG AA",
        tipo="METRICA",
        subtitulo="Acessibilidade visual",
        pergunta="Qual a razão de contraste mínima exigida pelo padrão WCAG 2.1 nível AA para textos normais?",
        dica="Informe apenas o primeiro número da proporção X:1.",
        unidade_medida=":1",
        valor_minimo=Decimal("4.50"),
        valor_maximo=Decimal("4.50"),
        valor_ideal=Decimal("4.50"),
    )

    # =============================================================
    # EVENTO 8 - Feira de Inovação no Agronegócio (Futuro)
    # =============================================================
    # atividade_ev8_1 (Oficina Drones NDVI): 1 quiz (sem respostas ainda)
    q_ev8_1_1 = criar_quiz(
        atividade_ev8_1,
        titulo="Interpretação do Índice NDVI",
        tipo="METRICA",
        subtitulo="Vigor vegetativo",
        pergunta="Em uma lavoura de soja saudável em pleno desenvolvimento vegetativo, qual o valor esperado de NDVI?",
        dica="Varia entre -1 e +1; vegetação densa fica próxima ao limite superior.",
        unidade_medida="NDVI",
        valor_minimo=Decimal("0.70"),
        valor_maximo=Decimal("0.90"),
        valor_ideal=Decimal("0.82"),
    )

    # =============================================================
    # EVENTO 9 e EVENTO 10 (Futuros)
    # =============================================================
    # atividade_ev9_1 (Oficina CLPs): 1 quiz (sem respostas ainda)
    q_ev9_1_1 = criar_quiz(
        atividade_ev9_1,
        titulo="Linguagem Ladder - Contato Normalmente Aberto",
        tipo="MULTIPLA",
        subtitulo="Norma IEC 61131-3",
        pergunta="Na programação em Ladder, qual símbolo representa um contato normalmente aberto (NA)?",
        dica="Não possui barra diagonal cortando o símbolo.",
        opcao_a="--| |--",
        opcao_b="--|/|--",
        opcao_c="--( )--",
        opcao_d="--(R)--",
        alternativa_correta="A",
    )
    # Demais atividades dos eventos 7, 8, 9 e 10 ficam com 0 quizzes.


    # -------------------------------------------------------------
    # 8. RESPOSTAS DOS QUIZZES
    # -------------------------------------------------------------
    Resposta.objects.all().delete()
    def registrar_resposta(usuario_obj, atividade_obj, quiz_obj, valor_resposta=None, resposta_texto=None):
        """
        Registra a resposta de um participante no quiz.
        Ignora caso o usuário seja o organizador do evento (que não possui crachá).
        """
        if usuario_obj.user_django.is_staff or usuario_obj.user_django.is_superuser:
            return None

        inscricao_obj = Inscricao.objects.filter(
            usuario_id=usuario_obj.id,
            evento=atividade_obj.evento
        ).first()

        if not inscricao_obj:
            inscricao_obj = Inscricao.objects.create(
                usuario_id=usuario_obj.id,
                evento=atividade_obj.evento
            )

        dt_presenca = atividade_obj.horaInicio + timedelta(minutes=10)
        participa_obj, created = Participa.objects.get_or_create(
            inscricao=inscricao_obj,
            atividade=atividade_obj,
            defaults={
                "funcao": StatusParticipa.PARTICIPANTE,
                "presente": True,
                "data_hora_presenca": dt_presenca,
            }
        )

        if not created:
            if not participa_obj.presente or not participa_obj.data_hora_presenca:
                participa_obj.presente = True
                participa_obj.data_hora_presenca = dt_presenca
                participa_obj.save()

        correto = False
        status = "errado"

        if quiz_obj.tipo == "METRICA" and valor_resposta is not None:
            val = Decimal(str(valor_resposta))
            if quiz_obj.valor_minimo <= val <= quiz_obj.valor_maximo:
                correto = True
                if quiz_obj.valor_ideal is not None and val == quiz_obj.valor_ideal:
                    status = "certo"
                else:
                    status = "aproximado"
        elif quiz_obj.tipo == "MULTIPLA" and resposta_texto:
            resp_limpa = resposta_texto.strip().upper()
            if resp_limpa == quiz_obj.alternativa_correta:
                correto = True
                status = "certo"

        resposta, _ = Resposta.objects.update_or_create(
            participa=participa_obj,
            quiz=quiz_obj,
            defaults={
                "valor_resposta": Decimal(str(valor_resposta)) if valor_resposta is not None else None,
                "resposta_texto": resposta_texto.strip().upper() if resposta_texto else None,
                "correto": correto,
                "completo": True,
                "status": status,
            }
        )
        return resposta

    # --- Oficina de Sensores (Joana, João e Sofia presentes; Pedro presente mas não respondeu) ---
    registrar_resposta(usuario_participante4, atividade_oficina, quiz_1, valor_resposta="10.20")  # aproximado
    registrar_resposta(usuario_participante4, atividade_oficina, quiz_2, valor_resposta="42.50")  # errado
    registrar_resposta(usuario_participante4, atividade_oficina, quiz_3, valor_resposta="3.30")   # certo

    registrar_resposta(usuario_participante2, atividade_oficina, quiz_1, valor_resposta="10.25")  # certo
    registrar_resposta(usuario_participante2, atividade_oficina, quiz_2, valor_resposta="49.80")  # aproximado
    registrar_resposta(usuario_participante2, atividade_oficina, quiz_3, valor_resposta="3.28")   # aproximado

    registrar_resposta(usuario_participante5, atividade_oficina, quiz_1, valor_resposta="11.10")  # errado
    registrar_resposta(usuario_participante5, atividade_oficina, quiz_2, valor_resposta="50.00")  # certo

    # --- Palestra de IA (Mariana, Joana e Admin2 presentes; outros 5 inscritos ficam "Em Espera") ---
    registrar_resposta(usuario_participante1, atividade_palestra, q_ev1_p1, resposta_texto="A")   # certo
    registrar_resposta(usuario_participante1, atividade_palestra, q_ev1_p2, resposta_texto="B")   # certo
    registrar_resposta(usuario_participante4, atividade_palestra, q_ev1_p1, resposta_texto="A")   # certo
    registrar_resposta(usuario_participante4, atividade_palestra, q_ev1_p2, resposta_texto="A")   # errado
    registrar_resposta(usuario_admin2, atividade_palestra, q_ev1_p1, resposta_texto="A")          # certo

    # --- Oficina Docker/K8s (Mariana e Lucas presentes; João, Joana, Sofia, Thiago e Admin2 ficam "Ausente") ---
    registrar_resposta(usuario_participante1, atividade_ev1_3, q_ev1_3_1, resposta_texto="C")     # certo
    registrar_resposta(usuario_participante1, atividade_ev1_3, q_ev1_3_2, valor_resposta="150.00")# aproximado
    registrar_resposta(usuario_participante3, atividade_ev1_3, q_ev1_3_1, resposta_texto="C")     # certo
    registrar_resposta(usuario_participante3, atividade_ev1_3, q_ev1_3_2, valor_resposta="180.00")# errado

    # --- Evento 2 Encerrado (Clara, Fernanda e Admin3 presentes; João, Sofia, Helena e Gabriel ficam "Ausente") ---
    registrar_resposta(usuario_participante7, atividade_palestra2, q_ev2_1, resposta_texto="C")   # certo
    registrar_resposta(usuario_participante9, atividade_palestra2, q_ev2_1, resposta_texto="C")   # certo
    registrar_resposta(usuario_admin3, atividade_palestra2, q_ev2_1, resposta_texto="A")          # errado

    registrar_resposta(usuario_participante7, atividade_ev2_2, q_ev2_2_1, resposta_texto="B")     # certo
    registrar_resposta(usuario_participante7, atividade_ev2_2, q_ev2_2_2, valor_resposta="75.00") # certo

    # --- Evento 3 Encerrado (Lucas e Clara presentes; João, Joana e Patrícia ficam "Ausente") ---
    registrar_resposta(usuario_participante7, atividade_ev3_2, q_ev3_2_1, valor_resposta="4.00")  # certo
    registrar_resposta(usuario_participante7, atividade_ev3_2, q_ev3_2_2, resposta_texto="B")     # certo
    registrar_resposta(usuario_participante3, atividade_ev3_2, q_ev3_2_1, valor_resposta="3.90")  # aproximado
    registrar_resposta(usuario_participante3, atividade_ev3_2, q_ev3_2_2, resposta_texto="B")     # certo

    # --- Evento 4 Em andamento (Rafael e Mariana presentes; João e Amanda ficam "Ausente" na ev4_1) ---
    registrar_resposta(usuario_participante6, atividade_ev4_1, q_ev4_1, resposta_texto="B")       # certo
    registrar_resposta(usuario_participante1, atividade_ev4_1, q_ev4_1, resposta_texto="B")       # certo

    registrar_resposta(usuario_participante6, atividade_ev4_3, q_ev4_3_1, valor_resposta="-80.00")# certo
    registrar_resposta(usuario_participante6, atividade_ev4_3, q_ev4_3_2, resposta_texto="B")     # certo
    registrar_resposta(usuario_participante6, atividade_ev4_3, q_ev4_3_3, valor_resposta="15.00") # certo

    registrar_resposta(usuario_participante6, atividade_ev4_5, q_ev4_5_1, valor_resposta="125.40")# certo
    registrar_resposta(usuario_participante2, atividade_ev4_5, q_ev4_5_1, valor_resposta="124.80")# aproximado

    # --- Evento 6 Em andamento (Thiago e Clara presentes) ---
    registrar_resposta(usuario_participante8, atividade_ev6_3, q_ev6_3_1, resposta_texto="B")     # certo
    registrar_resposta(usuario_participante8, atividade_ev6_3, q_ev6_3_2, valor_resposta="3.00")  # certo
    registrar_resposta(usuario_participante7, atividade_ev6_3, q_ev6_3_1, resposta_texto="B")     # certo
    registrar_resposta(usuario_participante7, atividade_ev6_3, q_ev6_3_2, valor_resposta="5.00")  # errado

    print("População do banco de dados concluída com sucesso!")

if __name__ == "__main__":
    popular_banco()