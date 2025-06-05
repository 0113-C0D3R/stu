from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from collections import Counter
from django_countries import countries

from .models import Student
from .forms import StudentForm, DocumentFormSet  # DocumentFormSet الآن يشمل حقل caption

@login_required
def home(request):
    return render(request, 'students/home.html')


# صفحة إضافة طالب مع دعم رفع مستندات
@login_required
def add_student(request):
    if request.method == "POST":
        student_form = StudentForm(request.POST, request.FILES)
        if student_form.is_valid():
            # حفظ بيانات الطالب أولاً للحصول على instance
            student = student_form.save(commit=False)
            student.save()

            # إنشاء formset لربط مستندات هذا الطالب
            document_formset = DocumentFormSet(request.POST, request.FILES, instance=student)
            if document_formset.is_valid():
                document_formset.save()
                messages.success(request, 'تم إضافة الطالب والمستندات بنجاح.')
                return redirect('student_list')
            else:
                # إذا فشل رفع المستندات، حذف الطالب لتفادي سجل ناقص
                student.delete()
                messages.error(request, 'حدث خطأ أثناء رفع المستندات. يرجى المحاولة مجددًا.')
        else:
            # إذا فشل نموذج الطالب، نعرض formset فارغ (لن يحفظ لأن student_form لم يُحفظ)
            document_formset = DocumentFormSet(request.POST, request.FILES)
    else:
        student_form = StudentForm()
        document_formset = DocumentFormSet()

    context = {
        'student_form': student_form,
        'document_formset': document_formset,
    }
    return render(request, 'students/add_student.html', context)


# صفحة عرض الطلاب
@login_required
def student_list(request):
    query = request.GET.get('q')
    students = Student.objects.all()
    if query:
        students = students.filter(first_name__icontains=query)
    return render(request, 'students/student_list.html', {'students': students})


# صفحة تفاصيل الطالب (هنا نعرض المستندات مع العنوان التوضيحي)
@login_required
def student_detail(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    return render(request, 'students/student_detail.html', {'student': student})


# صفحة تعديل طالب مع دعم تعديل/حذف/إضافة مستندات
@login_required
def student_edit(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    if request.method == "POST":
        student_form = StudentForm(request.POST, request.FILES, instance=student)
        document_formset = DocumentFormSet(request.POST, request.FILES, instance=student)

        if student_form.is_valid() and document_formset.is_valid():
            # حفظ بيانات الطالب أولًا
            student_form.save()
            # ثم حفظ المستندات (يتعامل مع الحذف والإضافة تلقائيًا)
            document_formset.save()
            messages.success(request, 'تم تحديث بيانات الطالب والمستندات بنجاح.')
            return redirect('student_detail', student_id=student.id)
    else:
        student_form = StudentForm(instance=student)
        document_formset = DocumentFormSet(instance=student)

    context = {
        'student_form': student_form,
        'document_formset': document_formset,
        'student': student,
    }
    return render(request, 'students/student_edit.html', context)


@login_required
def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    student.delete()
    return redirect(reverse('student_list'))


class CustomLoginView(LoginView):
    template_name = 'students/login.html'


@login_required
def get_statistics(request):
    # بيانات الجنس
    male_students = Student.objects.filter(gender='M').count()
    female_students = Student.objects.filter(gender='F').count()

    # بيانات الجنسية
    nationalities = Student.objects.values_list('nationality', flat=True)
    nationality_counts = Counter(nationalities)
    
    # تحويل رموز الدول إلى أسماء كاملة
    nationality_labels = [countries.name(code) for code in nationality_counts.keys()]
    nationality_counts = list(nationality_counts.values())

    data = {
        'male_students': male_students,
        'female_students': female_students,
        'nationality_labels': nationality_labels,
        'nationality_counts': nationality_counts,
    }

    return JsonResponse(data)


@login_required
def home_with_statistics(request):
    # بيانات الجنس
    male_students = Student.objects.filter(gender='M').count()
    female_students = Student.objects.filter(gender='F').count()

    # بيانات الجنسية
    nationalities = Student.objects.values_list('nationality', flat=True)
    nationality_counts = Counter(nationalities)
    
    # تحويل رموز الدول إلى أسماء كاملة
    nationality_labels = [countries.name(code) for code in nationality_counts.keys()]
    nationality_counts = list(nationality_counts.values())

    context = {
        'male_students': male_students,
        'female_students': female_students,
        'nationality_labels': nationality_labels,
        'nationality_counts': nationality_counts,
    }

    return render(request, 'students/home.html', context)


@login_required
def to_passports(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    return render(request, 'students/passport_renewal.html', {'student': student})