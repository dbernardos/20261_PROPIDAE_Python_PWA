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
    path('editar_evento/<int:evento_id>/', views.cadastrar_evento, name='urledt_evento'),
    path('excluir_evento/<int:evento_id>/', views.excluir_evento, name='urldel_evento'),
    path('eventos/<int:evento_id>/', views.detalhes_evento, name='urldet_evento'),

    path('cadastrar_atividade/<int:evento_id>/', views.cadastrar_atividade, name='urlcad_atividade'),

    path('dados/', views.dados, name='urldados'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)