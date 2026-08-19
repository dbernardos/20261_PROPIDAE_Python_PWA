from django.db import models
from django.utils import timezone
import uuid
import uuid6
from django.contrib.auth.models import User
from smart_selects.db_fields import ChainedForeignKey #Para encadeamento de campos
from django.core.exceptions import ValidationError # ValidationError para validação de campos no backend
from django.conf import settings

# Create your EVENTO models here.
# -----------------------------------------------


class Apoiador(models.Model):
    nome = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name = "Apoiador"
        verbose_name_plural = "Apoiadores"

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
    administrador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='eventos',)

    nome = models.CharField(max_length=200)
    descricao = models.TextField(max_length=500, blank=True, null=True)
    emailContato = models.EmailField(verbose_name="Email de Contato", max_length=50, blank=True, null=True)
    apoiadores = models.ManyToManyField(Apoiador, related_name='eventos')
    local = models.CharField(max_length=45, blank=True, null=True)
    imagemBanner = models.ImageField(verbose_name="Banner", upload_to='banners/', blank=True, null=True)

    dataInicio = models.DateField(verbose_name="Data de Início")
    dataFim = models.DateField(verbose_name="Data de Término")

    tipoEvento = models.CharField(verbose_name="Tipo de Evento", choices=tipoEvento.choices, max_length=20, default=tipoEvento.SEMANA)

    eventoMultiplo = models.BooleanField(default=False)
    eventoPublico = models.BooleanField(default=True)

    def __str__(self):
        return self.nome
    

"""Model da tabela Inscricao"""  

def gerar_codigo_cracha():
    return str(uuid6.uuid7())
class Inscricao(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    evento = models.ForeignKey('Evento', on_delete=models.CASCADE)

    dataHora = models.DateTimeField(auto_now_add=True)
    cracha = models.CharField(max_length=50, unique=True, default=gerar_codigo_cracha)
    
    class Meta:
        verbose_name = "Inscrição"
        verbose_name_plural = "Inscrições"
    
    def __str__(self):
        nome_usuario = self.usuario.nome if hasattr(self.usuario, 'nome') else str(self.usuario)
        return f"{nome_usuario} - {self.evento.nome}"
        

class StatusParticipa(models.TextChoices):
    PARTICIPANTE = 'Participante', 'Participante'
    PALESTRANTE = 'Palestrante', 'Palestrante'
    ORGANIZADOR = 'Organizador', 'Organizador'

class Participa(models.Model):
    """Model para armazenar os participantes pelo crachá"""
    inscricao = models.ForeignKey('Inscricao', on_delete=models.CASCADE)
    
    atividade = ChainedForeignKey(
        'Atividade',
        chained_field='inscricao',  # Campo da classe local que dispara o filtro
        chained_model_field='evento__inscricao',  # Busca as atividades do evento relacionado à inscrição
        show_all=False,  # Não exibe atividades antes de escolher a inscrição
        auto_choose=False,  # Se só houver 1 atividade no evento, seleciona automaticamente
        sort=True,
        on_delete=models.CASCADE,
    )
    
    
    #atividade = models.ForeignKey('Atividade', on_delete=models.CASCADE)
    funcao = models.CharField('Funcao', choices=StatusParticipa.choices, max_length=20, default=StatusParticipa.PARTICIPANTE)
    
    data_hora = models.DateTimeField(auto_now_add=True)
    data_hora_presenca = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Participa"
        verbose_name_plural = "Participam"
        ordering = ['funcao']
    
    
    def clean(self):
        """Garantia no Backend: Impede salvamento de atividade incompatível com o evento"""
        super().clean()
        if self.inscricao_id and self.atividade_id:
            if self.atividade.evento != self.inscricao.evento:
                raise ValidationError({
                    'atividade': (
                        'A atividade selecionada não pertence ao evento'
                        ' desta inscrição.'
                    )
                })

    def save(self, *args, **kwargs):
        self.full_clean()  # Força o disparo da validação clean() antes de salvar
        super().save(*args, **kwargs)
       
    
    def __str__(self):
        #return f"{self.funcao or 'Sem funcao'} - {self.data_hora}"
        return f"{self.inscricao} ; {self.atividade} ; {self.funcao}"

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
    descricao = models.TextField(verbose_name="Descrição", max_length=500, blank=True, null=True)
    tipoAtividade = models.CharField(verbose_name="Tipo de Atividade", choices=tipoAtividade.choices, max_length=20, default=tipoAtividade.PALESTRA)
    complementoLocal = models.CharField(verbose_name="Complemento do Local", max_length=45, blank=True, null=True)
    horaInicio = models.DateTimeField(verbose_name="Hora de Início")
    horaFim = models.DateTimeField(verbose_name="Hora de Término")
    limitePessoas = models.PositiveIntegerField(verbose_name="Limite de Pessoas", blank=True, null=True)
    

    
    def __str__(self):
        return self.nome + " - " + self.evento.nome