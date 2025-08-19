# config/settings/base.py

from pathlib import Path
from functools import lru_cache
import gettext
import pycountry
import logging
import environ, json


# 1. تهيئة django-environ وقراءة ملف .env
env = environ.Env(
    # تعريف القيم الافتراضية وأنواعها
    DEBUG=(bool, False),
)
# قراءة ملف .env إن وُجد
environ.Env.read_env(env_file=Path(__file__).resolve().parent.parent.parent / '.env')

# 2. مسار جذر المشروع
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 3. المفتاح السري من ملف .env
SECRET_KEY = env('DJANGO_SECRET_KEY')

# 4. تثبيت التطبيقات
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap5',
    'widget_tweaks',
    'students.apps.StudentsConfig',
]

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',

    # حدّد اللغة من الكوكي/الهيدر أولاً
    'django.middleware.locale.LocaleMiddleware',

    # بعدها نجبر العربية داخل /admin/
    'config.middleware.ForceAdminArabicMiddleware',

    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                "students.context_processors.site_settings",
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# -------------------------------------------------------------
# Arabic country names for django-countries
# -------------------------------------------------------------
logger = logging.getLogger(__name__)

@lru_cache
def arabic_countries() -> dict[str, str]:
    """
    يُرجِع قاموس {كود ISO → اسم الدولة بالعربية}.
    يحاول ملفات iso-codes 'iso3166' ثم 'iso3166-1'.
    وإن لم يجدها، يَسقُط على قاموس يدوي صغير.
    """
    for domain in ("iso3166", "iso3166-1"):
        try:
            tr = gettext.translation(
                domain=domain,
                localedir=pycountry.LOCALES_DIR,
                languages=["ar"],
            )
            _ = tr.gettext
            return {c.alpha_2: _(c.name) for c in pycountry.countries}
        except FileNotFoundError:
            continue  # جرّب الدومين التالي

    # ------- Fallback يدوي لأكثر الدول شيوعًا -------
    logger.warning("Arabic iso-codes not found; using manual fallback.")
    fallback = {
        "YE": "اليمن",   "SA": "السعودية",  "AE": "الإمارات",
        "QA": "قطر",     "KW": "الكويت",     "OM": "عُمان",
        "BH": "البحرين", "EG": "مصر",        "SD": "السودان",
    }
    return {
        c.alpha_2: fallback.get(c.alpha_2, c.name)
        for c in pycountry.countries
    }

COUNTRIES_OVERRIDE = arabic_countries()



LANGUAGE_CODE = 'ar'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'students' / 'static']

AUTH_USER_MODEL = 'students.CustomUser'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'login'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# حدود ومساحات الرفع
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024      # 5MB لكل طلب
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024     # 5MB لكل ملف

# لمنع المتصفح من التخمين وتشغيل محتوى بغير نوعه
SECURE_CONTENT_TYPE_NOSNIFF = True

# صلاحيات ملفات الرفع على القرص (لا تنفيذ)
FILE_UPLOAD_PERMISSIONS = 0o640

# قيود الشعار
SCHOOL_LOGO_MAX_MB = 2
SCHOOL_LOGO_MAX_PIXELS = 4000 * 4000  # حد أقصى لعدد البيكسلات
SCHOOL_LOGO_ALLOWED_FORMATS = {"PNG", "JPEG", "WEBP"}  # ما نقبله فعليًا
