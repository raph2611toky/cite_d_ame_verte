from pathlib import Path
from dotenv import load_dotenv
import os
from datetime import timedelta
from config.helpers.utils import get_server_settings

load_dotenv()

IP_ADDR,PORT = get_server_settings()

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = 'django-insecure-wttkq7&*pnt9e(sh7e&r09g15@-kv5fop3_u1autog0l^uo@uj'

DEBUG = True

ALLOWED_HOSTS = [IP_ADDR]

LOCAL_APPS = [
    'apps.users.apps.UsersConfig',
    'apps.client.apps.ClientConfig',
    'apps.evenements.apps.EvenementsConfig',
    'apps.formations.apps.FormationsConfig',
    'apps.marketplace.apps.MarketplaceConfig',
    'apps.sante.apps.SanteConfig',
    'apps.meteo.apps.MeteoConfig',
    'apps.chatbot.apps.ChatbotConfig'
]

THIRD_PARTY_APPS = [
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'channels',
    'daphne',
    'django_crontab'
]

INSTALLED_APPS = [
    *LOCAL_APPS,
    *THIRD_PARTY_APPS,
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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

# WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

CHANNEL_LAYER = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"host":[("127.0.0.1", 6379)]},
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'fr-FR'

TIME_ZONE = os.getenv("TIMEZONE_AREA")

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_ROOT = BASE_DIR / 'staticfiles'


MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

BASE_URL = f"http://{IP_ADDR}:{PORT}/"

AUTH_USER_MODEL = 'users.User'
AUTHENTICATION_BACKENDS = ['apps.users.backends.EmailBackend']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',
}

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DJOSER = {
    "PASSWORD_RESET_CONFIRM_URL": "auth/password/reset-password-confirmation/?uid={uid}&token={token}",
    "ACTIVATION_URL": "#/activate/{uid}/{token}",
    "SEND_ACTIVATION_EMAIL": False,
    "SERIALIZERS": {},
    "LOGIN_FIELD": "email",
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

DEBUG = True

ALLOWED_HOSTS = [IP_ADDR]
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DATABASE_NAME'),
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': IP_ADDR,
        'PORT': os.getenv('DATABASE_PORT'),
        'OPTIONS':{
        	'charset': 'utf8mb4'
        }
    }
}

CORS_ALLOWED_ORIGINS = [
    "http://*",
]

CORS_ALLOW_METHODS = [
    'GET',
    'DELETE',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

CORS_ORIGIN_WHITELIST =[
    "http://*:3000",
    "*"
] 

CORS_ALLOW_ALL_ORIGINS = True

CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
    "http://*",
]

CORS_ALLOW_PRIVATE_NETWORK = True


SITE_NAME = "cité d'âme verte"

CRONJOBS = [
    ('*/2 * * * *', 'config.tasks.catastrophes_mg.collect_catastrophes_data', f'>> {os.getenv("LOG_FILE_PATH")} 2>&1'),
    ('0 0 * * *', 'config.tasks.token_mobile_manager.login_all_nigth', f'>> {os.getenv("LOG_FILE_PATH")} 2>&1'),
    ('*/10 * * * *', 'config.tasks.token_mobile_manager.refresh_token_all_ten_minutes', f'>> {os.getenv("LOG_FILE_PATH")} 2>&1'),
    ('*/1 * * * *', 'config.tasks.queue_payment_manager_for_client.process_payment_queue', f'>> {os.getenv("LOG_FILE_PATH")} 2>&1'),
    ('*/1 * * * *', 'config.tasks.queue_payment_manager_for_user.process_payment_queue', f'>> {os.getenv("LOG_FILE_PATH")} 2>&1'),
]