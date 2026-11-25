from django.db import models
from django.utils import timezone
import uuid
from django.contrib.auth.models import User
from django.db.models import Sum, Q
from django.core.exceptions import ValidationError

# MODELS do LOGIN.
# -----------------------------------------------

def validar_tamanho_usuario(imagem):
    limite_mb = 2  # Limite de 2 MegaByte por imagem
    if imagem.size > limite_mb * 1024 * 1024:
        raise ValidationError(f"A foto de perfil não pode exceder {limite_mb}MB. Escolha um arquivo menor.")

"""Model da tabela Usuario"""
class Usuario(models.Model):
    nome = models.CharField(max_length=200)
    cpf = models.CharField(verbose_name="CPF", max_length=14, unique=True, blank=True, null=True)
    dataNascimento = models.DateField(verbose_name="Data de Nascimento", blank=True, null=True)
    email = models.EmailField(max_length=200,unique=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    
    formacao = models.CharField(max_length=200, blank=True, null=True)
    empresa = models.CharField(max_length=45, blank=True, null=True)
    cargo = models.CharField(max_length=45, blank=True, null=True)
    fotoPerfil = models.ImageField(verbose_name="Foto de Perfil", upload_to='perfis/', validators=[validar_tamanho_usuario], blank=True, null=True)
    biografia = models.CharField(max_length=500, blank=True, null=True)

    data_cadastro = models.DateTimeField(auto_now_add=True)
    ultimo_acesso = models.DateTimeField(auto_now=True)
    user_django = models.OneToOneField(User, on_delete=models.CASCADE, related_name='participante')
    
    def __str__(self):
        return self.nome 

    @property
    def pontos_totais(self):
        """Soma todos os pontos conquistados pelo usuário em quizzes concluídos."""
        if not hasattr(self, '_cache_pontos_totais'):
            from app_quiz.models import Resposta

            respostas = Resposta.objects.filter(
                participa__inscricao__usuario=self,
                completo=True,
            ).select_related('quiz')

            self._cache_pontos_totais = sum(
                (getattr(r, 'pontos_conquistados', 0) or 0) for r in respostas
            )
        return self._cache_pontos_totais

    @property
    def nivel(self):
        """Calcula o nível inteiro a partir da pontuação total (100 pts por nível, iniciando no 1)."""
        pontos = max(0, self.pontos_totais)
        return (pontos // 100) + 1

    @property
    def nivel_progresso(self):
        """Percentual de progresso (0 a 100) para alcançar o próximo nível."""
        pontos = max(0, self.pontos_totais)
        return round(((pontos % 100) / 100) * 100)

    @property
    def total_eventos_participados(self):
        """Quantidade de eventos distintos em que o usuário teve ao menos uma presença registrada."""
        from app_evento.models import Participa

        return (
            Participa.objects.filter(
                Q(presente=True) | Q(data_hora_presenca__isnull=False),
                inscricao__usuario=self,
                inscricao__ativa=True,
            )
            .values('inscricao__evento_id')
            .distinct()
            .count()
        )

    @property
    def total_atividades(self):
        """Quantidade de atividades distintas em que o usuário registrou presença."""
        from app_evento.models import Participa

        return (
            Participa.objects.filter(
                Q(presente=True) | Q(data_hora_presenca__isnull=False),
                inscricao__usuario=self,
                inscricao__ativa=True,
            )
            .values('atividade_id')
            .distinct()
            .count()
        )
        