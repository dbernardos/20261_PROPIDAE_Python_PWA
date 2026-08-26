from django.db import models
from django.utils import timezone
import uuid
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model


# Create your QUIZ models here.
# -----------------------------------------------
class Quiz(models.Model):
    """Model para os desafios/quiz"""
    ## CORRIGIR FALTA DE INTEGRIDADE NAS ATIVIDADES (remover blank=True, null=True)
    atividade = models.ForeignKey('app_evento.Atividade', on_delete=models.CASCADE, blank=True, null=True)
    titulo = models.CharField(max_length=200)
    numero = models.PositiveIntegerField(unique=True, help_text="Número do desafio")
    subtitulo = models.CharField(max_length=300, blank=True, null=True)
    #descricao = models.TextField(help_text="Descrição do desafio")
    
    # Configurações da resposta
    pergunta = models.TextField()
    dica = models.TextField(blank=True, null=True, help_text="Dica para o participante")
    unidade_medida = models.CharField(verbose_name="Unidade de Medida", max_length=50, help_text="Ex: mm, gramas, unidades")
    valor_minimo = models.DecimalField(verbose_name="Valor Mínimo", max_digits=10, decimal_places=2, help_text="Valor mínimo aceitável")
    valor_maximo = models.DecimalField(verbose_name="Valor Máximo", max_digits=10, decimal_places=2, help_text="Valor máximo aceitável")
    valor_ideal = models.DecimalField(verbose_name="Valor Ideal", max_digits=10, decimal_places=2, blank=True, null=True, help_text="Valor ideal/resposta correta")
    icone = models.CharField(max_length=50, default="bi-trophy", help_text="Classe do Bootstrap Icon")

    # Controle
    data_criacao = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True, help_text="Quiz disponível para resposta")
    
    class Meta:
        verbose_name = "Quiz/Desafio"
        verbose_name_plural = "Quizzes/Desafios"
        ordering = ['numero']
    
    def __str__(self):
        return f"Desafio {self.numero}: {self.titulo}"
    
    def get_faixa_resposta(self):
        """Retorna a faixa de resposta formatada"""
        return f"{self.valor_minimo} a {self.valor_maximo} {self.unidade_medida}"

"""Model da tabela Resposta"""
class Resposta(models.Model):
    """Model para armazenar as respostas dos participantes"""
    participa = models.ForeignKey("app_evento.Participa", on_delete=models.CASCADE, related_name='respostas')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='respostas')
    
    valor_resposta = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)
    data_resposta = models.DateTimeField(auto_now_add=True)
    correto = models.BooleanField(default=False)
    #completo = models.BooleanField(default=False, help_text="Indica se o quiz foi completado com sucesso")
    #tentativas = models.PositiveIntegerField(default=1)
    
    class Meta:
        verbose_name = "Resposta do Quiz"
        verbose_name_plural = "Respostas dos Quizzes"
        unique_together = ['participa', 'quiz']
        ordering = ['-data_resposta']
    
    def __str__(self):
        #return f"{self.participa} - {self.quiz}: {self.valor_resposta}"
        return f"Resposta de {self.participa} para {self.quiz}"
    
    def verificar_resposta(self):
        """Verifica se a resposta está dentro da faixa aceitável"""
        self.correto = self.quiz.valor_minimo <= self.valor_resposta <= self.quiz.valor_maximo
        if self.correto:
            self.completo = True
        self.save()
        return self.correto


def calcular_progresso_geral(participante):
    """
    Calcula o progresso geral de um participante nos quizzes.
    Retorna um dicionário com: total, respondidos, porcentagem.
    """
    Usuario = get_user_model()
    
    # Total de quizzes ativos
    total = Quiz.objects.filter(ativo=True).count()
    
    # Quizzes que o participante já completou (Resposta.completo = True)
    respondidos = Resposta.objects.filter(
        participante=participante,
        quiz__ativo=True,
        completo=True
    ).count()
    
    # Evita divisão por zero
    porcentagem = round((respondidos / total) * 100, 2) if total > 0 else 0
    
    return {
        'total': total,
        'respondidos': respondidos,
        'porcentagem': porcentagem,
    }