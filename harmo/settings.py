# harmo/settings.py
from pathlib import Path
import os
import dj_database_url  # installed in requirements

# ---------- Paths
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------- Security & env
SECRET_KEY = os.environ.get("SECRET_KEY", "fallback-key")
DEBUG = os.environ.get("DEBUG", "False") == "True"

# Start with safe defaults; we’ll append the Render host dynamically below.
ALLOWED_HOSTS = [
    "altavellum.onrender.com",
    ".onrender.com",
    "localhost",
    "127.0.0.1",
]

# Render provides the external hostname in an env var — add it if present.
_render_host = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if _render_host and _render_host not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(_render_host)

# ---------- Installed apps
INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",

    # Project apps
    "major",
    "profiles",
    "dashboard.home",
    "dashboard.app",
]

# ---------- Middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # WhiteNoise must be right after SecurityMiddleware
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "harmo.urls"

# ---------- Templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "major" / "templates",
            BASE_DIR / "dashboard" / "templates",
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

WSGI_APPLICATION = "harmo.wsgi.application"

# ---------- Database
# Default: SQLite (good for quick deploys). If DATABASE_URL is set (e.g., Postgres on Render),
# it will override automatically.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
_database_url = os.environ.get("DATABASE_URL")
if _database_url:
    DATABASES["default"] = dj_database_url.config(
        default=_database_url,
        conn_max_age=600,
        ssl_require=True,
    )

# ---------- Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------- I18N
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ---------- Static & Media
STATIC_URL = "/static/"
# locations inside your repo to collect from (only if they exist)
_static_dirs = [
    BASE_DIR / "dashboard" / "static",
    BASE_DIR / "major" / "static",
]
STATICFILES_DIRS = [p for p in _static_dirs if p.exists()]
# where collectstatic puts files for WhiteNoise to serve
STATIC_ROOT = BASE_DIR / "staticfiles"

# WhiteNoise storage (if you ever see "Missing staticfiles manifest entry",
# temporarily switch to CompressedStaticFilesStorage to diagnose)
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------- Auth redirects
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "user-home"
LOGOUT_REDIRECT_URL = "home"

# ---------- CSRF (include your Render host)
CSRF_TRUSTED_ORIGINS = [
    "https://altavellum.onrender.com",
]
if _render_host:
    CSRF_TRUSTED_ORIGINS.append(f"https://{_render_host}")

# ---------- Security (behind Render’s proxy)
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    # You can enable HSTS after first confirming HTTPS works end-to-end:
    # SECURE_HSTS_SECONDS = 3600
    # SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    # SECURE_HSTS_PRELOAD = True

# ---------- Logging (prints real errors to Render logs)
if not DEBUG:
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
