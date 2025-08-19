from django.core.exceptions import ValidationError
from django.conf import settings
from PIL import Image

def validate_image_strict(image_file):
    """
    1) التحقق من الحجم.
    2) فتح الصورة بـ Pillow والتحقق من الصيغة الفعلية (وليس مجرد الامتداد).
    3) رفض الصور ذات عدد بيكسلات ضخم.
    """
    max_bytes = settings.SCHOOL_LOGO_MAX_MB * 1024 * 1024
    if image_file.size > max_bytes:
        raise ValidationError(f"حجم الشعار يجب ألا يتجاوز {settings.SCHOOL_LOGO_MAX_MB}MB.")

    try:
        img = Image.open(image_file)
        img.verify()  # يتحقق من سلامة بنية الصورة
    except Exception:
        raise ValidationError("الملف المرفوع ليس صورة صالحة.")

    # إعادة الفتح بعد verify (لأن verify تغلق الملف داخليًا)
    image_file.seek(0)
    img = Image.open(image_file)

    fmt = (img.format or "").upper()
    if fmt not in settings.SCHOOL_LOGO_ALLOWED_FORMATS:
        raise ValidationError("يُسمح فقط بصيغ: PNG / JPEG / WEBP.")

    w, h = img.size
    if w * h > settings.SCHOOL_LOGO_MAX_PIXELS:
        raise ValidationError("أبعاد الصورة كبيرة جدًا. يرجى تصغيرها قبل الرفع.")
