from pathlib import Path
import os
import dj_database_url

# SETTINGS do SEA.
# -----------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

# Segurança e Ambiente
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-9q#0(2@c0a%f%4quo!ea(d6u2u=zjt64cjq4wvvgd!qrgf^#g3',
)
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
USE_HTTPS = os.environ.get('USE_HTTPS', str(not DEBUG)) == 'True'

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'portalseaeventos.com.br',
    'www.portalseaeventos.com.br',
    '.ngrok-free.app',
    '.ngrok-free.dev',
    '.ngrok.io',
]

CSRF_TRUSTED_ORIGINS = [
    'https://*.ngrok-free.app',
    'https://*.ngrok-free.dev',
    'https://*.ngrok.io',
    'https://portalseaeventos.com.br',
    'https://www.portalseaeventos.com.br',
]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Aplicações
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
  
    'app_login',
    'app_evento',
    'app_quiz',
  
    'django_bootstrap5',
    'smart_selects',
    'django_user_agents',
]

if DEBUG:
    INSTALLED_APPS += ['django_extensions']

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware',
]

ROOT_URLCONF = 'SEA.urls'
WSGI_APPLICATION = 'SEA.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'SEA.context_processors.session_settings',
            ],
        },
    },
]

# Banco de Dados
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

if os.environ.get('DATABASE_URL'):
    DATABASES['default'] = dj_database_url.config(
        conn_max_age=600,
        conn_health_checks=True,
    )

# Validação de Senha
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internacionalização
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Arquivos Estáticos e Mídia
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Autenticação, Sessão e Cookies
LOGIN_URL = 'app_login:urllogin'
LOGIN_REDIRECT_URL = 'app_evento:urldis_evento'
LOGOUT_REDIRECT_URL = 'app_login:urllogin'

CSRF_USE_SESSIONS = True
CSRF_COOKIE_SECURE = USE_HTTPS
SESSION_COOKIE_SECURE = USE_HTTPS
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SAMESITE = 'Lax'

SESSION_COOKIE_AGE = 1800  # 30 minutos de inatividade
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True