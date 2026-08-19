from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.conf import settings

from django.views.static import serve

def service_worker(request):
        response = HttpResponse(open('service-worker.js').read(), content_type="application/javascript")
        response['Cache-Control'] = 'no-cache'
        return response

urlpatterns = [
    
     
    path('admin/', admin.site.urls),

    # Todas as URLs que começam com "login/" vão para o app_login
    path('login/', include('app_login.urls')),

    # Todas as URLs que começam com "evento/" vão para o app_evento
    path('evento/', include('app_evento.urls')),

    # Todas as URLs que começam com "quiz/" vão para o app_quiz
    path('quiz/', include('app_quiz.urls')),
    
    path('manifest.json', TemplateView.as_view(template_name="manifest.json", content_type='application/manifest+json')),
    path('service-worker.js', TemplateView.as_view(template_name="service-worker.js", content_type='application/javascript'), name="service_worker"),
    
    path('chaining/', include('smart_selects.urls')),
]

# Força o Django a servir arquivos estáticos e de mídia quando DEBUG = False
if not settings.DEBUG:
    urlpatterns += [
        # Rota para os arquivos de mídia (Uploads, foto de perfil)
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
        
        # Rota para os arquivos estáticos (Imagens do sistema, CSS, JS)
        re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    ]