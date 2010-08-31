import os
_base = os.path.dirname(__file__)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Panu Tangchalermkul', 'panuta@gmail.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'sms_dev',                      # Or path to database file if using sqlite3.
        'USER': 'sms_dev',                      # Not used with sqlite3.
        'PASSWORD': 'sms_dev',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

SYSTEM_NAME = 'Thai Health Strategy Management Systems'
WEBSITE_ADDRESS = 'localhost:8000'

TIME_ZONE = 'Asia/Bangkok'
LANGUAGE_CODE = 'th'
SITE_ID = 1
USE_I18N = True
USE_L10N = True

MEDIA_ROOT = os.path.join(_base, 'media') + '/'
MEDIA_URL = '/m'
ADMIN_MEDIA_PREFIX = '/media/'

AUTH_PROFILE_MODULE = 'accounts.UserAccount'
ACCOUNT_ACTIVATION_DAYS = 3
LOGIN_REDIRECT_URL = '/home/'

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'application.testbed@gmail.com'
EMAIL_HOST_PASSWORD = 'opendream'
EMAIL_PORT = 587
EMAIL_SUBJECT_PREFIX = '[SMS] '

SYSTEM_NOREPLY_EMAIL = EMAIL_HOST_USER

# Make this unique, and don't share it with anybody.
SECRET_KEY = '10vd5(jw9bjaiu3wn7&thabp%4pdb10n0(3q5&)=)$34mive8('

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    #'thaihealthsms.context_processors.user_account',
)

MIDDLEWARE_CLASSES = (
    'thaihealthsms.middleware.AJAXSimpleExceptionResponse',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'thaihealthsms.urls'

TEMPLATE_DIRS = (
    os.path.join(_base, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    
    'thaihealthsms.accounts',
    'thaihealthsms.administration',
    'thaihealthsms.domain',
    'thaihealthsms.helper',
    'thaihealthsms.budget',
    # 'thaihealthsms.progress',
    'thaihealthsms.kpi',
    
    'registration',
)
