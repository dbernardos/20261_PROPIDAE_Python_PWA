from django.db import models


class Quiz(models.Model):
    TIPO_CHOICES = (
        ('METRICA', 'Numérica/Métrica (Faixa de valores)'),
        ('MULTIPLA', 'Múltipla Escolha'),
    )
    OPCOES_CHOICES = [('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')]

    atividade = models.ForeignKey('app_evento.Atividade', on_delete=models.CASCADE, blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='METRICA')
    titulo = models.CharField(max_length=200, blank=True, null=True)
    numero = models.PositiveIntegerField(blank=True, null=True, editable=False)
    subtitulo = models.CharField(max_length=300, blank=True, null=True)
    pergunta = models.TextField(max_length=300, blank=True, null=True)
    dica = models.TextField(max_length=300, blank=True, null=True, help_text="Dica para o participante")

    # Campos numéricos
    unidade_medida = models.CharField( "Unidade de Medida", max_length=50, blank=True, default='', help_text="Ex: mm, gramas, unidades")
    valor_minimo = models.DecimalField("Valor Mínimo", max_digits=10, decimal_places=2, blank=True, null=True)
    valor_maximo = models.DecimalField("Valor Máximo", max_digits=10, decimal_places=2, blank=True, null=True)
    valor_ideal = models.DecimalField("Valor Ideal", max_digits=10, decimal_places=2, blank=True, null=True)

    # Campos de múltipla escolha
    opcao_a = models.CharField(max_length=255, blank=True, null=True)
    opcao_b = models.CharField(max_length=255, blank=True, null=True)
    opcao_c = models.CharField(max_length=255, blank=True, null=True)
    opcao_d = models.CharField(max_length=255, blank=True, null=True)
    alternativa_correta = models.CharField(max_length=1, choices=OPCOES_CHOICES, blank=True, null=True)

    #Info
    data_criacao = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField("Quiz Ativo", default=True)

    class Meta:
        verbose_name = "Quiz/Desafio"
        verbose_name_plural = "Quizzes/Desafios"
        unique_together = ('atividade', 'numero')
        ordering = ['atividade', 'numero']

    def __str__(self):
        return f"Desafio {self.numero}: {self.titulo}"

    def save(self, *args, **kwargs):
        if not self.pk and not self.numero:
            ultimo = Quiz.objects.filter(atividade=self.atividade).aggregate(
                max_num=models.Max('numero')
            )['max_num'] or 0
            self.numero = ultimo + 1
        super().save(*args, **kwargs)


class Resposta(models.Model):
    STATUS_CHOICES = (
        ('certo', 'Correta'),
        ('aproximado', 'Aproximado (Na faixa)'),
        ('errado', 'Errado'),
    )

    participa = models.ForeignKey("app_evento.Participa", on_delete=models.CASCADE, related_name='respostas')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='respostas')
    valor_resposta = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)
    resposta_texto = models.CharField(max_length=2, blank=True, null=True)
    data_resposta = models.DateTimeField(auto_now_add=True)
    correto = models.BooleanField(default=False)
    completo = models.BooleanField(default=False)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='errado')

    class Meta:
        verbose_name = "Resposta do Quiz"
        verbose_name_plural = "Respostas dos Quizzes"
        unique_together = ['participa', 'quiz']
        ordering = ['-data_resposta']

    def __str__(self):
        return f"Resposta de {self.participa} para {self.quiz}"

    def avaliar(self):
        """Centraliza a regra de correção para ambos os tipos de quiz."""
        if self.quiz.tipo == 'MULTIPLA':
            self.correto = self.resposta_texto == self.quiz.alternativa_correta
            self.status = 'certo' if self.correto else 'errado'
        else:
            val, vmin, vmax = self.valor_resposta, self.quiz.valor_minimo, self.quiz.valor_maximo
            na_faixa = val is not None and vmin is not None and vmax is not None and vmin <= val <= vmax
            self.correto = na_faixa
            if na_faixa:
                self.status = 'certo' if (self.quiz.valor_ideal is not None and val == self.quiz.valor_ideal) else 'aproximado'
            else:
                self.status = 'errado'
        self.completo = True

    @property
    def pontos_conquistados(self):
        if not self.correto:
            return 0
        if self.quiz.tipo == 'MULTIPLA':
            return 30

        q = self.quiz
        if None not in (q.valor_ideal, q.valor_minimo, q.valor_maximo, self.valor_resposta):
            diferenca = abs(float(self.valor_resposta) - float(q.valor_ideal))
            tolerancia = max(
                abs(float(q.valor_maximo) - float(q.valor_ideal)),
                abs(float(q.valor_ideal) - float(q.valor_minimo)),
            )
            if tolerancia == 0 or diferenca == 0:
                return 50
            proporcao_erro = min(1.0, diferenca / tolerancia)
            return max(20, round(50 - (proporcao_erro * 30)))

        return 20
    
    
    
    
    