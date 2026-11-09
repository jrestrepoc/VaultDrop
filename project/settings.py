import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'dev-key')

DEBUG = os.environ.get('DJANGO_DEBUG', '1') == '1'

if not DEBUG and SECRET_KEY == 'dev-key':
    raise ImproperlyConfigured('Define DJANGO_SECRET_KEY cuando DJANGO_DEBUG=0.')

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1,testserver').split(',')

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',

    'apps.core',
    'apps.users',
    'apps.wallet',
    'apps.cases',
    'apps.openings',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# runserver sirve los estaticos con DEBUG=1; gunicorn no sirve ninguno por si solo.
if not DEBUG:
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.environ.get('DJANGO_DB_PATH', str(BASE_DIR / 'db.sqlite3')),
        'OPTIONS': {'timeout': 20},
    }
}

if os.environ.get('POSTGRES_HOST'):
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': os.environ['POSTGRES_HOST'],
        'NAME': os.environ['POSTGRES_DB'],
        'USER': os.environ['POSTGRES_USER'],
        'PASSWORD': os.environ['POSTGRES_PASSWORD'],
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Solo detras de Nginx existe Flask; sin Gateway el frontend usa la ruta de Django.
CATALOG_URL = os.environ.get('CATALOG_URL', '')

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.User'

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Sirve las imagenes de assetsweapons/images (skins/armas) bajo el mismo
# namespace estatico, ademas de los directorios static/ de cada app.
STATICFILES_DIRS = [
    *([BASE_DIR / 'assetsweapons'] if (BASE_DIR / 'assetsweapons').exists() else []),
]

# Modo de la Factory de notificaciones (patrón Factory, apps/users/infra/factories.py).
# MOCK: imprime/loguea el mensaje de bienvenida (dev/tests, sin dependencias externas).
# REAL: envía un correo de verdad mediante django.core.mail.send_mail.
NOTIFICACION_MODE = os.environ.get('NOTIFICACION_MODE', 'MOCK')

# Backend de correo para el modo REAL de NotificadorFactory. Por defecto escribe a
# consola para no requerir SMTP configurado; en producción se reemplaza por un backend
# real (ej. SMTP/SendGrid) vía variable de entorno.
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')

# Con DEBUG=0 Django solo envia los errores por correo a ADMINS, que aqui no existen.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'loggers': {'django.request': {'handlers': ['console'], 'level': 'ERROR'}},
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'EXCEPTION_HANDLER': 'apps.core.exceptions.custom_exception_handler',
}
