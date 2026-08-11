from django.contrib import admin
from .models import Usuario

# Register your models here.
# -----------------------------------------------
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'biografia', 'fotoPerfil', 'cpf', 'telefone', 'dataNascimento', 'cargo', 'formacao', 'empresa', 'data_cadastro', 'ultimo_acesso')
    #list_display_links = ('nome')
    #search_fields = ('nome')
    #list_filter = ('nome')
    #list_editable = ('email')
