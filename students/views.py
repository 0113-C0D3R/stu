from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from collections import Counter
from django_countries import countries

from .models import Student, Correspondent, ExecutiveDirector  # تأكد من استيراد ExecutiveDirector
from .forms import StudentForm, DocumentFormSet

@login_required
def home(request):
    return render(request, 'students/home.html')

@login_required
def add_student(request):
    if request.method == "POST":
        student_form = StudentForm(request.POST, request.FILES)
        if student_form.is_valid():
            student = student_form.save()
            document_formset = DocumentFormSet(request.POST, request.FILES, instance=student)
            if document_formset.is_valid():
                document_formset.save()
                messages.success(request, 'تم إضافة الطالب والمستندات بنجاح.')
                return redirect('students:student_list')
            student.delete()
            messages.error(request, 'حدث خطأ أثناء رفع المستندات. يرجى المحاولة مجددًا.')
        else:
            document_formset = DocumentFormSet(request.POST, request.FILES)
    else:
        student_form = StudentForm()
        document_formset = DocumentFormSet()

    return render(request, 'students/add_student.html', {
        'student_form': student_form,
        'document_formset': document_formset,
    })

@login_required
def student_list(request):
    query = request.GET.get('q')
    students = Student.objects.all()
    if query:
        students = students.filter(first_name__icontains=query)
    return render(request, 'students/student_list.html', {'students': students})

@login_required
def student_detail(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    return render(request, 'students/student_detail.html', {'student': student})

@login_required
def student_edit(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == "POST":
        student_form = StudentForm(request.POST, request.FILES, instance=student)
        document_formset = DocumentFormSet(request.POST, request.FILES, instance=student)
        if student_form.is_valid() and document_formset.is_valid():
            student_form.save()
            document_formset.save()
            messages.success(request, 'تم تحديث بيانات الطالب والمستندات بنجاح.')
            return redirect('students:student_detail', student_id=student.id)
    else:
        student_form = StudentForm(instance=student)
        document_formset = DocumentFormSet(instance=student)

    return render(request, 'students/student_edit.html', {
        'student_form': student_form,
        'document_formset': document_formset,
        'student': student,
    })

@login_required
def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    student.delete()
    return redirect('students:student_list')

class CustomLoginView(LoginView):
    template_name = 'students/login.html'

@login_required
def get_statistics(request):
    male_students = Student.objects.filter(gender='M').count()
    female_students = Student.objects.filter(gender='F').count()
    nationalities = Student.objects.values_list('nationality', flat=True)
    nationality_counts = Counter(nationalities)
    nationality_labels = [countries.name(code) for code in nationality_counts.keys()]
    nationality_values = list(nationality_counts.values())

    from django.http import JsonResponse
    data = {
        'male_students': male_students,
        'female_students': female_students,
        'nationality_labels': nationality_labels,
        'nationality_counts': nationality_values,
    }
    return JsonResponse(data)

@login_required
def home_with_statistics(request):
    male_students = Student.objects.filter(gender='M').count()
    female_students = Student.objects.filter(gender='F').count()
    nationalities = Student.objects.values_list('nationality', flat=True)
    nationality_counts = Counter(nationalities)
    nationality_labels = [countries.name(code) for code in nationality_counts.keys()]
    nationality_values = list(nationality_counts.values())

    context = {
        'male_students': male_students,
        'female_students': female_students,
        'nationality_labels': nationality_labels,
        'nationality_counts': nationality_values,
    }
    return render(request, 'students/home.html', context)

@login_required
def to_passports(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    return render(request, 'students/passport_renewal.html', {'student': student})

@login_required
@permission_required('students.can_create_correspondence', raise_exception=True)
def transfer_residence_letter(request, student_id):
    student = get_object_or_404(Student, pk=student_id)

    # جلب بيانات مدير الجوازات
    try:
        director = Correspondent.objects.get(category='مدير الجوازات')
        correspondent_name = director.name
        correspondent_title = director.title
    except Correspondent.DoesNotExist:
        correspondent_name = ''
        correspondent_title = ''

    # جلب بيانات المدير التنفيذي من نموذج ExecutiveDirector
    exec_dir = ExecutiveDirector.objects.first()
    if exec_dir and exec_dir.signature:
        signature_url = exec_dir.signature.url
        exec_name = exec_dir.name
        exec_title = exec_dir.title
        exec_institute = exec_dir.institute
    else:
        signature_url = None
        exec_name = ''
        exec_title = ''
        exec_institute = ''


    subject_text = 'طلب نقل بيانات الإقامة'
    old_passport = student.passport_number_old or ''
    new_passport = student.passport_number or ''

    if request.method == 'POST':
        messages.success(request, 'تم حفظ المراسلة بنجاح.')
        return redirect('students:student_detail', student_id=student.id)

    context = {
        'student': student,
        'correspondent_name': correspondent_name,
        'correspondent_title': correspondent_title,
        'exec_name': exec_name,
        'exec_title': exec_title,
        'exec_institute': exec_institute,
        'signature_url': signature_url,
        'subject': subject_text,
        'old_passport': old_passport,
        'new_passport': new_passport,
    }
    return render(request, 'students/transfer_residence_letter.html', context)

