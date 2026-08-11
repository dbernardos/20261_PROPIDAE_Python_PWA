from django.contrib import admin
from .models import  Evento, Atividade, Participa, Inscricao

# Register your models here.
# -----------------------------------------------
@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao', 'emailContato', 'apoiadores', 'local', 'imagemBanner', 'dataInicio', 'dataFim', 'tipoEvento', 'eventoMultiplo', 'eventoPublico')
    
    
@admin.register(Atividade)
class AtividadeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao', 'tipoAtividade', 'complementoLocal', 'horaInicio', 'horaFim', 'limitePessoas')
    
@admin.register(Inscricao)
class InscricaoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'evento', 'dataHora', 'cracha')
    
@admin.register(Participa)
class ParticipaAdmin(admin.ModelAdmin):
    list_display = ('inscricao', 'atividade', 'funcao', 'data_hora', 'data_hora_presenca')
    

