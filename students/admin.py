# admin.py (النسخة المُعدلة والآمنة)

from django.contrib import admin
# 1. تم تغيير الاستيراد من mark_safe إلى format_html
from django.utils.html import format_html
from .models import Student, Correspondent, Document, ExecutiveDirector

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
            # 2. تم استخدام format_html لإنشاء HTML آمن
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


admin.site.site_header = "لوحة التحكم - معهد الفخرية"   # العنوان الكبير أعلى لوحة الإدارة (وأعلى صفحة تسجيل الدخول)
admin.site.site_title  = "لوحة التحكم - معهد الفخرية"   # نص عنوان التبويب في المتصفح
admin.site.index_title = "لوحة التحكم - معهد الفخرية"    # عنوان صفحة البداية داخل الأدمن