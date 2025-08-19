from django.apps import AppConfig

class StudentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "students"
    verbose_name = "نظام الطلاب"   # ← هذا الذي يظهر كعنوان القسم في لوحة الأدمن

    def ready(self):
        import students.signals  # إن كنت تستخدم الإشارات
