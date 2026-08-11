from django.urls import path
from django.http import HttpResponse
from django.conf.urls.static import static
from django.conf import settings
from . import views
from django.contrib.auth.views import LoginView, LogoutView

from django.views.decorators.cache import cache_control
from django.contrib.auth import views as auth_views


# Opcional: dá um "nome" ao namespace do app (útil para usar {% url %} nos templates)
app_name = 'login'

urlpatterns = [
    path('login/', LoginView.as_view(template_name='app_login/login.html'), name='urllogin'),
    path('logout/', LogoutView.as_view(), name='app_login/urllogout'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)