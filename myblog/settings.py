from pathlib import Path
import os

# --- Rutas base ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Seguridad / Debug ---
SECRET_KEY = 'dev-secret-key-cambia-esto-en-produccion'
DEBUG = True

# --- Seguridad / Hosts permitidos ---
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "192.168.30.133",   # ⚡ cambia por la IP local de tu PC
]

# --- CSRF confianza ---
CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "http://192.168.30.133:8000",  # ⚡ cambia por tu IP real
]

# --- Apps instaladas ---
INSTALLED_APPS = [
    # Core Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Terceros
    'ckeditor',              # Editor
    'ckeditor_uploader',     # Subida de archivos/imagenes desde CKEditor
    'taggit',                # Tags

    # Apps locales
    'blog.apps.BlogConfig',
]

# --- Middleware (orden importante) ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',   # antes que Auth
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# --- URLs / WSGI ---
ROOT_URLCONF = 'myblog.urls'
WSGI_APPLICATION = 'myblog.wsgi.application'

# --- Templates (motor DjangoTemplates) ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Si quieres una carpeta de templates global, descomenta y apunta a BASE_DIR / "templates"
        'DIRS': [],
        'APP_DIRS': True,   # habilita blog/templates/
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'blog.context_processors.global_tags',
            ],
        },
    },
]

# --- Base de datos (SQLite para desarrollo) ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --- Validadores de contraseña ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- Localización ---
LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Panama'
USE_I18N = True
USE_TZ = True

# --- Archivos estáticos y media ---
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'   # para collectstatic en prod
STATICFILES_DIRS: list[Path] = []        # añade rutas locales si usas assets propios

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'          # asegúrate que exista: media/

# --- CKEditor (con uploader) ---
# Carpeta de subida relativa a MEDIA_ROOT → media/uploads/
CKEDITOR_UPLOAD_PATH = 'uploads/'
# Permitir archivos no imagen (opcional)
# CKEDITOR_ALLOW_NONIMAGE_FILES = True
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 300,
        'width': '100%',
    }
}

# --- Auth / Redirecciones ---
LOGIN_REDIRECT_URL = 'blog:post_list'
LOGOUT_REDIRECT_URL = 'blog:post_list'

# --- Defaults ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
