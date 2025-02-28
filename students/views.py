from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Student
from .forms import StudentForm
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator  # استيراد Paginator
from django.shortcuts import render, get_object_or_404  # استيراد get_object_or_404

# عرض نموذج تسجيل الدخول
def home(request):
    return render(request, 'students/home.html')

# صفحة إضافة طالب
@login_required
def add_student(request):
    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES)  # تأكد من تمرير request.FILES
        if form.is_valid():
            form.save()
            return redirect('student_list')  # إعادة التوجيه بعد الحفظ
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


class CustomLoginView(LoginView):
    template_name = 'students/login.html'




