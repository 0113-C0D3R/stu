import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from students.forms import DocumentFormSet
from students.models import Student, Document

@pytest.mark.django_db
def test_document_formset_minimal():
    # 1. أنشئ طالبًا جديدًا
    student = Student.objects.create(
        first_name='Test', last_name='User',
        birth_date='1990-01-01', gender='F',
        nationality='US', job='', marital_status='single'
    )

    # 2. جهّز ملفًا وهميًا
    fake_file = SimpleUploadedFile(
        'test.txt', b'Hello world', content_type='text/plain'
    )

    # 3. احصل على prefix الـ formset (غالبًا 'documents')
    prefix = DocumentFormSet().prefix

    # 4. ضبط بيانات الإدارة لإرسال نموذج واحد فقط
    data = {
        f'{prefix}-TOTAL_FORMS': '1',
        f'{prefix}-INITIAL_FORMS': '0',
        f'{prefix}-MIN_NUM_FORMS': '0',
        f'{prefix}-MAX_NUM_FORMS': '1000',

        # بيانات النموذج الوحيد
        f'{prefix}-0-doc_type': 'passport',
        f'{prefix}-0-caption': 'Test Passport',
    }
    files = {
        f'{prefix}-0-file': fake_file
    }

    # 5. انشئ الـ formset وتحقق من صلاحيته
    formset = DocumentFormSet(data=data, files=files, instance=student)
    assert formset.is_valid(), f"Unexpected errors: {formset.errors}"

    # 6. احفظ وتأكد من إنشاء مستند واحد في DB
    instances = formset.save()
    assert len(instances) == 1
    doc = Document.objects.get(student=student)
    assert doc.caption == 'Test Passport'
