from django.db import models, transaction   
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django_countries.fields import CountryField
# ===== Site Settings (School Logo) =====
import uuid
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver

class Student(models.Model):
    # ← 4 مسافات هنا
    first_name = models.CharField(max_length=50)
    last_name  = models.CharField(max_length=50)

    reference_number = models.CharField(
        "الرقم المرجعي",
        max_length=5,
        editable=False,
        null=True,       # مؤقّتًا
        unique=False,    # مؤقّتًا
    )

    reference_number_int = models.PositiveIntegerField(
        null=True,       # مؤقّتًا
        editable=False,
    )

    def save(self, *args, **kwargs):
        from django.db import transaction
        if not self.reference_number:
            with transaction.atomic():
                last = (
                    Student.objects
                    .order_by("-reference_number_int")
                    .values_list("reference_number_int", flat=True)
                    .first()
                ) or 0
                nxt = last + 1
                self.reference_number_int = nxt
                self.reference_number     = f"{nxt:05d}"
        super().save(*args, **kwargs)

    

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
    middle_name = models.CharField("الاسم الأوسط", max_length=50, blank=True)
    last_name = models.CharField(max_length=100, verbose_name="اللقب")
    birth_date  = models.DateField("تاريخ الميلاد", null=True, blank=True)
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
    passport_number_old = models.CharField(max_length=50, blank=True, null=True, verbose_name="رقم الجواز القديم")
    passport_expiry = models.DateField(blank=True, null=True, verbose_name="تاريخ انتهاء الجواز")
    purpose = models.CharField(max_length=100, blank=True, null=True, verbose_name="الغرض")
    registration_place = models.CharField(max_length=100, blank=True, null=True, verbose_name="مكان التسجيل")
    visa_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="رقم التأشيرة")
    date_of_issued = models.DateField(blank=True, null=True, verbose_name="تاريخ اصدار الجواز")
    port_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="اسم الميناء")
    date_of_registration = models.DateField(blank=True, null=True, verbose_name="تاريخ التسجيل")
    place_of_issued_residence = models.CharField(max_length=100, blank=True, null=True, verbose_name="مكان إصدار الإقامة")
    residence_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="رقم الإقامة")
    residence_issue_place = models.CharField(max_length=100, blank=True, null=True, verbose_name="مكان إصدار الإقامة")
    residence_issued_date = models.DateField(blank=True, null=True, verbose_name="تاريخ إصدار الإقامة")
    residence_end_date = models.DateField(blank=True, null=True, verbose_name="تاريخ انتهاء الإقامة")

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

    
class GeneratedLetter(models.Model):
    """
    نموذج لتسجيل كل خطاب يتم إنشاؤه في النظام.
    """
    reference_number = models.CharField(max_length=50, unique=True, verbose_name="الرقم المرجعي")
    letter_type = models.CharField(max_length=50, verbose_name="نوع الخطاب")
    students = models.ManyToManyField(Student, verbose_name="الطلاب")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        verbose_name="تم إنشاؤه بواسطة"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    class Meta:
        verbose_name = "خطاب مُنشأ"
        verbose_name_plural = "الخطابات المُنشأة"
        ordering = ['-created_at']

    def __str__(self):
        return self.reference_number


class ReferenceCounter(models.Model):
    """
    نموذج لحفظ آخر رقم تسلسلي لكل نوع من الخطابات لضمان عدم التكرار.
    """
    letter_type_code = models.CharField(max_length=20, unique=True, verbose_name="رمز نوع الخطاب")
    last_sequence = models.PositiveIntegerField(default=0, verbose_name="آخر رقم تسلسلي")

    class Meta:
        verbose_name = "عدّاد أرقام مرجعية"
        verbose_name_plural = "عدّادات الأرقام المرجعية"

    def __str__(self):
        return f"عدّاد {self.letter_type_code}: {self.last_sequence}"



def school_logo_path(instance, filename):
    # اسم عشوائي بامتداد PNG (نحن سنعيد ترميز الصورة في الفورم لضمان الأمان)
    return f"school/logo/{uuid.uuid4().hex}.png"

class SiteSettings(models.Model):
    school_name = models.CharField("اسم المدرسة", max_length=255, blank=True)
    logo = models.ImageField("شعار المدرسة", upload_to=school_logo_path, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "إعدادات الموقع"
        verbose_name_plural = "إعدادات الموقع"

    def __str__(self):
        return self.school_name or "إعدادات الموقع"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

# حذف الملف القديم عند تغيير الشعار لتفادي التراكم
@receiver(pre_save, sender=SiteSettings)
def auto_delete_old_logo_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return
    old_file = getattr(old, "logo", None)
    new_file = getattr(instance, "logo", None)
    if old_file and new_file and old_file.name != new_file.name:
        old_file.storage.delete(old_file.name)

# حذف الملف من القرص عند حذف السجل
@receiver(post_delete, sender=SiteSettings)
def auto_delete_logo_on_delete(sender, instance, **kwargs):
    if instance.logo:
        instance.logo.storage.delete(instance.logo.name)
