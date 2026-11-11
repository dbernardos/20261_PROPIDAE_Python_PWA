from django.contrib import admin
from .models import Usuario

# REGISTROS do LOGIN.
# -----------------------------------------------

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'nome', 
        'email', 
        'biografia', 
        'fotoPerfil', 
        'cpf', 
        'telefone', 
        'dataNascimento', 
        'cargo', 
        'formacao', 
        'empresa', 
        'data_cadastro', 
        'ultimo_acesso'
    )
    list_display_links = ('id', 'nome')
    
    #search_fields = ('nome')
    #list_filter = ('nome')
    #list_editable = ('email')
