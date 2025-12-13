from pathlib import Path
from datetime import timedelta
import os
import environ # django-environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize environment variables
env = environ.Env()
# Read .env file
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# ==============================================================================
# CORE SETTINGS
# ==============================================================================

SECRET_KEY = env('SECRET_KEY', default='unsafe-secret-key')
DEBUG = env.bool('DEBUG', default=True)

ALLOWED_HOSTS = ['*'] # Allow all hosts (matches Regular behavior, tighten for prod)

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third Party
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist', # For logout functionality
    'corsheaders',
    'drf_spectacular', # Swagger documentation

    # Local Apps
    'apps.common',
    'apps.users',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware', # CORS
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Custom Exception Middleware can be added here if needed, 
    # but DRF handles API exceptions via REST_FRAMEWORK settings.
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

WSGI_APPLICATION = 'config.wsgi.application'


# ==============================================================================
# DATABASE
# ==============================================================================
# Supports both SQLite and PostgreSQL via .env
DATABASES = {
    'default': env.db('DATABASE_URL', default='sqlite:///db.sqlite3')
}


# ==============================================================================
# PASSWORD VALIDATION
# ==============================================================================
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8}, # Matches Regular requirement
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ==============================================================================
# INTERNATIONALIZATION
# ==============================================================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# ==============================================================================
# STATIC FILES
# ==============================================================================
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


# ==============================================================================
# CUSTOM USER MODEL
# ==============================================================================
AUTH_USER_MODEL = 'users.User'


# ==============================================================================
# REST FRAMEWORK (DRF) CONFIGURATION
# ==============================================================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'apps.common.pagination.CustomPageNumberPagination',
    'PAGE_SIZE': 10,
    'EXCEPTION_HANDLER': 'apps.common.exceptions.api_exception_handler', # Custom Error Handler
}

# ==============================================================================
# JWT CONFIGURATION (Simple JWT)
# ==============================================================================
# Matches logic in src/config/tokens.js and src/config/config.js
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=env.int('JWT_ACCESS_EXPIRATION_MINUTES', default=30)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=env.int('JWT_REFRESH_EXPIRATION_DAYS', default=30)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'sub', # Matches standard JWT 'sub' claim used in Regular
}

# Custom constants for other token types (Reset Password, Verify Email)
JWT_RESET_PASSWORD_EXPIRATION_MINUTES = env.int('JWT_RESET_PASSWORD_EXPIRATION_MINUTES', default=10)
JWT_VERIFY_EMAIL_EXPIRATION_MINUTES = env.int('JWT_VERIFY_EMAIL_EXPIRATION_MINUTES', default=10)


# ==============================================================================
# CORS CONFIGURATION
# ==============================================================================
CORS_ALLOW_ALL_ORIGINS = True # Set to False and configure CORS_ALLOWED_ORIGINS in prod


# ==============================================================================
# SWAGGER / API DOCS
# ==============================================================================
SPECTACULAR_SETTINGS = {
    'TITLE': 'Django REST API Starter Kit',
    'DESCRIPTION': 'Documentation for the REST API (Ported from Regular)',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    # Swagger UI Security Setup
    'COMPONENT_SPLIT_REQUEST': True,
}


# ==============================================================================
# EMAIL CONFIGURATION
# ==============================================================================
if DEBUG:
    # Console backend for development (prints email to terminal)
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    
EMAIL_HOST = env('SMTP_HOST', default='smtp.example.com')
EMAIL_PORT = env.int('SMTP_PORT', default=587)
EMAIL_HOST_USER = env('SMTP_USERNAME', default='')
EMAIL_HOST_PASSWORD = env('SMTP_PASSWORD', default='')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = env('EMAIL_FROM', default='support@yourapp.com')