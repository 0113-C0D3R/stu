import pytest
from students.models import Student

@pytest.mark.django_db
def test_student_str():
    s = Student(first_name='Aisha', last_name='Saleh')
    assert str(s) == 'Aisha Saleh'  # nosec B101
