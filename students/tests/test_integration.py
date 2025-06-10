# students/tests/test_integration.py

import pytest
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from students.models import Student, Document

@pytest.mark.django_db
def test_full_student_crud_flow(authenticated_client):
    # 1. إنشاء طالب جديد مع مستند
    create_url = reverse("students:student_create")
    upload = SimpleUploadedFile("file.pdf", b"dummy", content_type="application/pdf")
    data_create = {
        "first_name": "Lina",
        "last_name": "Yasser",
        "birth_date": "2000-01-01",
        "gender": "F",
        "nationality": "US",
        "marital_status": "single",
        "documents-0-doc_type": "passport",
        "documents-0-file": upload,
        "documents-0-caption": "",
        "documents-TOTAL_FORMS": "1",
        "documents-INITIAL_FORMS": "0",
    }
    response_create = authenticated_client.post(create_url, data_create, format="multipart")
    # ✅ FIX: Added nosec comment
    assert response_create.status_code == 302, "فشل إنشاء الطالب، تحقق من صلاحية النموذج"  # nosec B101

    # التحقق من إنشاء الطالب والمستند
    student = Student.objects.get(first_name="Lina", last_name="Yasser")
    assert Document.objects.filter(student=student).exists()  # nosec B101
    doc = Document.objects.get(student=student)

    # 2. استعراض التفاصيل
    # ✅  التصحيح: استخدام student_id بدلاً من pk
    detail_url = reverse("students:student_detail", kwargs={"student_id": student.id})
    response_detail = authenticated_client.get(detail_url)
    assert response_detail.status_code == 200  # nosec B101
    assert "Lina" in response_detail.content.decode()  # nosec B101

    # 3. تعديل الطالب
    # ✅  التصحيح: استخدام student_id بدلاً من pk
    update_url = reverse("students:student_update", kwargs={"student_id": student.id})
    data_update = {
        "first_name": "LinaUpdated",
        "last_name": student.last_name,
        "birth_date": student.birth_date.strftime("%Y-%m-%d"),
        "gender": student.gender,
        "nationality": student.nationality,
        "marital_status": student.marital_status,
        "documents-TOTAL_FORMS": "1",
        "documents-INITIAL_FORMS": "1",
        "documents-0-id": doc.id,
        "documents-0-student": student.id,
        "documents-0-doc_type": doc.doc_type,
        "documents-0-caption": "Updated Caption",
    }
    response_update = authenticated_client.post(update_url, data_update)
    # ✅ FIX: Corrected variable to response_update and added nosec comment
    assert response_update.status_code == 302, "فشل تحديث الطالب، تحقق من صلاحية النموذج"  # nosec B101
    student.refresh_from_db()
    # ✅ FIX: Added nosec comment
    assert student.first_name == "LinaUpdated"  # nosec B101

    # 4. حذف الطالب
    # ✅  التصحيح: استخدام student_id بدلاً من pk
    delete_url = reverse("students:student_delete", kwargs={"student_id": student.id})
    response_delete = authenticated_client.post(delete_url)
    # ✅ FIX: Added nosec comment
    assert response_delete.status_code == 302  # nosec B101
    with pytest.raises(Student.DoesNotExist):
        Student.objects.get(id=student.id)