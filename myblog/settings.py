from pathlib import Path
import os
import dj_database_url   # 👈 para leer DATABASE_URL de Railway


# --- Rutas base ---
BASE_DIR = Path(__file__).resolve().parent.parent


# --- Seguridad / Debug ---
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-cambia-esto-en-produccion")

# ⚡ DEBUG se controla con variable de entorno (en Railway pon DEBUG=False)
DEBUG = os.environ.get("DEBUG", "True") == "True"

# Redirigir a tu ruta personalizada de login
LOGIN_URL = '/login/'

# --- Seguridad / Hosts permitidos ---
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    ".up.railway.app",  
]

# --- CSRF confianza ---
CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "https://*.up.railway.app",  
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
    'ckeditor',
    'ckeditor_uploader',
    'taggit',
    'rest_framework',
    "widget_tweaks",

    # Apps locales
    'blog.apps.BlogConfig',

    # Cloudinary
    'cloudinary',
    'cloudinary_storage',
]

# ✅ No pongas CLOUDINARY_STORAGE manual si ya usas CLOUDINARY_URL
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"



# --- Middleware (orden importante) ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ✅ Whitenoise para servir estáticos en prod
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
        'DIRS': [],  # carpeta global de templates si quieres usar BASE_DIR / "templates"
        'APP_DIRS': True,   # habilita blog/templates/
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                # 🔥 nuestros processors
                "blog.context_processors.global_tags",
                "blog.context_processors.unread_notifications",
                "blog.context_processors.latest_notifications",
            ],
        },
    },
]

# --- Base de datos ---
if os.environ.get("DATABASE_URL"):  
    # En Railway → usar Postgres
    DATABASES = {
        "default": dj_database_url.config(
            default=os.environ["DATABASE_URL"],
            conn_max_age=600,
            ssl_require=True
        )
    }
else:
    # En local → usar SQLite
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
STATICFILES_DIRS = [BASE_DIR / "static"] # ✅ aquí cargas tus íconos (ej: static/img/pc.png)

# ⚡ Importante para producción con Whitenoise
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'          # asegúrate que exista: media/

# --- CKEditor (con uploader) ---
CKEDITOR_UPLOAD_PATH = 'uploads/'   # Carpeta de subida relativa a MEDIA_ROOT → media/uploads/
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 300,
        'width': '100%',
    }
}

# --- CKEditor5 (config opcional si usas ckeditor5.fields.CKEditor5Field) ---
CKEDITOR5_CONFIGS = {
    'default': {
        'toolbar': [
            'heading', '|',
            'bold', 'italic', 'link', 'underline', '|',
            'bulletedList', 'numberedList', '|',
            'blockQuote', 'imageUpload'
        ]
    }
}

# --- Auth / Redirecciones ---
LOGIN_REDIRECT_URL = 'blog:post_list'
LOGOUT_REDIRECT_URL = 'blog:post_list'

# --- Defaults ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}