

from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Student, Correspondent

from .models import Student, Document, Correspondent, ExecutiveDirector

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
            return mark_safe(f'<img src="{obj.signature.url}" style="width: 100px;" />')
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