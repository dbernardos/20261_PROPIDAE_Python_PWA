from django.contrib import admin
from .models import Usuario, Quiz, Resposta, Atividade, Evento, Participa, Inscricao

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'biografia', 'fotoPerfil', 'cpf', 'telefone', 'dataNascimento', 'cargo', 'formacao', 'empresa', 'data_cadastro', 'ultimo_acesso')
    #list_display_links = ('nome')
    #search_fields = ('nome')
    #list_filter = ('nome')
    #list_editable = ('email')

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('atividade', 'titulo', 'numero', 'subtitulo', 'pergunta', 'dica', 'unidade_medida', 'valor_minimo', 'valor_maximo','valor_ideal', 'icone', 'data_criacao', 'ativo')
    #list_display_links = ('numero', 'titulo')

@admin.register(Resposta)
class RespostaQuizAdmin(admin.ModelAdmin):
    list_display = ('participa', 'quiz', 'valor_resposta', 'data_resposta', 'correto')
    
    
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
    
