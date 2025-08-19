# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from students.views import HomeView

urlpatterns = [
    # 🏠 الصفحة الرئيسية
    path("", HomeView.as_view(), name="home"),

    # ⚙️ لوحات الإدارة
    path("admin/", admin.site.urls),

    # 👤 مصادقة Django الافتراضيّة
    path("accounts/", include("django.contrib.auth.urls")),

    # 📚 تطبيق الطلاب (جميع روابطه تحت /student/)
    path(
        "student/",
        include(("students.urls", "students"), namespace="students"),
    ),
]

# ملفات الميديا والاستاتيك في وضع التطوير
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# إعدادات إعادة التوجيه بعد تسجيل الدخول/الخروج
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/student/"
LOGOUT_REDIRECT_URL = "/student/"


handler403 = "students.views.error_403"