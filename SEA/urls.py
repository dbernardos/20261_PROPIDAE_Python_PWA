from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

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
]