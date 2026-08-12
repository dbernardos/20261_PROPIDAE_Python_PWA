from django.urls import path
from django.http import HttpResponse
from django.conf.urls.static import static
from django.conf import settings
from . import views
from django.views.generic import TemplateView

# Pode usar {% url %} nos templates
app_name = 'app_quiz'

def service_worker(request):
    response = HttpResponse(open('service-worker.js').read(), content_type="application/javascript")
    response['Cache-Control'] = 'no-cache'
    return response

# Create your QUIZ urls here.
# -----------------------------------------------
urlpatterns = [
    path('quiz/', views.quiz, name='urlquiz'),
    path('identificar/', views.identificar_funcionario, name='urlidentificar'),
    path('', views.leitor_qrcode, name="urlleitor_qrcode"), 

    path('boas-vindas/<str:cracha>/', views.boas_vindas, name='urlboas_vindas'),
    path('<str:cracha>/desafio/<int:quiz_numero>/', views.quiz_detail, name='urlquiz_detail'),
    path('<str:cracha>/desafio/<int:quiz_numero>/reset/', views.reset_quiz, name='urlreset_quiz'),

    path('manifest.json', TemplateView.as_view(template_name="app_quiz/manifest.json", content_type='application/manifest+json')),
    path('service-worker.js', TemplateView.as_view(template_name="app_quiz/service-worker.js", content_type='application/javascript'), name="service_worker"),  
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)