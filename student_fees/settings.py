import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
 
BASE_DIR = Path(__file__).resolve().parent.parent
 
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret")  # 👈 safer for deployment
 
# In production, set DEBUG to False
DEBUG = False   # 👈 change this
 
# Allow your Leapcell domain (you can put "*" for testing, but better to add exact domain later)
ALLOWED_HOSTS = ["*"]   # e.g., ["yourapp.leapcell.app"]
 
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
 
    # 👇 Add this for static file serving in production
    'whitenoise.middleware.WhiteNoiseMiddleware',
 
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
 
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3'
    }
}
 
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_TZ = False
 
# ---------------- STATIC FILES ---------------- #
STATIC_URL = '/static/'
 
# Where Django will collect static files
STATIC_ROOT = BASE_DIR / "staticfiles"   # 👈 add this
 
# Keep your dev static folder too
STATICFILES_DIRS = [BASE_DIR / "static"]
 
# Tell Django to use WhiteNoise for compressed static files
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
# ------------------------------------------------ #