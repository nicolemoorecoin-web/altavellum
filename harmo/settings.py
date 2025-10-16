from pathlib import Path
from urllib.parse import urlparse
import os
import dj_database_url

# =========================
# Paths
# =========================
BASE_DIR = Path(__file__).resolve().parent.parent

# =========================
# Env helpers
# =========================
def env_list(name: str):
    raw = os.getenv(name, "")
    return [item.strip() for item in raw.split(",") if item.strip()]

def env_bool(name: str, default: bool = False):
    val = os.getenv(name)
    if val is None:
        return default
    return val.lower() in {"1", "true", "yes", "on"}

# =========================
# Security / Debug
# =========================
DEBUG = env_bool("DEBUG", default=True)   # default True for local dev
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-not-for-production")

# Add production domains via ALLOWED_HOSTS env, e.g.
# ALLOWED_HOSTS="shipishly.com,www.shipishly.com"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,.onrender.com").split(",")


# =========================
# Installed apps
# =========================
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

# =========================
# Middleware
# =========================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # serves static on Render
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "harmo.urls"

# =========================
# Templates
# =========================
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

# =========================
# Database
# Works with SQLite locally, Postgres on Render if DATABASE_URL is set.
# Avoids passing sslmode to SQLite (which causes your error).
# =========================
_default_sqlite = f"sqlite:///{BASE_DIR / 'db.sqlite3'}"

db_cfg = dj_database_url.config(
    default=_default_sqlite,
    conn_max_age=600,
    ssl_require=False,  # do NOT force SSL here; we’ll add it only for Postgres
)

engine = (db_cfg.get("ENGINE") or "")
if "sqlite" in engine:
    db_cfg.pop("OPTIONS", None)
else:
    # Postgres only: prefer/require SSL depending on DEBUG
    db_cfg.setdefault("OPTIONS", {})
    db_cfg["OPTIONS"]["sslmode"] = "require" if not DEBUG else "prefer"

DATABASES = {"default": db_cfg}
# =========================
# Password validation
# =========================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# =========================
# i18n / tz
# =========================
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# =========================
# Static / Media
# =========================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = [
    p for p in [
        BASE_DIR / "dashboard" / "static",
        BASE_DIR / "major" / "static",
    ] if p.exists()
]

# WhiteNoise hashed static in prod; plain storage in DEBUG
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
        if not DEBUG
        else "django.contrib.staticfiles.storage.StaticFilesStorage"
    },
}

WHITENOISE_MANIFEST_STRICT = False

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =========================
# Auth redirects
# =========================
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "user-home"
LOGOUT_REDIRECT_URL = "home"

# =========================
# CSRF trusted origins
# Provide with env, e.g.
# CSRF_TRUSTED_ORIGINS="https://shipishly.com,https://www.shipishly.com"
# =========================
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")

# (Optional) trust proxy headers on Render if you terminate SSL there
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
