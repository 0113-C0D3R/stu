# students/views.py 
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render # <-- تم إضافة render هنا
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
from django.utils import timezone 

# from hijri_converter import hijri_converter # <-- السطر القديم
from hijri_converter.convert import Gregorian # <-- السطر الجديد والصحيح

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
        if 'document_formset' not in context:
            if self.request.POST:
                context['document_formset'] = DocumentFormSet(self.request.POST, self.request.FILES)
            else:
                context['document_formset'] = DocumentFormSet()
        return context

    def post(self, request, *args, **kwargs):
        """
        Override the post method to handle both the main form and the formset validation
        before saving anything to the database.
        """
        self.object = None
        form = self.get_form()
        formset = DocumentFormSet(request.POST, request.FILES)

        # Validate both the form and the formset
        if form.is_valid() and formset.is_valid():
            # If both are valid, call our custom form_valid
            return self.form_valid(form, formset)
        else:
            # If either is invalid, call our custom form_invalid
            return self.form_invalid(form, formset)

    def form_valid(self, form, formset):
        """
        This method is called only when both the form and formset are valid.
        We can now safely save everything to the database.
        """
        # Save the student object
        self.object = form.save()
        # Associate the formset with the saved student and save it
        formset.instance = self.object
        formset.save()
        
        messages.success(self.request, 'تم إضافة الطالب والمستندات بنجاح.')
        return redirect(self.get_success_url())

    def form_invalid(self, form, formset):
        """
        This method is called when either the form or formset is invalid.
        It re-renders the template with the forms and their errors without saving anything.
        """
        messages.error(self.request, 'يرجى تصحيح الأخطاء أدناه.')
        return self.render_to_response(
            self.get_context_data(form=form, document_formset=formset)
        )

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
    template_name = 'students/letters/transfer_residence_letter.html'

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


class GenerateMedicalCheckLetterView(LoginRequiredMixin, View): # <-- تمت إضافة LoginRequiredMixin
    """
    A flexible view to generate medical check request letters.
    - If a 'student_id' is passed via GET params, it generates a letter for that single student.
    - Otherwise, it displays a form to select multiple students.
    """
    selection_template = 'students/letters/select_students_for_letter.html'
    letter_template = 'students/letters/medical_check_letter.html'

    def get(self, request, *args, **kwargs):
        student_id = request.GET.get('student_id')

        # --- المنطق الجديد ---
        # إذا جاء الطلب مع ID لطالب محدد (من صفحة التفاصيل)
        if student_id:
            student = get_object_or_404(Student, pk=student_id)
            # استدعاء دالة مشتركة لتجهيز وعرض الخطاب
            return self.render_letter(request, [student])

        # --- المنطق القديم ---
        # إذا لم يكن هناك ID، نعرض صفحة اختيار الطلاب
        all_students = Student.objects.all().order_by('first_name', 'last_name')
        context = {
            'students': all_students,
            'page_title': 'اختيار طلاب لخطاب الفحص الطبي',
        }
        return render(request, self.selection_template, context)

    def post(self, request, *args, **kwargs):
        selected_student_ids = request.POST.getlist('student_ids')

        if not selected_student_ids:
            all_students = Student.objects.all().order_by('first_name', 'last_name')
            context = {
                'students': all_students,
                'page_title': 'اختيار طلاب لخطاب الفحص الطبي',
                'error': 'يرجى اختيار طالب واحد على الأقل.'
            }
            return render(request, self.selection_template, context)

        students_to_print = Student.objects.filter(id__in=selected_student_ids)
        # استدعاء دالة مشتركة لتجهيز وعرض الخطاب
        return self.render_letter(request, students_to_print)

    def render_letter(self, request, students_queryset):
        """
        A helper method to prepare context and render the letter template.
        This avoids code duplication between GET (for single student) and POST (for multiple).
        """
        try:
            correspondent = Correspondent.objects.get(category='lab')
        except Correspondent.DoesNotExist:
            correspondent = None

        director = ExecutiveDirector.objects.first()

        today_gregorian = timezone.now().date()
        today_hijri_obj = Gregorian(today_gregorian.year, today_gregorian.month, today_gregorian.day).to_hijri()
        
        context = {
            'students': students_queryset,
            'correspondent': correspondent,
            'today_gregorian': today_gregorian.strftime('%Y / %m / %d'),
            'today_hijri': f"{today_hijri_obj.year} / {today_hijri_obj.month} / {today_hijri_obj.day}",
            'page_title': 'خطاب طلب فحص طبي',
            
            # متغيرات المدير التنفيذي الجديدة
            'exec_name': director.name if director else '',
            'exec_title': director.title if director else '',
            'exec_institute': director.institute if director else '',
            'signature_url': director.signature.url if director and director.signature else None,
        }
        # --- نهاية التعديل ---
        
        return render(request, self.letter_template, context)