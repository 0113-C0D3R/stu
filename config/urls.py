"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    # هنا نُدرِج ملف students/urls.py مع إعطائه الاسم 'students'
    path('student/', include(('students.urls', 'students'), namespace='students')),
    path('', include('students.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    

LOGIN_URL = '/students/login/'
LOGIN_REDIRECT_URL = '/students/'
LOGOUT_REDIRECT_URL = '/students/'
