# students/tests/conftest.py

import pytest
from django.test import Client
from django.contrib.auth import get_user_model # ✅ 1. استيراد الدالة الصحيحة

@pytest.fixture
def authenticated_client(client): # نمرر الـ client الأساسي من pytest-django
    """
    Fixture to provide a Django test client that is logged in.
    """
    # ✅ 2. الحصول على نموذج المستخدم النشط في المشروع
    User = get_user_model()
    
    # Create a user for the tests, مع التأكد من عدم وجوده مسبقاً
    # هذا يمنع الأخطاء عند إعادة تشغيل الاختبارات عدة مرات
    if not User.objects.filter(username='testuser').exists():
        User.objects.create_user(username='testuser', password='password123')
    
    # Log the user in
    client.login(username='testuser', password='password123')
    
    return client