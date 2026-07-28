from django.contrib import admin
from .models import Usuario, Quiz, Resposta

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'data_cadastro', 'ultimo_acesso')
    #list_display_links = ('nome')
    #search_fields = ('nome')
    #list_filter = ('nome')
    #list_editable = ('email')

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('numero', 'titulo', 'ativo')
    #list_display_links = ('numero', 'titulo')

@admin.register(Resposta)
class RespostaQuizAdmin(admin.ModelAdmin):
    list_display = ('participa', 'quiz', 'valor_resposta', 'data_resposta')