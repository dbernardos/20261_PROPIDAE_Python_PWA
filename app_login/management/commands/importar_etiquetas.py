import csv
import os
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from app_login.models import Usuario
from app_evento.models import Evento, Inscricao, Atividade, Participa

class Command(BaseCommand):
    help = 'Importa usuários do arquivo etiquetas.csv e cria inscrições e participações.'

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str, help='Caminho para o arquivo CSV')
        parser.add_argument('--evento-id', type=int, default=12, help='ID do Evento (padrão: 12)')
        parser.add_argument('--atividade-id', type=int, default=33, help='ID da Atividade (padrão: 33)')

    def handle(self, *args, **kwargs):
        csv_path = kwargs['csv_path']
        evento_id = kwargs['evento_id']
        atividade_id = kwargs['atividade_id']

        if not os.path.exists(csv_path):
            raise CommandError(f'Arquivo não encontrado: {csv_path}')

        # 1. Validações iniciais de Evento e Atividade
        try:
            evento = Evento.objects.get(id=evento_id)
        except Evento.DoesNotExist:
            raise CommandError(f'Evento com ID {evento_id} não encontrado.')

        try:
            atividade = Atividade.objects.get(id=atividade_id)
        except Atividade.DoesNotExist:
            raise CommandError(f'Atividade com ID {atividade_id} não encontrada.')

        # O model Participa exige que a atividade pertença ao evento da inscrição
        if atividade.evento_id != evento.id:
            raise CommandError(f'A atividade {atividade_id} não pertence ao evento {evento_id}.')

        created_users = 0
        created_inscricoes = 0
        created_participacoes = 0
        skipped = 0

        # 2. Leitura e Processamento do CSV
        with open(csv_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                id_csv = row.get('ID', '').strip()
                nome = row.get('NOME', '').strip()
                empresa = row.get('EMPRESA', '').strip()

                # Pula linhas sem ID ou Nome (como as últimas linhas do seu CSV)
                if not id_csv or not nome:
                    self.stdout.write(self.style.WARNING(f'Linha pulada (ID ou Nome vazios): {row}'))
                    skipped += 1
                    continue

                # O campo cracha tem max_length=8
                cracha = id_csv[:8] 
                # O campo empresa tem max_length=45 no seu model
                empresa_truncada = empresa[:45] if empresa else ''

                username = f"{cracha}"
                
                # A. Criar User do Django (Autenticação)
                user_django, user_created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'first_name': nome.split()[0] if nome.split() else '', 
                        'last_name': ' '.join(nome.split()[1:]) if len(nome.split()) > 1 else '',
                        'password': '12345678p'
                    }
                )

                # B. Criar Usuario (app_login)
                usuario, usu_created = Usuario.objects.get_or_create(
                    user_django=user_django,
                    defaults={'nome': nome, 'empresa': empresa_truncada}
                )
                if usu_created:
                    created_users += 1

                # C. Criar Inscrição (app_evento)
                # O save() do seu model já detecta o 'cracha' e gera o QR Code automaticamente!
                inscricao, insc_created = Inscricao.objects.get_or_create(
                    usuario=usuario,
                    evento=evento,
                    defaults={'cracha': cracha}
                )
                if insc_created:
                    created_inscricoes += 1

                # D. Criar Participação (app_evento)
                participa, part_created = Participa.objects.get_or_create(
                    inscricao=inscricao,
                    atividade=atividade,
                )
                if part_created:
                    created_participacoes += 1

        # 3. Relatório Final
        self.stdout.write(self.style.SUCCESS(
            f'\nImportação concluída com sucesso!\n'
            f'-> Usuários criados: {created_users}\n'
            f'-> Inscrições criadas: {created_inscricoes}\n'
            f'-> Participações criadas: {created_participacoes}\n'
            f'-> Linhas puladas (dados incompletos): {skipped}'
        ))