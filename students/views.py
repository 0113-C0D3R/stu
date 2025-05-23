from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Student
from .forms import StudentForm
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator  # استيراد Paginator
from django.shortcuts import render, get_object_or_404  # استيراد get_object_or_404
from django.contrib import messages
from django.urls import reverse
from students.models import Student
from django.http import JsonResponse
from collections import Counter
from django_countries import countries


@login_required            # هذا يضمن إعادة التوجيه إلى صفحة /accounts/login/ إذا لم يكن المستخدم مسجّل دخول
def home(request):
    return render(request, 'students/home.html')

# صفحة إضافة طالب
@login_required
def add_student(request):
    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('student_list')
    else:
        form = StudentForm()
    
    return render(request, 'students/add_student.html', {'form': form})
    

# صفحة عرض الطلاب
@login_required
def student_list(request):
    query = request.GET.get('q')
    students = Student.objects.all()
    if query:
        students = students.filter(first_name__icontains=query)
    return render(request, 'students/student_list.html', {'students': students})



def student_detail(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    return render(request, 'students/student_detail.html', {'student': student})



# صفحة تعديل طالب
def student_edit(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            return redirect('student_detail', student_id=student.id)
    else:
        form = StudentForm(instance=student)

    return render(request, 'students/student_edit.html', {'form': form, 'student': student})


    

def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    student.delete()
    return redirect(reverse('student_list'))
    




class CustomLoginView(LoginView):
    template_name = 'students/login.html'


@login_required
# def get_statistics(request):
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


def to_passports(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    return render(request, 'students/passport_renewal.html', {'student': student})

