# students/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import (
    Student, Correspondent, Document, ExecutiveDirector,
    CustomUser, AuthUserProxy,   # ← انتبه: AuthUserProxy يأتي من models.py
)

# لو كان CustomUser مسجل مسبقًا في مكان آخر، ألغِ تسجيله هنا احترازيًا
try:
    admin.site.unregister(CustomUser)
except admin.sites.NotRegistered:
    pass

@admin.register(Correspondent)
class CorrespondentAdmin(admin.ModelAdmin):
    list_display = ('category', 'name', 'title')
    search_fields = ('category', 'name')

@admin.register(ExecutiveDirector)
class ExecutiveDirectorAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'institute', 'signature_thumbnail')
    readonly_fields = ('signature_thumbnail',)

    def signature_thumbnail(self, obj):
        if obj.signature:
            return format_html('<img src="{}" style="width: 100px;" />', obj.signature.url)
        return ""
    signature_thumbnail.short_description = "معاينة التوقيع"

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'passport_number')
    search_fields = ('first_name', 'last_name', 'passport_number')

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('student', 'doc_type', 'uploaded_at')
    list_filter = ('doc_type',)

# ===== لا تسجّل CustomUser هنا =====
# @admin.register(CustomUser)   ← احذف/لا تستخدم هذا

# سجّل البروكسي تحت قسم المصادقة والتفويض
@admin.register(AuthUserProxy)
class AuthUserAdmin(UserAdmin):
    model = AuthUserProxy
    list_display = ("username", "email", "first_name", "last_name", "is_staff", "is_active")
    list_filter  = ("is_staff", "is_superuser", "is_active", "groups")

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("المعلومات الشخصية", {"fields": ("first_name", "last_name", "email")}),
        ("الصلاحيات", {"fields": ("is_active", "is_staff", "groups")}),  # لا نعرض is_superuser
        ("تواريخ مهمة", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "password1", "password2", "is_staff", "groups"),
        }),
    )
    search_fields = ("username", "first_name", "last_name", "email")
    ordering = ("username",)

# ترويسات لوحة التحكم
admin.site.site_header = "لوحة التحكم - معهد الفخرية"
admin.site.site_title  = "لوحة التحكم - معهد الفخرية"
admin.site.index_title = "لوحة التحكم - معهد الفخرية"
