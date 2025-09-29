# harmo/settings.py
from pathlib import Path
import os
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY", "fallback-key")
DEBUG = os.environ.get("DEBUG", "False") == "True"

ALLOWED_HOSTS = ["altavellum.onrender.com", ".onrender.com", "localhost", "127.0.0.1"]
_render_host = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if _render_host and _render_host not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(_render_host)

INSTALLED_APPS = [
    "django.contrib.admin","django.contrib.auth","django.contrib.contenttypes",
    "django.contrib.sessions","django.contrib.messages","django.contrib.staticfiles",
    "django.contrib.humanize",
    "major","profiles","dashboard.home","dashboard.app",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "harmo.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "major" / "templates", BASE_DIR / "dashboard" / "templates"],
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

WSGI_APPLICATION = "harmo.wsgi.application"

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}
_database_url = os.environ.get("DATABASE_URL")
if _database_url:
    DATABASES["default"] = dj_database_url.config(default=_database_url, conn_max_age=600, ssl_require=True)

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ---------- Static & Media
STATIC_URL = "/static/"



STATICFILES_DIRS = [p for p in [
    BASE_DIR / "static",                 # project-level (optional)
    BASE_DIR / "dashboard" / "static",   # because 'dashboard' is a package, not an app root
    BASE_DIR / "major" / "static",
] if p.exists()]


STATIC_ROOT = BASE_DIR / "staticfiles"

# make sure Django looks in both FileSystem and app /static dirs
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]


# hashed filenames + gzip/brotli; fails build if a CSS url() is missing
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "user-home"
LOGOUT_REDIRECT_URL = "home"

CSRF_TRUSTED_ORIGINS = ["https://altavellum.onrender.com"]
if _render_host:
    CSRF_TRUSTED_ORIGINS.append(f"https://{_render_host}")

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {"console": {"class": "logging.StreamHandler"}},
        "loggers": {
            "django": {"handlers": ["console"], "level": "INFO"},
            "django.request": {"handlers": ["console"], "level": "ERROR", "propagate": False},
            "django.server": {"handlers": ["console"], "level": "ERROR", "propagate": False},
        },
        "root": {"handlers": ["console"], "level": "WARNING"},
    }
