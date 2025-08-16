
import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url   # 👈 added this
 
load_dotenv()


 
BASE_DIR = Path(__file__).resolve().parent.parent
# load_dotenv(os.path.join(BASE_DIR, "student_fees_app_v6", ".env"))
 
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret")
 
DEBUG = False   # 👈 production = False
 
# Allow your Leapcell domain (or * for now)
ALLOWED_HOSTS = ["*"]
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'fees',
]
 
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # 👈 added for static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]
 
ROOT_URLCONF = 'student_fees.urls'
 
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ],},
}]
 
WSGI_APPLICATION = 'student_fees.wsgi.application'
 

# DATABASES config
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
    )
}
# ------------------------------------------------- #
 
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_TZ = False
 
# ---------------- STATIC FILES ---------------- #
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"   # where Django collects static files
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
# ------------------------------------------------ #