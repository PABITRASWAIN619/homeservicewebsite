from pathlib import Path
import os
import dj_database_url


# ======================================================
# BASE DIRECTORY
# ======================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ======================================================
# SECURITY
# ======================================================

SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-change-this-key"
)

DEBUG = os.environ.get("DEBUG", "False") == "True"


ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    ".onrender.com",
]


CSRF_TRUSTED_ORIGINS = [
    "https://homeservicewebsite-143.onrender.com",
]


# ======================================================
# APPLICATIONS
# ======================================================

INSTALLED_APPS = [

    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",


    # Application
    "accounts",


    # Channels
    "channels",


    # Cloudinary
    "cloudinary",
    "cloudinary_storage",

]


# ======================================================
# MIDDLEWARE
# ======================================================

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


# ======================================================
# URL CONFIG
# ======================================================

ROOT_URLCONF = "home_service.urls"



# ======================================================
# TEMPLATES
# ======================================================

TEMPLATES = [

    {

        "BACKEND":
        "django.template.backends.django.DjangoTemplates",

        "DIRS":
        [
            BASE_DIR / "templates"
        ],

        "APP_DIRS": True,


        "OPTIONS":
        {

            "context_processors":
            [

                "django.template.context_processors.request",

                "django.contrib.auth.context_processors.auth",

                "django.contrib.messages.context_processors.messages",

            ],

        },

    },

]



# ======================================================
# WSGI / ASGI
# ======================================================

WSGI_APPLICATION = "home_service.wsgi.application"

ASGI_APPLICATION = "home_service.asgi.application"



# ======================================================
# DATABASE
# Render PostgreSQL
# Local SQLite
# ======================================================


DATABASE_URL = os.environ.get("DATABASE_URL")


if DATABASE_URL:


    DATABASES = {

        "default":
        dj_database_url.config(

            default=DATABASE_URL,

            conn_max_age=600,

            ssl_require=True

        )

    }


else:


    DATABASES = {

        "default":
        {

            "ENGINE":
            "django.db.backends.sqlite3",

            "NAME":
            BASE_DIR / "db.sqlite3",

        }

    }



# ======================================================
# PASSWORD VALIDATION
# ======================================================

AUTH_PASSWORD_VALIDATORS = [

    {
        "NAME":
        "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },


    {
        "NAME":
        "django.contrib.auth.password_validation.MinimumLengthValidator",
    },


    {
        "NAME":
        "django.contrib.auth.password_validation.CommonPasswordValidator",
    },


    {
        "NAME":
        "django.contrib.auth.password_validation.NumericPasswordValidator",
    },

]



# ======================================================
# LANGUAGE
# ======================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kolkata"

USE_I18N = True

USE_TZ = True



# ======================================================
# STATIC FILES
# ======================================================

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"


# Only load if folder exists

if (BASE_DIR / "static").exists():

    STATICFILES_DIRS = [

        BASE_DIR / "static"

    ]


STATICFILES_STORAGE = (
    "whitenoise.storage.CompressedManifestStaticFilesStorage"
)



# ======================================================
# CLOUDINARY
# ======================================================

import cloudinary


cloudinary.config(

    cloud_name=os.environ.get(
        "CLOUDINARY_CLOUD_NAME"
    ),

    api_key=os.environ.get(
        "CLOUDINARY_API_KEY"
    ),

    api_secret=os.environ.get(
        "CLOUDINARY_API_SECRET"
    )

)



DEFAULT_FILE_STORAGE = (
    "cloudinary_storage.storage.MediaCloudinaryStorage"
)


MEDIA_URL = "/media/"



# ======================================================
# LOGIN
# ======================================================

LOGIN_URL = "/login/"

LOGIN_REDIRECT_URL = "/customer-dashboard/"

LOGOUT_REDIRECT_URL = "/login/"



# ======================================================
# SESSION
# ======================================================

SESSION_ENGINE = (
    "django.contrib.sessions.backends.db"
)


SESSION_COOKIE_AGE = 86400


SESSION_SAVE_EVERY_REQUEST = True


SESSION_EXPIRE_AT_BROWSER_CLOSE = True



# ======================================================
# EMAIL OTP
# ======================================================

EMAIL_BACKEND = (
    "django.core.mail.backends.smtp.EmailBackend"
)


EMAIL_HOST = "smtp.gmail.com"

EMAIL_PORT = 587

EMAIL_USE_TLS = True


EMAIL_HOST_USER = os.environ.get(
    "EMAIL_HOST_USER"
)


EMAIL_HOST_PASSWORD = os.environ.get(
    "EMAIL_HOST_PASSWORD"
)



# ======================================================
# AUTH BACKEND
# ======================================================

AUTHENTICATION_BACKENDS = [

    "accounts.backends.EmailBackend",

    "django.contrib.auth.backends.ModelBackend",

]



# ======================================================
# CHANNELS
# ======================================================

CHANNEL_LAYERS = {


    "default":

    {

        "BACKEND":
        "channels.layers.InMemoryChannelLayer"

    }


}



# ======================================================
# SECURITY
# ======================================================

SECURE_PROXY_SSL_HEADER = (

    "HTTP_X_FORWARDED_PROTO",

    "https",

)


SECURE_SSL_REDIRECT = False


SESSION_COOKIE_SECURE = False


CSRF_COOKIE_SECURE = False



# ======================================================
# DEFAULT PRIMARY KEY
# ======================================================

DEFAULT_AUTO_FIELD = (
    "django.db.models.BigAutoField"
)