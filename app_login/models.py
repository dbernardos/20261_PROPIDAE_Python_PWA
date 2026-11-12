from django.db import models
from django.utils import timezone
import uuid
from django.contrib.auth.models import User
from django.db.models import Sum, Q
from django.core.exceptions import ValidationError

# MODELS do LOGIN.
# -----------------------------------------------
def validar_tamanho_usuario(imagem):
    limite_mb = 2  # Limite de 1 MegaByte por imagem
    if imagem.size > limite_mb * 1024 * 1024:
        raise ValidationError(f"A foto de perfil não pode exceder {limite_mb}MB. Escolha um arquivo menor.")

"""Model da tabela Usuario"""
class Usuario(models.Model):
    nome = models.CharField(max_length=200)
    cpf = models.CharField(verbose_name="CPF", max_length=14, unique=True)
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
    #participante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
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
        """Quantidade total de eventos em que o usuário possui inscrição."""
        from app_evento.models import Inscricao

        return (
            Inscricao.objects.filter(usuario=self)
            .values('evento_id')
            .distinct()
            .count()
        )

    @property
    def total_atividades(self):
        """Quantidade total de atividades em que o usuário registrou participação."""
        from app_evento.models import Participa

        return (
            Participa.objects.filter(inscricao__usuario=self)
            .values('atividade_id')
            .distinct()
            .count()
        )
        
'''
class LogAcesso(models.Model):
    """Model para registrar acessos dos participantes"""
    participante = models.ForeignKey(Participante, on_delete=models.CASCADE, related_name='logs_acesso')
    data_acesso = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Log de Acesso"
        verbose_name_plural = "Logs de Acesso"
        ordering = ['-data_acesso']
'''
