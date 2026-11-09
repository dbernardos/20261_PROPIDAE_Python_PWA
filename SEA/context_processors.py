from django.conf import settings

def session_settings(request):
    return {
        'SESSION_COOKIE_AGE': settings.SESSION_COOKIE_AGE
    }