from django.db import models
from django.utils import timezone
import uuid

class Participante(models.Model):
    """Model para armazenar os participantes pelo crachá"""
    cracha = models.CharField(max_length=200, unique=True, verbose_name="Número do Crachá")
    nome = models.CharField(max_length=200, blank=True, null=True)
    empresa = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ultimo_acesso = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Participante"
        verbose_name_plural = "Participantes"
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome or 'Sem nome'} - {self.cracha}"
    
    def get_progresso_geral(self):
        """Retorna o progresso geral do participante"""
        quizzes_respondidos = self.respostas.filter(completo=True).count()
        total_quizzes = Quiz.objects.filter(ativo=True).count()
        return {
            'respondidos': quizzes_respondidos,
            'total': total_quizzes,
            'porcentagem': round((quizzes_respondidos / total_quizzes * 100) if total_quizzes > 0 else 0, 1)
        }

class Quiz(models.Model):
    """Model para os desafios/quiz"""
    titulo = models.CharField(max_length=200)
    subtitulo = models.CharField(max_length=300, blank=True, null=True)
    descricao = models.TextField(help_text="Descrição do desafio")
    numero = models.PositiveIntegerField(unique=True, help_text="Número do desafio")
    icone = models.CharField(max_length=50, default="bi-trophy", help_text="Classe do Bootstrap Icon")
    
    # Configurações da resposta
    pergunta = models.TextField()
    unidade_medida = models.CharField(max_length=50, help_text="Ex: mm, gramas, unidades")
    valor_minimo = models.DecimalField(max_digits=10, decimal_places=2, help_text="Valor mínimo aceitável")
    valor_maximo = models.DecimalField(max_digits=10, decimal_places=2, help_text="Valor máximo aceitável")
    valor_ideal = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Valor ideal/resposta correta")
    
    # Dicas e ajuda
    dica = models.TextField(blank=True, null=True, help_text="Dica para o participante")
    
    # Controle
    ativo = models.BooleanField(default=True, help_text="Quiz disponível para resposta")
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Quiz/Desafio"
        verbose_name_plural = "Quizzes/Desafios"
        ordering = ['numero']
    
    def __str__(self):
        return f"Desafio {self.numero}: {self.titulo}"
    
    def get_faixa_resposta(self):
        """Retorna a faixa de resposta formatada"""
        return f"{self.valor_minimo} a {self.valor_maximo} {self.unidade_medida}"

class RespostaQuiz(models.Model):
    """Model para armazenar as respostas dos participantes"""
    participante = models.ForeignKey(Participante, on_delete=models.CASCADE, related_name='respostas')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='respostas')
    
    valor_resposta = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)
    data_resposta = models.DateTimeField(auto_now_add=True)
    ultima_atualizacao = models.DateTimeField(auto_now=True)
    
    # Status
    correto = models.BooleanField(default=False)
    completo = models.BooleanField(default=False, help_text="Indica se o quiz foi completado com sucesso")
    tentativas = models.PositiveIntegerField(default=1)
    
    class Meta:
        verbose_name = "Resposta do Quiz"
        verbose_name_plural = "Respostas dos Quizzes"
        unique_together = ['participante', 'quiz']
        ordering = ['-data_resposta']
    
    def __str__(self):
        return f"{self.participante} - {self.quiz}: {self.valor_resposta}"
    
    def verificar_resposta(self):
        """Verifica se a resposta está dentro da faixa aceitável"""
        self.correto = self.quiz.valor_minimo <= self.valor_resposta <= self.quiz.valor_maximo
        if self.correto:
            self.completo = True
        self.save()
        return self.correto

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

"""Model da tabela Usuario"""
class Usuario(models.Model):
    nome = models.CharField(max_length=200)
    email = models.EmailField(max_length=200,unique=True)
    biografia = models.CharField(max_length=500, blank=True, null=True)
    fotoPerfil = models.CharField(max_length=200, blank=True, null=True)
    cpf = models.CharField(max_length=14, unique=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    dataNascimento = models.DateField(blank=True, null=True)
    cargo = models.CharField(max_length=45, blank=True, null=True)
    formacao = models.CharField(max_length=200, blank=True, null=True)
    empresa = models.CharField(max_length=45, blank=True, null=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ultimo_acesso = models.DateTimeField(auto_now=True)

"""Model da tabela Evento"""
class Evento(models.Model):
    administrador = models.ForeignKey('Usuario', on_delete=models.CASCADE)

    nome = models.CharField(max_length=200)
    descricao = models.TextField(max_length=500, blank=True, null=True)
    emailContato = models.EmailField(max_length=50, blank=True, null=True)
    apoiadores = models.TextField(max_length=200, blank=True, null=True)
    local = models.CharField(max_length=45, blank=True, null=True)
    complementoLocal = models.CharField(max_length=45, blank=True, null=True)
    imagemBanner = models.CharField(max_length=200, blank=True, null=True)

    dataInicio = models.DateField()
    dataFim = models.DateField()

    tipoEvento = models.CharField(max_length=45, blank=True, null=True)

    eventoMultiplo = models.BooleanField(default=False)
    eventoPublico = models.BooleanField(default=True)

"""Model da tabela Atividade"""
class Atividade(models.Model):
    evento = models.ForeignKey('Evento', on_delete=models.CASCADE)

    nome = models.CharField(max_length=200)
    descricao = models.TextField(max_length=500, blank=True, null=True)
    tipoAtividade = models.CharField(max_length=45, blank=True, null=True)
    horaInicio = models.DateTimeField()
    horaFim = models.DateTimeField()
    imagemBanner = models.CharField(max_length=200, blank=True, null=True)
    limitePessoas = models.PositiveIntegerField(blank=True, null=True)
    
"""Model da tabela Inscricao"""  
class Inscricao(models.Model):
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE)
    evento = models.ForeignKey('Evento', on_delete=models.CASCADE)

    dataHora = models.DateTimeField(auto_now_add=True)
    cracha = models.CharField(max_length=50, unique=True, default=uuid.uuid4)

"""Model da tabela Participa"""
class Participa(models.Model):
    inscricao = models.ForeignKey('Inscricao', on_delete=models.CASCADE)
    atividade = models.ForeignKey('Atividade', on_delete=models.CASCADE)

