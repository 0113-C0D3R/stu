# config/settings/prod.py
import os
# config/settings/prod.py

from .base import *

# ###########################################################
# ############# PRODUCTION-SPECIFIC SETTINGS #############
# ###########################################################

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Configure your production domain(s) here
# استبدل هذا بنطاقك الفعلي
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']


# ==============================================================================
# SECURITY HEADERS SETTINGS (as discussed)
# ==============================================================================

# إذا كان موقعك يعمل خلف Reverse Proxy مثل Nginx أو Apache
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'httpss')

# 1. إجبار كل الطلبات على التحويل إلى HTTPS
SECURE_SSL_REDIRECT = True

# 2. إرسال الكوكيز عبر HTTPS فقط
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# 3. منع المتصفح من تخمين أنواع الملفات
SECURE_CONTENT_TYPE_NOSNIFF = True

# 4. تفعيل حماية HSTS (HTTP Strict Transport Security)
# ❗️ تحذير: ابدأ بقيمة صغيرة للاختبار (3600 = ساعة واحدة)
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True


# ... هنا يمكنك إضافة إعدادات الإنتاج الأخرى (مثل قاعدة البيانات) ...