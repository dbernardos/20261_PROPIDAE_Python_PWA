from django.urls import path
from django.http import HttpResponse
from django.conf.urls.static import static
from django.conf import settings
from . import views

# Pode usar {% url %} nos templates
app_name = 'app_evento'

# Create your EVENTO urls here.
# -----------------------------------------------
urlpatterns = [
    path('', views.home, name="urlhome"), 
    path('cadastrar_evento/', views.cadastrar_evento, name='urlcad_evento'),
    path('editar_evento/<int:evento_id>/', views.editar_evento, name='urledt_evento'),
    path('excluir_evento/<int:evento_id>/', views.excluir_evento, name='urldel_evento'),
    path('eventos/<int:evento_id>/', views.detalhes_evento, name='urldet_evento'),
    path('eventos_disponiveis/', views.eventos_disponiveis, name='urldis_evento'),

    path('cadastrar_atividade/<int:evento_id>/', views.cadastrar_atividade, name='urlcad_atividade'),
    path('atividade/<int:atividade_id>/editar/', views.editar_atividade, name='urleditar_atividade'),
    path('atividade/<int:atividade_id>/excluir/', views.excluir_atividade, name='urlexcluir_atividade'),

    path('sorteio/', views.sorteio, name='urlsorteio'),

    path('dados/', views.dados, name='urldados'),
    path('minhas_inscricoes/', views.minhas_inscricoes, name='urlminhas_inscricoes')
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

