from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from django.views.decorators.cache import never_cache

from . import views

app_name = 'app_login'

# URL do LOGIN.
# -----------------------------------------------

urlpatterns = [
    path( '',never_cache(LoginView.as_view(
            template_name='app_login/login.html',
            redirect_authenticated_user=True,
        )), name='urllogin',
    ),
    path('logout/', LogoutView.as_view(), name='urllogout'),
    path('cadastrar/', views.cadastrar_usuario, name='urlcad_usuario'),
    path('meu_usuario/', views.meu_usuario, name='urlmeu_usuario'),
]