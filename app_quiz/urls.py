from django.urls import path
from django.http import HttpResponse
from django.conf.urls.static import static
from django.conf import settings
from . import views
from django.views.generic import TemplateView

# Pode usar {% url %} nos templates
app_name = 'app_quiz'



# Create your QUIZ urls here.
# -----------------------------------------------
urlpatterns = [
    path('identificar/', views.identificar_funcionario, name='urlidentificar'),
    path('', views.leitor_qrcode, name="urlleitor_qrcode"), 

    path('boas-vindas/<str:cracha>/', views.boas_vindas, name='urlboas_vindas'),
    path('<str:cracha>/desafio/<int:quiz_numero>/', views.quiz_detail, name='urlquiz_detail'),
    path('<str:cracha>/desafio/<int:quiz_numero>/reset/', views.reset_quiz, name='urlreset_quiz'),

     
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)