from django.db import models
from django.utils import timezone
import uuid
from django.contrib.auth.models import User

# Create your LOGIN models here.
# -----------------------------------------------
"""Model da tabela Usuario"""
class Usuario(models.Model):
    nome = models.CharField(max_length=200)
    email = models.EmailField(max_length=200,unique=True)
    biografia = models.CharField(max_length=500, blank=True, null=True)
    fotoPerfil = models.ImageField(upload_to='perfil/', blank=True, null=True)
    cpf = models.CharField(max_length=14, unique=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    dataNascimento = models.DateField(blank=True, null=True)
    cargo = models.CharField(max_length=45, blank=True, null=True)
    formacao = models.CharField(max_length=200, blank=True, null=True)
    empresa = models.CharField(max_length=45, blank=True, null=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ultimo_acesso = models.DateTimeField(auto_now=True)
    participante = models.OneToOneField(User, on_delete=models.CASCADE)


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
