from pathlib import Path
import os

# --- Paths
BASE_DIR = Path(__file__).resolve().parent.parent
CORE_DIR = str(BASE_DIR)  # you referenced this in templates/static

# --- Security (dev only)
SECRET_KEY = "dev-secret-key-not-for-production"
DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "FiscroFinance.org", "www.FiscroFinance.org"]

# --- Applications
INSTALLED_APPS = [
    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Extras
    "django.contrib.humanize",  # so {% load humanize %} works

    # Your apps
    "major",
    "profiles",
    "dashboard.home",
    "dashboard.app",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # okay in dev too
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "harmo.urls"

# --- Templates
TEMPLATE_DIR = os.path.join(CORE_DIR, "dashboard", "templates")
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [TEMPLATE_DIR],
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

# --- Database (local dev)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# --- Password validation (keep defaults)
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- I18N
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# --- Static / Media
STATIC_URL = "/static/"
STATICFILES_DIRS = (
    os.path.join(CORE_DIR, "dashboard", "static"),
)
STATIC_ROOT = None  # not used in dev
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(CORE_DIR, "media")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Auth redirects
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "user-home"
LOGOUT_REDIRECT_URL = "home"

# --- Email (dev-friendly; adjust as needed)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "noreply@example.com"
