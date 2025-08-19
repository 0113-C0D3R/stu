from io import BytesIO
from PIL import Image, ImageOps
from django.core.files.base import ContentFile

def sanitize_and_reencode_to_png(file_obj):
    """
    يفتح الصورة، يزيل أي بيانات/ميتا، يصحح الدوران (EXIF)،
    ثم يعيد حفظها بصيغة PNG نظيفة.
    """
    file_obj.seek(0)
    img = Image.open(file_obj)

    # إزالة دوران EXIF إن وجد + تحويل إلى RGB (لو كانت P أو RGBA سيحفظها PNG جيدًا)
    img = ImageOps.exif_transpose(img)
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA")

    out = BytesIO()
    # optimize=True لتقليل الحجم قدر الإمكان
    img.save(out, format="PNG", optimize=True)
    out.seek(0)
    return ContentFile(out.read())
