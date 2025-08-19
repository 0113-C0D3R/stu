# config/apps.py
from django.contrib.auth.apps import AuthConfig

class ArabicAuthConfig(AuthConfig):
    # نحتفظ بالاسم الأصلي للتطبيق (auth) ونغيّر التسمية الظاهرة فقط
    verbose_name = "المستخدمين / الصلاحيات"
