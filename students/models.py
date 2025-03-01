from django.db import models
from django.contrib.auth.models import AbstractUser
from django_countries.fields import CountryField



class Student(models.Model):
    # الحقول الحالية
    GENDER_CHOICES = [
        ('M', 'ذكر'),
        ('F', 'أنثى'),
    ]
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)

    def get_gender_display(self):
        return dict(self.GENDER_CHOICES).get(self.gender, self.gender)
        
    
    nationality = CountryField(verbose_name="الجنسية")  # استخدام CountryField

    MARITAL_STATUS_CHOICES = [
        ('single', 'أعزب'),
        ('married', 'متزوج'),
        ('divorced', 'مطلق'),
        ('widowed', 'أرمل'),
    ]

    first_name = models.CharField(max_length=100, verbose_name="الاسم الأول")
    last_name = models.CharField(max_length=100, verbose_name="اللقب")
    birth_date = models.DateField(verbose_name="تاريخ الميلاد")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="الجنس")

    image = models.ImageField(upload_to='students_images/', blank=True, null=True, verbose_name="صورة الطالب")
    
    nationality = CountryField(verbose_name="الجنسية") 
    job = models.CharField(max_length=100, verbose_name="الوظيفة", blank=True, null=True)
    marital_status = models.CharField(max_length=10, choices=MARITAL_STATUS_CHOICES, verbose_name="الحالة الاجتماعية")

    # Passport & Registration Information
    passport_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="رقم الجواز")
    registration_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="رقم التسجيل")
    place_of_issue = models.CharField(max_length=100, blank=True, null=True, verbose_name="مكان الإصدار")
    purpose = models.CharField(max_length=100, blank=True, null=True, verbose_name="الغرض")
    registration_place = models.CharField(max_length=100, blank=True, null=True, verbose_name="مكان التسجيل")
    visa_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="رقم التأشيرة")
    date_of_issued = models.DateField(blank=True, null=True, verbose_name="تاريخ الإصدار")
    port_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="اسم الميناء")
    date_of_registration = models.DateField(blank=True, null=True, verbose_name="تاريخ التسجيل")
    place_of_issued_residence = models.CharField(max_length=100, blank=True, null=True, verbose_name="مكان إصدار الإقامة")
    residence_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="رقم الإقامة")
    residence_issue_place = models.CharField(max_length=100, blank=True, null=True, verbose_name="مكان إصدار الإقامة")
    residence_issued_date = models.DateField(blank=True, null=True, verbose_name="تاريخ إصدار الإقامة")
    residence_end_date = models.DateField(blank=True, null=True, verbose_name="تاريخ انتهاء الإقامة")
    reference_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="الرقم المرجعي")

    # Entry & Exit Dates
    entry_date = models.DateField(blank=True, null=True, verbose_name="تاريخ الدخول")
    end_date = models.DateField(blank=True, null=True, verbose_name="تاريخ المغادرة")
    registration_date = models.DateField(blank=True, null=True, verbose_name="تاريخ التسجيل")
    end_registration_date = models.DateField(blank=True, null=True, verbose_name="تاريخ انتهاء التسجيل")

    # General Information
    type_of_services = models.CharField(max_length=100, blank=True, null=True, verbose_name="نوع الخدمات")
    issuing_authority = models.CharField(max_length=100, blank=True, null=True, verbose_name="الجهة المصدرة")
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="رقم الهاتف")

    # Companion Information
    companion_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="اسم المرافق")
    companion_nationality = models.CharField(max_length=100, blank=True, null=True, verbose_name="جنسية المرافق")
    companion_relationship = models.CharField(max_length=100, blank=True, null=True, verbose_name="صلة القرابة")
    companion_passport_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="رقم جواز المرافق")
    companion_residence_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="رقم إقامة المرافق")
    companion_residence_end_date = models.DateField(blank=True, null=True, verbose_name="تاريخ انتهاء إقامة المرافق")

    # Note
    note = models.TextField(blank=True, null=True, verbose_name="ملاحظة")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'مسؤول النظام'),
        ('editor', 'محرر'),
        ('viewer', 'متصفح'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='viewer')


    def is_admin(self):
        return self.role == 'admin'

    def is_editor(self):
        return self.role == 'editor'

    def is_viewer(self):
        return self.role == 'viewer'


