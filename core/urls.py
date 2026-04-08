from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views


urlpatterns = [
    path('', views.index, name="urlindex"), 
    path('entrar', views.entrar, name="urlentrar"),
    path('sair', views.sair, name="urlsair"),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)