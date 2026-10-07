from django.urls import path
from django.http import HttpResponse
from django.conf.urls.static import static
from django.conf import settings
from . import views
from django.contrib.auth.views import LoginView, LogoutView

from django.views.decorators.cache import cache_control
from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.decorators.cache import never_cache


# Pode usar {% url %} nos templates
app_name = 'app_login'

# Create your LOGIN urls here.
# -----------------------------------------------
urlpatterns = [
    path('', never_cache(LoginView.as_view(template_name='app_login/login.html', redirect_authenticated_user=True)), name='urllogin'),

    path('logout/', LogoutView.as_view(), name='urllogout'),
    path('cadastrar/', views.cadastrar_usuario, name='urlcad_usuario'),

    path('meu_usuario/', views.meu_usuario, name="urlmeu_usuario"), 
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)