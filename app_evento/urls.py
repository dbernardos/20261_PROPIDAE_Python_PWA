from django.urls import path
from django.http import HttpResponse
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'app_evento'

# URL dos EVENTOS.
# -----------------------------------------------

urlpatterns = [
    path('', views.eventos_disponiveis, name="urldis_evento"), 
    
    path('pwa_home/', views.pwa_home, name='urlpwa_home'),
    path('pwa/evento/<int:evento_id>/atividades/', views.pwa_atividades_evento, name='urlpwa_atividades_evento'),
    
    path('cadastrar_evento/', views.cadastrar_evento, name='urlcad_evento'),
    path('editar_evento/<int:evento_id>/', views.editar_evento, name='urledt_evento'),
    path('excluir_evento/<int:evento_id>/', views.excluir_evento, name='urldel_evento'),
    path('eventos/<int:evento_id>/', views.detalhes_evento, name='urldet_evento'),
    
    path('eventos_disponiveis/', views.eventos_disponiveis, name='urldis_evento_aba'),
    
    path('meus_eventos/<int:evento_id>/', views.detalhes_meus_evento, name='urldet_myevento'),
    path('meus_eventos_disponiveis/', views.meus_eventos_disponiveis, name='urldis_myevento'),

    path('cadastrar_atividade/<int:evento_id>/', views.cadastrar_atividade, name='urlcad_atividade'),
    path('atividade/<int:atividade_id>/editar/', views.editar_atividade, name='urleditar_atividade'),
    path('atividade/<int:atividade_id>/excluir/', views.excluir_atividade, name='urlexcluir_atividade'),

    path('sorteio/', views.sorteio, name='urlsorteio'),
    path('atividade/<int:atividade_id>/sorteio/', views.sorteio, name='urlsorteio_atividade'),

    path('minhas_inscricoes/', views.minhas_inscricoes, name='urlminhas_inscricoes'),
    path('atividade/<int:atividade_id>/participar/', views.alternar_participacao_atividade, name='urlparticipar_atividade'),
    path('evento/<int:evento_id>/participantes/atividade/<int:atividade_id>/', views.gerenciar_participantes, name='urlgerenciar_participantes_atividade'),
    path('evento/<int:evento_id>/comprovante/', views.comprovante_inscricao, name='urlcomprovante_inscricao'),
    path('evento/<int:evento_id>/participantes/', views.gerenciar_participantes, name='urlgerenciar_participantes')
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)