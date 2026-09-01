from django.contrib import admin
from .models import Quiz, Resposta

# Register your models here.
# -----------------------------------------------
@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('id', 'atividade', 'titulo', 'numero', 'subtitulo', 'pergunta', 'dica', 'unidade_medida', 'valor_minimo', 'valor_maximo','valor_ideal', 'icone', 'data_criacao', 'ativo')
    list_display_links = ('id', 'titulo')

@admin.register(Resposta)
class RespostaQuizAdmin(admin.ModelAdmin):
    list_display = ('id', 'participa', 'quiz', 'valor_resposta', 'data_resposta', 'correto')
    list_display_links = ('id', 'participa')