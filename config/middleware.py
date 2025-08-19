# config/middleware.py
from django.utils import translation

class ForceAdminArabicMiddleware:
    """
    يجبر /admin/ على العربية بغضّ النظر عن كوكيز اللغة أو لغة المتصفح.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        is_admin = request.path.startswith("/admin/")
        if is_admin:
            translation.activate("ar")
            request.LANGUAGE_CODE = "ar"
        response = self.get_response(request)
        if is_admin:
            translation.deactivate()
        return response
