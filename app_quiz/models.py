from django.db import models



# MODELS do QUIZ.
# -----------------------------------------------
class Quiz(models.Model):
    """Model para os desafios/quiz"""
    
    TIPO_CHOICES = (
        ('METRICA', 'Numérica/Métrica (Faixa de valores)'),
        ('MULTIPLA', 'Múltipla Escolha'),
    )
    
    
    atividade = models.ForeignKey('app_evento.Atividade', on_delete=models.CASCADE, blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='METRICA')
    titulo = models.CharField(max_length=200)
    numero = models.PositiveIntegerField(blank=True, null=True, editable=False)
    subtitulo = models.CharField(max_length=300, blank=True, null=True)
    
    pergunta = models.TextField()
    dica = models.TextField(blank=True, null=True, help_text="Dica para o participante")
    
    unidade_medida = models.CharField(verbose_name="Unidade de Medida", max_length=50, help_text="Ex: mm, gramas, unidades")
    valor_minimo = models.DecimalField(verbose_name="Valor Mínimo", max_digits=10, decimal_places=2, help_text="Valor mínimo aceitável", blank=True, null=True)
    valor_maximo = models.DecimalField(verbose_name="Valor Máximo", max_digits=10, decimal_places=2, help_text="Valor máximo aceitável", blank=True, null=True)
    valor_ideal = models.DecimalField(verbose_name="Valor Ideal", max_digits=10, decimal_places=2, blank=True, null=True, help_text="Valor ideal/resposta correta")

    
    #Alternativas para Múltipla Escolha
    opcao_a = models.CharField(max_length=255, blank=True, null=True)
    opcao_b = models.CharField(max_length=255, blank=True, null=True)
    opcao_c = models.CharField(max_length=255, blank=True, null=True)
    opcao_d = models.CharField(max_length=255, blank=True, null=True)
    alternativa_correta = models.CharField(
        max_length=1, 
        choices=[('A','A'), ('B','B'), ('C','C'), ('D','D')], 
        blank=True, null=True
    )
    
    ## CORRIGIR FALTA DE INTEGRIDADE NAS ATIVIDADES (remover blank=True, null=True)
   
    data_criacao = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(verbose_name="Quiz Ativo", default=True, help_text="Quiz disponível para resposta")
    
    class Meta:
        verbose_name = "Quiz/Desafio"
        verbose_name_plural = "Quizzes/Desafios"
        unique_together = ('atividade', 'numero')
        ordering = ['atividade', 'numero']
    
    def __str__(self):
        return f"Desafio {self.numero}: {self.titulo}"
    
    def get_faixa_resposta(self):
        """Retorna a faixa de resposta formatada"""
        return f"{self.valor_minimo} a {self.valor_maximo} {self.unidade_medida}"

    def save(self, *args, **kwargs):
        # Faz a verificação ee é um Quiz novo e não tem número definido
        if not self.pk and not self.numero:
            # Pega o último número cadastrado NESTA atividade
            ultimo_quiz = Quiz.objects.filter(atividade=self.atividade).order_by('-numero').first()
            if ultimo_quiz and ultimo_quiz.numero:
                self.numero = ultimo_quiz.numero + 1
            else:
                self.numero = 1 
                
        super().save(*args, **kwargs)
    
"""Model da tabela Resposta"""
class Resposta(models.Model):
    
    STATUS_CHOICES = (
        ('certo', ' Correta'),
        ('aproximado', 'Aproximado (Na faixa)'),
        ('errado', 'Errado'),
    )
    
    participa = models.ForeignKey("app_evento.Participa", on_delete=models.CASCADE, related_name='respostas')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='respostas')
    
    valor_resposta = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)
    resposta_texto = models.CharField(max_length=2, blank=True, null=True, help_text="Letra escolhida na múltipla escolha")
    
    data_resposta = models.DateTimeField(auto_now_add=True)
    correto = models.BooleanField(default=False)
    completo = models.BooleanField(default=False, help_text="Indica se o quiz foi completado com sucesso")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='errado')
    class Meta:
        verbose_name = "Resposta do Quiz"
        verbose_name_plural = "Respostas dos Quizzes"
        unique_together = ['participa', 'quiz']
        ordering = ['-data_resposta']
    
    def __str__(self):
        return f"Resposta de {self.participa} para {self.quiz}"
    
    def verificar_resposta(self):
        """Verifica se a resposta está dentro da faixa aceitável"""
        self.completo = self.quiz.valor_minimo <= self.valor_resposta <= self.quiz.valor_maximo
        self.save()
        return self.correto

    @property
    def pontos_conquistados(self):
        """Retorna o bônus de acerto baseado na precisão da resposta (entre 20 e 50 pts)"""
        if not self.correto:
            return 0
            
        quiz = self.quiz
        # Se for Múltipla Escolha: valor fixo por acerto (ex: 30 pts)
        if quiz.tipo == 'MULTIPLA_ESCOLHA':
            return 30
            
        # Se for Métrica: calcula proporcionalmente a proximidade do valor_ideal
        if quiz.tipo == 'METRICA' and quiz.valor_ideal and self.valor_resposta is not None:
            diferenca = abs(self.valor_resposta - quiz.valor_ideal)
            tolerancia_max = max(abs(quiz.valor_maximo - quiz.valor_ideal), abs(quiz.valor_ideal - quiz.valor_minimo))
            
            if tolerancia_max == 0 or diferenca == 0:
                return 50  # Acerto exato perfeito = 50 pts
                
            # Interpolação linear de pontuação: 50 pts (exato) caindo até 20 pts (na borda da tolerância)
            proporcao_erro = diferenca / tolerancia_max
            bonus = 50 - (proporcao_erro * 30)
            return max(20, int(bonus))
            
        return 20  # Padrão básico para acerto