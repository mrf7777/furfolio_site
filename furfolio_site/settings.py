"""
Django settings for furfolio_site project.

Generated by 'django-admin startproject' using Django 4.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import os
import sys
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv(
    "DJ_SECRET_KEY", "django-insecure-p(cl0%pll8+qrh-2qt_nn^o()=b*5nfu0tnku$3q_mw7oji@2b")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "False") == "True"
DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE", "False") == "True"

ALLOWED_HOSTS = os.getenv("DJ_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.forms',
    'pwa',
    'furfolio',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'furfolio.middleware.TimezoneMiddleware',
]

ROOT_URLCONF = 'furfolio_site.urls'

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
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'furfolio_site.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

if DEVELOPMENT_MODE is True:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'furfolio',
            'USER': 'furfolio',
            'PASSWORD': 'admin',
            'HOST': 'localhost',
            'PORT': '5432',
            'TIME_ZONE': 'America/Chicago'
        }
    }
elif len(sys.argv) > 0 and sys.argv[1] != "collectstatic":
    if os.getenv("DATABASE_URL", None) is None:
        raise Exception("DATABASE_URL environment variable not defined")
    DATABASES = {
        "default": dj_database_url.parse(os.environ.get("DATABASE_URL"))
    }


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 14,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },

    {
        'NAME': 'django_advanced_password_validation.advanced_password_validation.ContainsDigitsValidator',
        'OPTIONS': {
            'min_digits': 1
        }
    },
    {
        'NAME': 'django_advanced_password_validation.advanced_password_validation.ContainsUppercaseValidator',
        'OPTIONS': {
            'min_uppercase': 1
        }
    },
    {
        'NAME': 'django_advanced_password_validation.advanced_password_validation.ContainsLowercaseValidator',
        'OPTIONS': {
            'min_lowercase': 1
        }
    },
    {
        'NAME': 'django_advanced_password_validation.advanced_password_validation.ContainsSpecialCharactersValidator',
        'OPTIONS': {
            'min_characters': 1
        }
    },
    {
        'NAME': 'django_advanced_password_validation.advanced_password_validation.MaximumLengthValidator',
        'OPTIONS': {
            'max_length': 256
        }
    }
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'
USE_I18N = True

USE_TZ = True
TIME_ZONE = 'UTC'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

MEDIA_URL = 'media/'
MEDIA_ROOT = '.media/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# custom user model
AUTH_USER_MODEL = 'furfolio.User'

LOGOUT_REDIRECT_URL = '/'

FORM_RENDERER = "furfolio.forms.CustomFormRenderer"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# Progressive Web App (PWA) settings
PWA_APP_NAME = "Furfolio"
PWA_APP_DESCRIPTION = "Commission management platform for creators and customers."
PWA_APP_LANG = 'en-US'
PWA_APP_ICONS = [
    {
        'src': '/static/icons/favicon-16x16.png',
        'sizes': '16x16',
    },
    {
        'src': '/static/icons/favicon-32x32.png',
        'sizes': '32x32',
    },
    {
        'src': '/static/icons/favicon-48x48.png',
        'sizes': '48x48',
    },
    {
        'src': '/static/icons/favicon-167x167.png',
        'sizes': '167x167',
    },
    {
        'src': '/static/icons/favicon-180x180.png',
        'sizes': '180x180',
    },
    {
        'src': '/static/icons/favicon-192x192.png',
        'sizes': '192x192',
    },
    {
        'src': '/static/icons/favicon-512x512.png',
        'sizes': '512x512',
    },
    {
        'src': '/static/icons/favicon-768x768.png',
        'sizes': '768x768',
    },
]
PWA_APP_SPLASH_SCREEN = [
    {
        'src': '/static/icons/favicon-768x768.png',
        'media': '(device-width: 320px) and (device-height: 568px) and (-webkit-device-pixel-ratio: 2)'
    }
]
