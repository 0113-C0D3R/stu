from django import forms
from django.forms import inlineformset_factory
from .models import Student, Document, SiteSettings
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.translation import gettext_lazy as _
from .validators import validate_image_strict
from .utils.images import sanitize_and_reencode_to_png
import uuid

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        exclude = ["reference_number"]   # امنعه من الظهور
        fields = '__all__'
        widgets = {
            'birth_date': forms.DateInput(attrs={'class': 'form-control flatpickr'}),
            'date_of_issued': forms.DateInput(attrs={'class': 'form-control flatpickr'}),
            'passport_expiry': forms.DateInput(attrs={'class': 'form-control flatpickr'}),
            'registration_date': forms.DateInput(attrs={'class': 'form-control flatpickr'}),
            'residence_issued_date': forms.DateInput(attrs={'class': 'form-control flatpickr'}),
            'residence_end_date': forms.DateInput(attrs={'class': 'form-control flatpickr'}),
            'entry_date': forms.DateInput(attrs={'class': 'form-control flatpickr'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control flatpickr'}),
            'end_registration_date': forms.DateInput(attrs={'class': 'form-control flatpickr'}),
            'companion_residence_end_date': forms.DateInput(attrs={'class': 'form-control flatpickr'}),
            'nationality': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'حفظ الطالب', css_class='btn btn-primary'))


# ----------------------------
# نموذج رفع مستند واحد (DocumentForm) مع حقل caption
# ----------------------------
class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['doc_type', 'file', 'caption']
        widgets = {
            'doc_type': forms.Select(attrs={'class': 'form-select'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'caption': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اكتب وصفًا توضيحيًا للمستند (اختياري)'
            }),
        }


# ----------------------------
# InlineFormSet لربط مستندات الطالب (Document) بالطالب نفسه (Student)
# ----------------------------
DocumentFormSet = inlineformset_factory(
    Student,               # الموديل الأب
    Document,              # الموديل الابن
    form=DocumentForm,     # النموذج الذي صممناه أعلاه
    extra=3,               # عدد الحقول الفارغة لرفع مستندات جديدة
    can_delete=True        # إظهار checkbox لحذف المستندات الموجودة
)


class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = ["school_name", "logo"]
        widgets = {
            "school_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "اسم المدرسة"}),
        }

    def clean_logo(self):
        f = self.cleaned_data.get("logo")

        # حالة "Clear" أو عدم رفع ملف جديد: لا نعمل أي معالجة (يُترك للسيف/الدجانغو)
        if not f:
            return f

        # 1) تحقق صارم من كونها صورة سليمة ومحدودة الحجم/الأبعاد
        validate_image_strict(f)
        # 2) تعقيم وإعادة ترميز إلى PNG نظيفة
        cleaned = sanitize_and_reencode_to_png(f)
        # 3) إعادة تغليفها كملف مرفوع داخل الذاكرة باسم عشوائي
        safe_name = f"{uuid.uuid4().hex}.png"
        return InMemoryUploadedFile(
            file=cleaned,
            field_name="logo",
            name=safe_name,
            content_type="image/png",
            size=cleaned.size,
            charset=None
        )

    def save(self, commit=True):
        """
        يمنع إعادة الكتابة فوق نفس ملف الشعار عند عدم رفع ملف جديد
        (يحل WinError 32 على ويندوز عند حفظ بدون تغيير الشعار).
        """
        instance = super().save(commit=False)

        # إذا لم يُرفع شعار جديد ولم يتم اختيار "Clear" -> لا تغيّر الملف
        # ملاحظة: عند اختيار "Clear" سيكون 'logo' ضمن changed_data وقيمته False.
        if "logo" not in self.changed_data:
            if instance.pk:
                old_logo = (
                    SiteSettings.objects
                    .filter(pk=instance.pk)
                    .values_list("logo", flat=True)
                    .first()
                )
                # نعيد نفس الاسم بدون محاولة كتابة/استبدال الملف فعليًا
                instance.logo.name = old_logo

        if commit:
            instance.save()
        return instance
