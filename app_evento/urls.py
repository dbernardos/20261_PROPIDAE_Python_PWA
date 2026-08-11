from django.urls import path
from django.http import HttpResponse
from django.conf.urls.static import static
from django.conf import settings
from . import views

# Opcional: dá um "nome" ao namespace do app (útil para usar {% url %} nos templates)
app_name = 'evento'

urlpatterns = [
    path('cadastrar_evento/', views.cadastrar_evento, name='cadastrar_evento'),
    path('cadastrar_atividade/<int:evento_id>/', views.cadastrar_atividade, name='cadastrar_atividade'),

    path('dados/', views.dados, name='dados'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)