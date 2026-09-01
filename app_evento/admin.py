from django.contrib import admin
from .models import  Evento, Atividade, Participa, Inscricao, Apoiador

# Register your models here.
# -----------------------------------------------
@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('id','nome', 'descricao', 'emailContato', 'local', 'imagemBanner', 'dataInicio', 'dataFim', 'tipoEvento', 'eventoMultiplo', 'eventoPublico')
    list_display_links = ('id', 'nome')
    
@admin.register(Atividade)
class AtividadeAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'descricao', 'tipoAtividade', 'complementoLocal', 'horaInicio', 'horaFim', 'limitePessoas')
    list_display_links = ('id', 'nome')
    
@admin.register(Inscricao)
class InscricaoAdmin(admin.ModelAdmin):
    list_display = ('id','usuario', 'evento', 'dataHora', 'cracha')
    list_display_links = ('id', 'usuario')
    
@admin.register(Participa)
class ParticipaAdmin(admin.ModelAdmin):
    list_display = ('id', 'inscricao', 'atividade', 'funcao', 'data_hora', 'data_hora_presenca')
    list_display_links = ('id', 'inscricao')
    
@admin.register(Apoiador)    
class ApoiadorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome')
    list_display_links = ('id', 'nome')
    