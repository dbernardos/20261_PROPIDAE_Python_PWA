from django.db import models
from django.utils import timezone
import uuid
from django.contrib.auth.models import User

# Create your EVENTO models here.
# -----------------------------------------------


class Apoiador(models.Model):
    nome = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.nome

class tipoEvento(models.TextChoices):   
    COLOQUIO = 'Coloquio', 'Colóquio'
    FORUM = 'Forum', 'Fórum'
    SIMPOSIO = 'Simposio', 'Simpósio'
    SEMANA = 'SemanaAcademica', 'Semana Acadêmica'
    ENCONTRO = 'Encontro', 'Encontro'
    CONGRESSO = 'Congresso', 'Congresso'

"""Model da tabela Evento"""
class Evento(models.Model):
    #administrador = models.ForeignKey('Usuario', on_delete=models.CASCADE)
    administrador = models.ForeignKey(User, on_delete=models.CASCADE)

    nome = models.CharField(max_length=200)
    descricao = models.TextField(max_length=500, blank=True, null=True)
    emailContato = models.EmailField(max_length=50, blank=True, null=True)
    #apoiadores = models.TextField(max_length=200, blank=True, null=True)
    apoiadores = models.ManyToManyField(Apoiador, related_name='eventos')
    local = models.CharField(max_length=45, blank=True, null=True)
    imagemBanner = models.ImageField(upload_to='banners/', blank=True, null=True)

    dataInicio = models.DateField()
    dataFim = models.DateField()

    #tipoEvento = models.CharField(max_length=45, blank=True, null=True)
    tipoEvento = models.CharField('tipoEvento', choices=tipoEvento.choices, max_length=20, default=tipoEvento.SEMANA)

    eventoMultiplo = models.BooleanField(default=False)
    eventoPublico = models.BooleanField(default=True)
    
    #apoiadores = models.ManyToManyField(Apoiador, related_name='eventos')
    
    def __str__(self):
        return self.nome
    

"""Model da tabela Inscricao"""  
class Inscricao(models.Model):
    usuario = models.ForeignKey('app_login.Usuario', on_delete=models.CASCADE)
    evento = models.ForeignKey('Evento', on_delete=models.CASCADE)

    dataHora = models.DateTimeField(auto_now_add=True)
    cracha = models.CharField(max_length=50, unique=True, default=uuid.uuid4)

class StatusParticipa(models.TextChoices):
    PARTICIPANTE = 'Participante', 'Participante'
    PALESTRANTE = 'Palestrante', 'Palestrante'
    ORGANIZADOR = 'Organizador', 'Organizador'

class Participa(models.Model):
    """Model para armazenar os participantes pelo crachá"""
    inscricao = models.ForeignKey('Inscricao', on_delete=models.CASCADE)
    atividade = models.ForeignKey('Atividade', on_delete=models.CASCADE)
    funcao = models.CharField('Funcao', choices=StatusParticipa.choices, max_length=20, default=StatusParticipa.PARTICIPANTE)
    
    data_hora = models.DateTimeField(auto_now_add=True)
    data_hora_presenca = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Participa"
        verbose_name_plural = "Participam"
        ordering = ['funcao']
    
    def __str__(self):
        return f"{self.funcao or 'Sem funcao'} - {self.data_hora}"
    

"""Model da tabela Atividade"""
class tipoAtividade(models.TextChoices):
    COLOQUIO = 'Coloquio', 'Colóquio'
    FORUM = 'Forum', 'Fórum'
    PALESTRA = 'Palestra', 'Palestra'
    OFICINA = 'Oficina', 'Oficina'
    MESA_REDONDA = 'Mesa Redonda', 'Mesa Redonda'
    PAINEL = 'Painel', 'Painel'
    MINICURSO = 'Minicurso', 'Minicurso'
    MEETUP = 'Meetup', 'Meetup'
    MASTERCLASS = 'Masterclass', 'Masterclass'
    DEMODAY = 'DemoDay', 'Demo Day'
    OUTRO = 'Outro', 'Outro'

class Atividade(models.Model):
    evento = models.ForeignKey('Evento', on_delete=models.CASCADE)

    nome = models.CharField(max_length=200)
    descricao = models.TextField(max_length=500, blank=True, null=True)
    #tipoAtividade = models.CharField(max_length=45, blank=True, null=True)
    tipoAtividade = models.CharField('tipoAtividade', choices=tipoAtividade.choices, max_length=20, default=tipoAtividade.PALESTRA)
    complementoLocal = models.CharField(max_length=45, blank=True, null=True)
    horaInicio = models.DateTimeField()
    horaFim = models.DateTimeField()
    #imagemBanner = models.CharField(max_length=200, blank=True, null=True)
    limitePessoas = models.PositiveIntegerField(blank=True, null=True)
