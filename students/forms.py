from django import forms
from .models import Student
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = '__all__'
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'date_of_issued': forms.DateInput(attrs={'type': 'date'}),
            'date_of_registration': forms.DateInput(attrs={'type': 'date'}),
            'residence_issued_date': forms.DateInput(attrs={'type': 'date'}),
            'residence_end_date': forms.DateInput(attrs={'type': 'date'}),
            'entry_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'registration_date': forms.DateInput(attrs={'type': 'date'}),
            'end_registration_date': forms.DateInput(attrs={'type': 'date'}),
            'companion_residence_end_date': forms.DateInput(attrs={'type': 'date'}),

            'birth_date': forms.DateInput(attrs={'class': 'form-control flatpickr'}),  # إضافة class لتفعيل Flatpickr
            'date_of_issued': forms.DateInput(attrs={'class': 'form-control flatpickr'}),  # إضافة class لتفعيل Flatpick
            'date_of_registration': forms.DateInput(attrs={'class': 'form-control flatpickr'}),  # إضافة class لتفعيل Flatpickr
            'residence_issued_date': forms.DateInput(attrs={'class': 'form-control flatpickr'}),  # إضافة class لتفعيل Flatpickr
            'residence_end_date': forms.DateInput(attrs={'class': 'form-control flatpickr'}),  # إضافة class لتفعيل Flatpickr
            'entry_date': forms.DateInput(attrs={'class': 'form-control flatpickr'}),  # إضافة class لتفعيل Flatpickr
            'end_date': forms.DateInput(attrs={'class': 'form-control flatpickr'}),  # إضافة class لتفعيل Flatpickr
            'registration_date': forms.DateInput(attrs={'class': 'form-control flatpickr'}),  # إضافة class لتفعيل Flatpickr
            'end_registration_date': forms.DateInput(attrs={'class': 'form-control flatpickr'}),  # إضافة class لتفعيل Flatpickr
            'companion_residence_end_date': forms.DateInput(attrs={'class': 'form-control flatpickr'}),  # إضافة class لتفعيل Flatpickr


            'nationality': forms.Select(attrs={'class': 'form-control'}),  # قائمة منسدلة للجنسية
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'حفظ الطالب', css_class='btn btn-primary'))




