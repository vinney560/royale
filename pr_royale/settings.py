from pathlib import Path
import os
from decouple import config
import dj_database_url

from sys_views.pretty_printer import (
    print_info, print_success, print_warning
    )

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", cast=bool, default=False)

ALLOWED_HOSTS = ["*"]

haddler404 = "app_royale.http_error_handlers.all_handlers.handler_404_request"
haddler500 = "app_royale.http_error_handlers.all_handlers.handler_500_request"

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # New apps
    'app_royale.apps.AppRoyaleConfig',
    'app_viulive.apps.AppViuliveConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Whitenoise middleware
    # https://warehouse.python.org/project/whitenoise/
    # https://warehouse.python.org/project/whitenoise/django/
    # https://warehouse.python.org/project/whitenoise/django/whitenoise/
    'whitenoise.middleware.WhiteNoiseMiddleware',

    # Rate Limit middleware
    # https://warehouse.python.org/project/ratelimit/
    'django_ratelimit.middleware.RatelimitMiddleware',
]

ROOT_URLCONF = 'pr_royale.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                # Context for anonymous_user. |> usage (anonymous_user.username, id...)
                'app_royale.anonymous_user_context.anonymous_user',
            ],
        },
    },
]

WSGI_APPLICATION = 'pr_royale.wsgi.application'

# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

# Check if we should force SQLite (useful for testing)
FORCE_SQLITE = config('FORCE_SQLITE', cast=bool, default=False)

if FORCE_SQLITE:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    print_info("🔒 SQLite forced via environment variable")
else:
    try:
        DATABASE_URI = config("DATABASE_URL")
        
        # Test with a simple query
        import psycopg2
        import urllib.parse
        
        result = urllib.parse.urlparse(DATABASE_URI)
        dbname = result.path[1:]
        user = result.username
        password = result.password
        host = result.hostname
        port = result.port or 5432
        
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port,
            connect_timeout=3
        )
        conn.close()
        
        DATABASES = {
            'default': {
                **dj_database_url.config(
                    default=config('DATABASE_URL'),
                    conn_max_age=600,
                    conn_health_checks=True,
                    ssl_require=True,
                ),
                'OPTIONS': {
                    'sslmode': 'require',
                    'connect_timeout': 10,
                    'pool': {
                        'min_size': 2,
                        'max_size': 20,
                        'timeout': 30,
                    }
                }
            }
        }
        print_success("✅ Connected to PostgreSQL")
        
    except Exception as e:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
        print_warning(f"⚠️  Falling back to SQLite: {str(e)}")

# Session && Cache
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'ratelimit': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'royale_ratelimit_cache'
    }
}

# Rate Limit
# https://warehouse.python.org/project/ratelimit/
RATELIMIT_USE_CACHE = 'ratelimit'
RATELIMIT_VIEW = "app_royale.http_error_handlers.all_handlers.handler_429_request"
RATELIMIT_ENABLE = True

# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Nairobi'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static', 
]
