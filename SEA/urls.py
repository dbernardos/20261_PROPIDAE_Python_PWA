from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),

    # Todas as URLs que começam com "login/" vão para o app_login
    path('login/', include('app_login.urls')),

    # Todas as URLs que começam com "evento/" vão para o app_evento
    path('evento/', include('app_evento.urls')),

    # Todas as URLs que começam com "quiz/" vão para o app_quiz
    path('quiz/', include('app_quiz.urls')),
]