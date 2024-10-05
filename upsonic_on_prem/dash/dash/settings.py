"""
Django settings for dash project.

Generated by 'django-admin startproject' using Django 4.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import os

from dotenv import load_dotenv

from django.core.management.utils import get_random_secret_key

load_dotenv(dotenv_path=".env")

sentry = os.environ.get("sentry", "false").lower() == "true"
sentry_django_key = os.environ.get(
    "sentry_django_key",
    "https://1040c5057fc1ad3bd322a800edf1aed2@us.sentry.io/4506678631858176",
)
sentry_dsn = os.environ.get(
    "sentry_dsn",
    "https://1040c5057fc1ad3bd322a800edf1aed2@o4506678585786368.ingest.sentry.io/4506678631858176",
)
# settings.py
if sentry:
    import sentry_sdk

    sentry_sdk.init(
        dsn=sentry_django_key,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        traces_sample_rate=1.0,
        # Set profiles_sample_rate to 1.0 to profile 100%
        # of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=1.0,
    )

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

# Write a function that generates a secret key and storing in /db/dash.secret and if it exists, read it from there
# If it does not exist, generate a new one and store it there

if os.path.exists("/db/dash.secret"):
    with open("/db/dash.secret", "r") as file:
        SECRET_KEY = file.readlines()[0]
else:
    with open("/db/dash.secret", "w") as file:
        SECRET_KEY = get_random_secret_key()
        file.write(SECRET_KEY)


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

SOCIALACCOUNT_QUERY_EMAIL = True
ACCOUNT_LOGOUT_ON_GET = True
SOCIALACCOUNT_LOGIN_ON_GET = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
ACCOUNT_ADAPTER = "app.adapter.CustomAccountAdapter"

ACCOUNT_FORMS = {
    "login": "app.forms.MyCustomLoginForm",
}

# Application definition

INSTALLED_APPS = [
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "app",
    "pwa",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "app.utils.DisableCSRF",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django_currentuser.middleware.ThreadLocalUserMiddleware",
]

ROOT_URLCONF = "dash.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(
                BASE_DIR,
                "app",
            ),
            os.path.join(BASE_DIR, "app", "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "dash.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

remote_db=os.environ.get("remote_db", "false").lower() == "true"

if not remote_db:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": "/db/dash.sqlite3"
        }
    }

else:
    db_name=os.environ.get("db_name")
    db_user=os.environ.get("db_user")
    db_pass=os.environ.get("db_pass")
    db_host=os.environ.get("db_host")
    db_port=os.environ.get("db_port")

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': db_name,
            'USER': db_user,
            'PASSWORD': db_pass,
            'HOST': db_host,
            'PORT': db_port, # default port
        }
    }




# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTH_USER_MODEL = "app.User"


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"


STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

ALLOWED_HOSTS = ["*"]

debug_mode = os.environ.get("debug", "false").lower() == "true"
DEBUG = debug_mode

# TODO: Adding csrf protection

AUTHENTICATION_BACKENDS = [
    'app.auth_backends.LdapBackend',
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",
    # `allauth` specific authentication methods, such as login by email
    "allauth.account.auth_backends.AuthenticationBackend",
    "sesame.backends.ModelBackend",
]

log_level = "INFO" if not debug_mode else "DEBUG"
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "loggers": {
        "": {
            "level": log_level,
        },
    },
}


PWA_APP_NAME = "Upsonic"
PWA_APP_DESCRIPTION = "Self-Driven Autonomous Python Libraries"
PWA_APP_THEME_COLOR = "#007bff"
PWA_APP_BACKGROUND_COLOR = "#ffffff"
PWA_APP_DISPLAY = "standalone"
PWA_APP_SCOPE = "/"
PWA_APP_ORIENTATION = "portrait"
PWA_APP_START_URL = "/"
PWA_APP_ICONS = [{"src": "/static/images/favicon.png", "sizes": "160x160"}]
PWA_APP_ICONS_APPLE = [{"src": "/static/images/favicon.png", "sizes": "160x160"}]
PWA_APP_DIR = "ltr"
PWA_APP_LANG = "en-US"
PWA_APP_SHORTCUTS = [
    {"name": "Libraries", "url": "/libraries", "description": "View all libraries"},
]

SESAME_ONE_TIME = True



LOGIN_REDIRECT_URL = '/home'

from dash.tracer import provider
from opentelemetry.instrumentation.django import DjangoInstrumentor

DjangoInstrumentor().instrument(tracer_provider=provider)
