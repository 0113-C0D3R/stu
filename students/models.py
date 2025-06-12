from django.db import models
from django.contrib.auth.models import AbstractUser
from django_countries.fields import CountryField

class Student(models.Model):

    GENDER_CHOICES = [
        ('M', 'ذكر'),
        ('F', 'أنثى'),
    ]
    nationality = CountryField(verbose_name="الجنسية")

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
    # ملاحظة: لديك حقول مكررة مثل image و nationality و note، قمت بإبقائها كما هي لتجنب أي مشاكل
    # ولكن من الأفضل تنظيفها وإزالة المكرر منها في المستقبل.
    
    nationality = CountryField(verbose_name="الجنسية")
    job = models.CharField(max_length=100, verbose_name="الوظيفة", blank=True, null=True)
    marital_status = models.CharField(max_length=10, choices=MARITAL_STATUS_CHOICES, verbose_name="الحالة الاجتماعية")

    # Passport & Registration Information
    passport_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="رقم الجواز")
    registration_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="رقم التسجيل")
    place_of_issue = models.CharField(max_length=100, blank=True, null=True, verbose_name="مكان الإصدار")
    passport_number_old = models.CharField(max_length=50, blank=True, null=True)
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

    # --- نهاية الحقول ---

    # === أفضل الممارسات: إضافة الخصائص هنا ===
    @property
    def full_name(self):
        """Returns the student's full name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def possessive_pronoun(self):
        """
        Returns the appropriate possessive pronoun based on gender.
        'ه' for Male ('M'), 'ها' for Female ('F').
        """
        if self.gender == 'M':
            return 'ه'
        return 'ها'
    # === نهاية الإضافات ===

    def __str__(self):
        return self.full_name  # تحديث لاستخدام الخاصية الجديدة

    class Meta:
        verbose_name        = "الطالب"
        verbose_name_plural = "الطلاب"
        permissions = [
            ("can_create_correspondence", "Can create correspondence/letters"),
        ]

    note = models.TextField(blank=True, null=True, verbose_name="ملاحظة")

# ----------------------------
# إضافة موديل Document أسفل Student
# ----------------------------
class Document(models.Model):
    DOC_TYPES = [
        ('passport', 'جواز سفر'),
        ('residence', 'إقامة'),
        ('id_card', 'هوية شخصية'),
        ('other', 'أخرى'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name="الطالب"
    )
    doc_type = models.CharField(
        max_length=20,
        choices=DOC_TYPES,
        default='other',
        verbose_name="نوع المستند"
    )
    file = models.FileField(
        upload_to='student_docs/%Y/%m/',
        verbose_name="الملف"
    )
    caption = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="الوصف التوضيحي"
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاريخ الرفع"
    )

    def __str__(self):
        return f"{self.student.first_name} {self.student.last_name} – {self.get_doc_type_display()}"
        


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

    

class Correspondent(models.Model):
    category = models.CharField(max_length=50, unique=True)
    name     = models.CharField(max_length=100)
    title    = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.name} ({self.category})"

    class Meta:
        verbose_name        = "الاسم"
        verbose_name_plural = "إدارة التوجيهات والمراسلات"



# *** نموذج جديد خاص بالمدير التنفيذي و التوقيع ***
class ExecutiveDirector(models.Model):
    name      = models.CharField(max_length=100, verbose_name="اسم المدير التنفيذي")
    title     = models.CharField(max_length=100, blank=True, verbose_name="المنصب الوظيفي")
    institute     = models.CharField(max_length=100, blank=True, verbose_name="اسم المعهد")
    signature = models.ImageField(
        upload_to='signatures/',
        blank=True,
        null=True,
        verbose_name="توقيع المدير التنفيذي"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "المدير التنفيذي"
        verbose_name_plural = "بيانات المدير التنفيذي"

    
