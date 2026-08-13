from django.contrib import admin
from .models import  Evento, Atividade, Participa, Inscricao, Apoiador

# Register your models here.
# -----------------------------------------------
@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao', 'emailContato', 'local', 'imagemBanner', 'dataInicio', 'dataFim', 'tipoEvento', 'eventoMultiplo', 'eventoPublico')
    
@admin.register(Atividade)
class AtividadeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao', 'tipoAtividade', 'complementoLocal', 'horaInicio', 'horaFim', 'limitePessoas')
    
@admin.register(Inscricao)
class InscricaoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'evento', 'dataHora', 'cracha')
    
@admin.register(Participa)
class ParticipaAdmin(admin.ModelAdmin):
    list_display = ('inscricao', 'atividade', 'funcao', 'data_hora', 'data_hora_presenca')
    
@admin.register(Apoiador)    
class ApoiadorAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    