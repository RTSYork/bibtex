"""
Django settings for csbibtex project.
"""

import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

from csbibtex.settings_secret import *

try:
    if DEBUG_REMOTE_USER != None:
        DEBUG = True
        TEMPLATE_DEBUG = True
except NameError:
    DEBUG = False
    TEMPLATE_DEBUG = False

ALLOWED_HOSTS = ['*']


# Application definition
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bibtex',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'csbibtex.urls'
WSGI_APPLICATION = 'csbibtex.wsgi.application'
TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, "db", 'db.sqlite3'),
    }
}

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/rts/static/'

# File storage
MEDIA_ROOT = os.path.join(BASE_DIR, "bibtex", "static", "papers")
MEDIA_URL = STATIC_URL + "papers/"

# Email
EMAIL_HOST = "smtp.york.ac.uk"
EMAIL_PORT = 25
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False
