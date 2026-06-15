from django.urls import path
from django.conf.urls.static import static
from django.http import HttpResponse
from django.conf import settings
from . import views

from django.views.decorators.cache import cache_control

def service_worker(request):
    response = HttpResponse(open('service-worker.js').read(), content_type="application/javascript")
    response['Cache-Control'] = 'no-cache'
    return response

urlpatterns = [
    path('', views.leitor_qrcode, name="urlleitor_qrcode"), 
    path('home', views.index, name="urlindex"), 
    path('entrar', views.entrar, name="urlentrar"),
    path('sair', views.sair, name="urlsair"),
    path('quiz', views.quiz, name='urlquiz'),
    path('boas-vindas/<str:cracha>/', views.boas_vindas, name='boas_vindas'),
    path('<str:cracha>/desafio/<int:quiz_numero>/', views.quiz_detail, name='quiz_detail'),
    path('<str:cracha>/desafio/<int:quiz_numero>/reset/', views.reset_quiz, name='reset_quiz'),

    # Service Worker e Manifest PWA
    path('service-worker.js', service_worker, name='service_worker'),
    path('manifest.json', 
         cache_control(no_cache=True)(
             lambda r: HttpResponse(
                 open('manifest.json').read(), 
                 content_type="application/json"
             )
         ), 
         name='manifest'),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)