"""
Django development settings.

These settings extend base.py for local development.
"""
from .base import *  # noqa: F401, F403

# =============================================================================
# DEBUG
# =============================================================================

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# =============================================================================
# DATABASE
# =============================================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME', default='singapore_smb'),
        'USER': env('DB_USER', default='postgres'),
        'PASSWORD': env('DB_PASSWORD', default='postgres'),
        'HOST': env('DB_HOST', default='localhost'),
        'PORT': env('DB_PORT', default='5432'),
    }
}

# =============================================================================
# DEBUG TOOLBAR
# =============================================================================

INSTALLED_APPS += ['debug_toolbar']  # noqa: F405
MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')  # noqa: F405
INTERNAL_IPS = ['127.0.0.1']

# =============================================================================
# CORS
# =============================================================================

CORS_ALLOW_ALL_ORIGINS = True

# =============================================================================
# EMAIL (Console backend for development)
# =============================================================================

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# =============================================================================
# LOGGING
# =============================================================================

LOGGING['handlers']['console']['level'] = 'DEBUG'  # noqa: F405
LOGGING['loggers']['apps']['level'] = 'DEBUG'  # noqa: F405

# =============================================================================
# DJANGO REST FRAMEWORK
# =============================================================================

# Add browsable API for development
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [  # noqa: F405
    'rest_framework.renderers.JSONRenderer',
    'rest_framework.renderers.BrowsableAPIRenderer',
]

# =============================================================================
# JWT (Longer-lived tokens for development)
# =============================================================================

from datetime import timedelta
SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'] = timedelta(hours=1)  # noqa: F405
SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'] = timedelta(days=30)  # noqa: F405
