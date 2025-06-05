from django import forms
from django.forms import inlineformset_factory
from .models import Student, Document
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = '__all__'
        widgets = {
            'birth_date': forms.DateInput(attrs={'class': 'form-control flatpickr'}),
            'date_of_issued': forms.DateInput(attrs={'class': 'form-control flatpickr'}),
            'date_of_registration': forms.DateInput(attrs={'class': 'form-control flatpickr'}),
            'residence_issued_date': forms.DateInput(attrs={'class': 'form-control flatpickr'}),
            'residence_end_date': forms.DateInput(attrs={'class': 'form-control flatpickr'}),
            'entry_date': forms.DateInput(attrs={'class': 'form-control flatpickr'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control flatpickr'}),
            'registration_date': forms.DateInput(attrs={'class': 'form-control flatpickr'}),
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