# students/tests/test_views.py

import pytest
from django.urls import reverse
from students.models import Student, Document
from django.core.files.uploadedfile import SimpleUploadedFile

@pytest.mark.django_db
class TestStudentViews:

    def test_student_list_view(self, authenticated_client):
        url = reverse("students:student_list")
        response = authenticated_client.get(url)
        assert response.status_code == 200

    def test_student_create_view_and_redirect(self, authenticated_client):
        url = reverse("students:student_create")
        data = {
            "first_name": "Test",
            "last_name": "User",
            "birth_date": "2000-01-01",
            "gender": "M",
            "nationality": "US",
            "marital_status": "single",
            "documents-TOTAL_FORMS": "0",
            "documents-INITIAL_FORMS": "0",
        }
        response = authenticated_client.post(url, data)
        assert response.status_code == 302, "فشل إعادة التوجيه، تحقق من صلاحية النموذج"
        assert Student.objects.filter(first_name="Test", last_name="User").exists()

    def test_student_update_view_and_redirect(self, authenticated_client):
        student = Student.objects.create(
            first_name="A",
            last_name="B",
            birth_date="2000-01-01",
            gender="M",
            nationality="US",
            marital_status="single",
        )
        # ✅  التصحيح: استخدام student_id بدلاً من pk
        url = reverse("students:student_update", kwargs={"student_id": student.id})
        data = {
            "first_name": "A2",
            "last_name": student.last_name,
            "birth_date": "2000-01-01",
            "gender": student.gender,
            "nationality": student.nationality,
            "marital_status": student.marital_status,
            "documents-TOTAL_FORMS": "0",
            "documents-INITIAL_FORMS": "0",
        }
        response = authenticated_client.post(url, data)
        assert response.status_code == 302, "فشل إعادة التوجيه، تحقق من صلاحية النموذج"
        student.refresh_from_db()
        assert student.first_name == "A2"

    def test_student_delete_view(self, authenticated_client):
        student = Student.objects.create(
            first_name="X",
            last_name="Y",
            birth_date="2000-01-01",
            gender="F",
            nationality="US",
            marital_status="single",
        )
        # ✅  التصحيح: استخدام student_id بدلاً من pk
        url = reverse("students:student_delete", kwargs={"student_id": student.id})
        response = authenticated_client.post(url)
        assert response.status_code == 302
        with pytest.raises(Student.DoesNotExist):
            Student.objects.get(id=student.id)

    def test_document_upload_in_create(self, authenticated_client):
        url = reverse("students:student_create")
        upload = SimpleUploadedFile("doc.pdf", b"content", content_type="application/pdf")
        data = {
            "first_name": "Sara",
            "last_name": "Ahmed",
            "birth_date": "2000-01-01",
            "gender": "F",
            "nationality": "US",
            "marital_status": "single",
            "documents-0-doc_type": "passport",
            "documents-0-file": upload,
            "documents-0-caption": "Test Caption",
            "documents-TOTAL_FORMS": "1",
            "documents-INITIAL_FORMS": "0",
        }
        response = authenticated_client.post(url, data, format="multipart")
        assert response.status_code == 302, "فشل إعادة التوجيه، تحقق من صلاحية النموذج والمستند"
        student = Student.objects.get(first_name="Sara", last_name="Ahmed")
        assert Document.objects.filter(student=student).exists()