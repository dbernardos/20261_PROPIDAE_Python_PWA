from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

# Pode usar {% url %} nos templates
app_name = 'app_quiz'



# Create your QUIZ urls here.
# -----------------------------------------------
urlpatterns = [
    path('identificar/', views.identificar_funcionario, name='urlidentificar'),
    path('', views.leitor_qrcode, name="urlleitor_qrcode"), 

    #cadastrar quiz
    path('cadastrar_quiz/<int:atividade_id>/', views.cadastrar_quiz, name='urlcad_quiz'),
    #editar quiz
    path('editar_quiz/<int:quiz_id>/', views.cadastrar_quiz, name='urleditar_quiz'),
    #gerenciar quizzes de uma atividade
    path('atividade/<int:atividade_id>/quizzes/', views.gerenciar_quizzes, name='urlgerenciar_quizzes'),
    
    
    path('boas-vindas/<str:cracha>/', views.boas_vindas, name='urlboas_vindas'),
    path('quizzes/<str:cracha>/', views.quizzes, name='urlquizzes'),
    path('<str:cracha>/desafio/<int:quiz_id>/', views.quiz_detail, name='urlquiz_detail'),
    path('<str:cracha>/desafio/<int:quiz_id>/reset/', views.reset_quiz, name='urlreset_quiz'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

