# students/views.py (محوّل إلى Class-Based Views)
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
)
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib import messages
from collections import Counter
from django_countries import countries

from .models import Student, Correspondent, ExecutiveDirector
from .forms import StudentForm, DocumentFormSet

# صفحة رئيسية بسيطة
class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'students/home.html'

# إضافة طالب مع معالجة formset
class StudentCreateView(LoginRequiredMixin, CreateView):
    model = Student
    form_class = StudentForm
    template_name = 'students/add_student.html'
    success_url = reverse_lazy('students:student_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['document_formset'] = DocumentFormSet(self.request.POST, self.request.FILES)
        else:
            context['document_formset'] = DocumentFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        document_formset = context['document_formset']
        if form.is_valid() and document_formset.is_valid():
            self.object = form.save()
            document_formset.instance = self.object
            document_formset.save()
            messages.success(self.request, 'تم إضافة الطالب والمستندات بنجاح.')
            return redirect(self.get_success_url())
        return self.form_invalid(form)

# قائمة الطلاب
class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'students/student_list.html'
    context_object_name = 'students'

    def get_queryset(self):
        qs = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            qs = qs.filter(first_name__icontains=query)
        return qs

# تفاصيل الطالب
class StudentDetailView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = 'students/student_detail.html'
    pk_url_kwarg = 'student_id'
    context_object_name = 'student'

# تعديل بيانات الطالب
class StudentUpdateView(LoginRequiredMixin, UpdateView):
    model = Student
    form_class = StudentForm
    template_name = 'students/student_edit.html'
    pk_url_kwarg = 'student_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['document_formset'] = DocumentFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            context['document_formset'] = DocumentFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        document_formset = context['document_formset']
        if form.is_valid() and document_formset.is_valid():
            self.object = form.save()
            document_formset.save()
            messages.success(self.request, 'تم تحديث بيانات الطالب والمستندات بنجاح.')
            return redirect('students:student_detail', student_id=self.object.id)
        return self.form_invalid(form)

# حذف الطالب
class StudentDeleteView(LoginRequiredMixin, DeleteView):
    model = Student
    template_name = 'students/student_confirm_delete.html'
    pk_url_kwarg = 'student_id'
    success_url = reverse_lazy('students:student_list')

# تسجيل دخول مخصص
class CustomLoginView(LoginView):
    template_name = 'students/login.html'

# إحصائيات (JSON)
class StatisticsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        male = Student.objects.filter(gender='M').count()
        female = Student.objects.filter(gender='F').count()
        nationality_counts = Counter(Student.objects.values_list('nationality', flat=True))
        data = {
            'male_students': male,
            'female_students': female,
            'nationality_labels': [countries.name(code) for code in nationality_counts.keys()],
            'nationality_counts': list(nationality_counts.values()),
        }
        from django.http import JsonResponse
        return JsonResponse(data)

# صفحة رئيسية مع إحصائيات
class HomeWithStatsView(LoginRequiredMixin, TemplateView):
    template_name = 'students/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        male = Student.objects.filter(gender='M').count()
        female = Student.objects.filter(gender='F').count()
        nationality_counts = Counter(Student.objects.values_list('nationality', flat=True))
        ctx.update({
            'male_students': male,
            'female_students': female,
            'nationality_labels': [countries.name(code) for code in nationality_counts.keys()],
            'nationality_counts': list(nationality_counts.values()),
        })
        return ctx

# مثال على TemplateView لباقي الصفحات
class PassportRenewalView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = 'students/passport_renewal.html'
    pk_url_kwarg = 'student_id'
    context_object_name = 'student'

class TransferResidenceLetterView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = 'students.can_create_correspondence'
    template_name = 'students/transfer_residence_letter.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        student = get_object_or_404(Student, id=self.kwargs['student_id'])
        director = Correspondent.objects.filter(category='مدير الجوازات').first()
        exec_dir = ExecutiveDirector.objects.first()

        ctx.update({
            'student': student,
            'correspondent_name': getattr(director, 'name', ''),
            'correspondent_title': getattr(director, 'title', ''),
            'exec_name': getattr(exec_dir, 'name', ''),
            'exec_title': getattr(exec_dir, 'title', ''),
            'exec_institute': getattr(exec_dir, 'institute', ''),
            'signature_url': exec_dir.signature.url if exec_dir and exec_dir.signature else None,
            'old_passport': student.passport_number_old or '',
            'new_passport': student.passport_number or '',
            'subject': 'طلب نقل بيانات الإقامة',
        })
        return ctx
