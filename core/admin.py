from django.contrib import admin
from .models import Participante, Quiz, RespostaQuiz, LogAcesso

@admin.register(Participante)
class ParticipanteAdmin(admin.ModelAdmin):
    list_display = ('cracha', 'nome', 'email', 'data_cadastro', 'ultimo_acesso')
    list_display_links = ('cracha', 'nome')
    search_fields = ('cracha', 'nome')
    list_filter = ('cracha', 'nome')
    #list_editable = ('email')

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('numero', 'titulo', 'descricao', 'ativo')
    list_display_links = ('numero', 'titulo')

@admin.register(RespostaQuiz)
class RespostaQuizAdmin(admin.ModelAdmin):
    list_display = ('participante', 'quiz', 'valor_resposta', 'data_resposta')

@admin.register(LogAcesso)
class LogAcessoAdmin(admin.ModelAdmin):
    list_display = ('participante', 'data_acesso', 'ip_address')