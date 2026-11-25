from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView
from django.views.static import serve

from app_evento.views import home_root

# URLS do SEA.
# -----------------------------------------------

urlpatterns = [
    path('', home_root, name='home_root'),
    path('admin/', admin.site.urls),
    path('login/', include('app_login.urls')),
    path('evento/', include('app_evento.urls')),
    path('quiz/', include('app_quiz.urls')),
    path('chaining/', include('smart_selects.urls')),
    # Arquivos PWA
    path(
        'manifest.json',
        TemplateView.as_view(template_name='manifest.json', content_type='application/manifest+json'),
    ),
    path(
        'service-worker.js',
        never_cache(TemplateView.as_view(template_name='service-worker.js', content_type='application/javascript')),
        name='service_worker',
    ),
]

# Mídia em desenvolvimento e fallback para produção sem servidor de arquivos (Nginx/S3)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]