from io import BytesIO
import qrcode

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone
from django.utils.timezone import localtime
from nanoid import generate
from smart_selects.db_fields import ChainedForeignKey


# MODELS do EVENTO.
# -----------------------------------------------

def gerar_codigo():
    alfabeto = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
    parte1 = generate(alfabeto, size=3)
    parte2 = generate(alfabeto, size=3)
    return f"{parte1}-{parte2}"


def gerar_codigo_unico(model_cls, field_name):
    """Garante unicidade do código gerado antes de persistir."""
    codigo = gerar_codigo()
    while model_cls.objects.filter(**{field_name: codigo}).exists():
        codigo = gerar_codigo()
    return codigo


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
    FEIRA = 'Feira', 'Feira'
    OUTRO = 'Outro', 'Outro'


def validar_tamanho_banner(imagem):
    limite_mb = 4  # Limite de 4 MegaBytes por imagem
    if imagem.size > limite_mb * 1024 * 1024:
        raise ValidationError(
            f"O banner não pode exceder {limite_mb}MB. Escolha um arquivo menor."
        )


class Evento(models.Model):
    administrador = models.ForeignKey(
        'app_login.Usuario',
        on_delete=models.CASCADE,
        related_name='administrador',
    )
    nome = models.CharField(max_length=200)
    descricao = models.TextField(max_length=500, blank=True, null=True)
    emailContato = models.EmailField(
        verbose_name="Email de Contato",
        max_length=254,
        blank=True,
        null=True,
    )
    apoiadores = models.ManyToManyField(
        Apoiador,
        related_name='apoiadores',
        blank=True,
    )
    local = models.CharField(max_length=255, blank=True, null=True)
    imagemBanner = models.ImageField(
        verbose_name="Banner",
        upload_to='banners/',
        validators=[validar_tamanho_banner],
        blank=True,
        null=True,
    )

    dataInicio = models.DateField(verbose_name="Data de Início")
    dataFim = models.DateField(verbose_name="Data de Término")

    tipoEvento = models.CharField(
        verbose_name="Tipo de Evento",
        choices=tipoEvento.choices,
        max_length=20,
        default=tipoEvento.SEMANA,
    )

    codigo_evento = models.CharField(
        max_length=7,
        unique=True,
        default=gerar_codigo,
        editable=False,
    )

    def save(self, *args, **kwargs):
        if not self.codigo_evento:
            self.codigo_evento = gerar_codigo_unico(Evento, 'codigo_evento')
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if self.dataInicio and self.dataFim and self.dataFim < self.dataInicio:
            raise ValidationError({
                'dataFim': 'A data de término não pode ser anterior à data de início.'
            })

    def __str__(self):
        return self.nome


# -----------------------------------------------
# MODELS DE INSCRIÇÃO E PARTICIPAÇÃO
# -----------------------------------------------

class Inscricao(models.Model):
    usuario = models.ForeignKey(
        'app_login.Usuario',
        on_delete=models.CASCADE,
        related_name='usuario',
    )
    evento = models.ForeignKey('Evento', on_delete=models.CASCADE)

    dataHora = models.DateTimeField(auto_now_add=True)
    cracha = models.CharField(
        max_length=7,
        unique=True,
        default=gerar_codigo,
        editable=False,
    )
    qrcode_imagem = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    ativa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Inscrição"
        verbose_name_plural = "Inscrições"
        constraints = [
            models.UniqueConstraint(
                fields=['usuario', 'evento'],
                name='unique_inscricao_usuario_evento',
            )
        ]

    def save(self, *args, **kwargs):
        if not self.cracha:
            self.cracha = gerar_codigo_unico(Inscricao, 'cracha')

        if self.ativa:
            if self.qrcode_imagem and self.qrcode_imagem.name:
                if not self.qrcode_imagem.storage.exists(self.qrcode_imagem.name):
                    self.qrcode_imagem = None

            if not self.qrcode_imagem and self.cracha:
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(self.cracha)
                qr.make(fit=True)

                img = qr.make_image(fill_color="black", back_color="white")
                buffer = BytesIO()
                img.save(buffer, format='PNG')
                buffer.seek(0)

                nome_arquivo = f'qrcode_{self.cracha}.png'
                self.qrcode_imagem.save(
                    nome_arquivo,
                    ContentFile(buffer.read()),
                    save=False,
                )

        super().save(*args, **kwargs)

    def __str__(self):
        nome_usuario = getattr(self.usuario, 'nome', str(self.usuario))
        return f"{nome_usuario} - {self.evento.nome}"


class StatusParticipa(models.TextChoices):
    PARTICIPANTE = 'Participante', 'Participante'
    ORGANIZADOR = 'Organizador', 'Organizador'


class Participa(models.Model):
    inscricao = models.ForeignKey('Inscricao', on_delete=models.CASCADE)
    atividade = ChainedForeignKey(
        'Atividade',
        chained_field='inscricao',
        chained_model_field='evento__inscricao',
        show_all=False,
        auto_choose=False,
        sort=True,
        on_delete=models.CASCADE,
    )
    funcao = models.CharField(
        'Funcao',
        choices=StatusParticipa.choices,
        max_length=20,
        default=StatusParticipa.PARTICIPANTE,
    )
    data_hora = models.DateTimeField('Data de Inscrição', auto_now_add=True)
    presente = models.BooleanField('Presente', default=False)
    data_hora_presenca = models.DateTimeField(
        'Data/Hora da Validação pelo QR Code',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Participa"
        verbose_name_plural = "Participam"
        ordering = ['funcao']
        unique_together = ('inscricao', 'atividade')

    def clean(self):
        super().clean()
        if self.inscricao_id and self.atividade_id:
            if self.atividade.evento != self.inscricao.evento:
                raise ValidationError({
                    'atividade': 'A atividade selecionada não pertence ao evento desta inscrição.'
                })

        if self.presente and not self.data_hora_presenca:
            self.data_hora_presenca = timezone.now()
        elif not self.presente and self.data_hora_presenca:
            self.data_hora_presenca = None

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        status = (
            f'Presente em {localtime(self.data_hora_presenca).strftime("%d/%m/%Y %H:%M")}'
            if self.presente and self.data_hora_presenca
            else 'Ausente'
        )
        return f'{self.inscricao} | {self.atividade} | {self.funcao} | Status: {status}'


# -----------------------------------------------
# MODELS DE ATIVIDADE E PRÊMIOS
# -----------------------------------------------

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
    descricao = models.TextField(
        verbose_name="Descrição",
        max_length=500,
        blank=True,
        null=True,
    )
    tipoAtividade = models.CharField(
        verbose_name="Tipo de Atividade",
        choices=tipoAtividade.choices,
        max_length=20,
        default=tipoAtividade.PALESTRA,
    )
    complementoLocal = models.CharField(
        verbose_name="Complemento do Local",
        max_length=150,
        blank=True,
        null=True,
    )
    horaInicio = models.DateTimeField(verbose_name="Hora de Início")
    horaFim = models.DateTimeField(verbose_name="Hora de Término")
    limitePessoas = models.PositiveIntegerField(
        verbose_name="Limite de Pessoas",
        blank=True,
        null=True,
    )
    codigo_leitor = models.CharField(
        max_length=7,
        unique=True,
        default=gerar_codigo,
        editable=False,
    )

    def clean(self):
        super().clean()
        if self.horaInicio and self.horaFim and self.horaFim <= self.horaInicio:
            raise ValidationError({
                'horaFim': 'A hora de término deve ser posterior à hora de início.'
            })

        if self.limitePessoas is not None and self.limitePessoas < 1:
            raise ValidationError({
                'limitePessoas': 'O limite de participantes deve ser de pelo menos 1 pessoa (ou deixe em branco para ilimitado).'
            })

        if self.evento_id and self.horaInicio and self.horaFim:
            dt_inicio = (
                localtime(self.horaInicio).date()
                if timezone.is_aware(self.horaInicio)
                else self.horaInicio.date()
            )
            dt_fim = (
                localtime(self.horaFim).date()
                if timezone.is_aware(self.horaFim)
                else self.horaFim.date()
            )
            if dt_inicio < self.evento.dataInicio:
                raise ValidationError({
                    'horaInicio': f'A atividade não pode começar antes do evento ({self.evento.dataInicio.strftime("%d/%m/%Y")}).'
                })
            if dt_fim > self.evento.dataFim:
                raise ValidationError({
                    'horaFim': f'A atividade não pode terminar após o encerramento do evento ({self.evento.dataFim.strftime("%d/%m/%Y")}).'
                })

    def save(self, *args, **kwargs):
        if not self.codigo_leitor:
            self.codigo_leitor = gerar_codigo_unico(Atividade, 'codigo_leitor')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nome} - {self.evento.nome}"

    def get_participantes_nomes(self):
        """Retorna a lista com os nomes de todos os inscritos desta atividade."""
        participacoes = self.participa_set.filter(
            inscricao__ativa=True,
            presente=True,
        ).select_related('inscricao__usuario__user_django')
        nomes = []
        for p in participacoes:
            if p.inscricao and p.inscricao.usuario:
                usr = p.inscricao.usuario
                if hasattr(usr, 'nome') and usr.nome:
                    nome = usr.nome
                elif hasattr(usr, 'user_django') and usr.user_django:
                    nome = usr.user_django.get_full_name().strip() or usr.user_django.username
                else:
                    nome = str(usr)
                nomes.append(nome)
        return nomes


class Premio(models.Model):
    """Model para armazenar os prêmios exclusivos de cada atividade no banco de dados."""
    atividade = models.ForeignKey(
        Atividade,
        on_delete=models.CASCADE,
        related_name='premios',
    )
    nome = models.CharField(max_length=200, verbose_name="Nome do Prêmio")
    quantidade = models.PositiveIntegerField(default=1, verbose_name="Quantidade")

    class Meta:
        verbose_name = "Prêmio"
        verbose_name_plural = "Prêmios"

    def __str__(self):
        return f"{self.nome} ({self.quantidade} un) - {self.atividade.nome}"