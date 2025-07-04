# students/views.py (النسخة النهائية المصححة)

from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
)
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from collections import Counter
from django_countries import countries
from django.utils import timezone
from hijri_converter.convert import Gregorian
from django.db import transaction
from datetime import datetime
from .models import Student, Correspondent, ExecutiveDirector, GeneratedLetter, ReferenceCounter
from .forms import StudentForm, DocumentFormSet
from django.urls import reverse

# ==============================================================================
#                                CORE VIEWS
# ==============================================================================

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'students/home.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        male_students = Student.objects.filter(gender='M').count()
        female_students = Student.objects.filter(gender='F').count()
        nationality_counts = Counter(Student.objects.values_list('nationality', flat=True))
        context['male_students'] = male_students
        context['female_students'] = female_students
        context['nationality_labels'] = [countries.name(code) for code in nationality_counts.keys() if code]
        context['nationality_counts'] = list(nationality_counts.values())
        context['page_title'] = 'لوحة التحكم الرئيسية'
        return context


class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'students/student_list.html'
    context_object_name = 'students'
    paginate_by = 15
    def get_queryset(self):
        qs = super().get_queryset().order_by('first_name', 'last_name')
        query = self.request.GET.get('q')
        if query:
            from django.db.models import Q
            qs = qs.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(passport_number__icontains=query)
            )
        return qs


class StudentDetailView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = 'students/student_detail.html'
    pk_url_kwarg = 'student_id'
    context_object_name = 'student'


class StudentCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'students.add_student'
    model = Student
    form_class = StudentForm
    template_name = 'students/add_student.html'
    success_url = reverse_lazy('students:student_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'document_formset' not in context:
            context['document_formset'] = DocumentFormSet(self.request.POST or None, self.request.FILES or None)
        return context
    def form_valid(self, form, formset):
        self.object = form.save()
        formset.instance = self.object
        formset.save()
        messages.success(self.request, f"تم إضافة الطالب '{self.object.full_name}' بنجاح.")
        return redirect(self.get_success_url())
    def form_invalid(self, form, formset):
        messages.error(self.request, 'يرجى تصحيح الأخطاء أدناه.')
        return self.render_to_response(self.get_context_data(form=form, document_formset=formset))


class StudentUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'students.change_student'
    model = Student
    form_class = StudentForm
    template_name = 'students/student_edit.html'
    pk_url_kwarg = 'student_id'
    def get_success_url(self):
        return reverse_lazy('students:student_detail', kwargs={'student_id': self.object.id})
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'document_formset' not in context:
            context['document_formset'] = DocumentFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object)
        return context
    def form_valid(self, form, formset):
        form.save()
        formset.save()
        messages.success(self.request, f"تم تحديث بيانات الطالب '{self.object.full_name}' بنجاح.")
        return redirect(self.get_success_url())
    def form_invalid(self, form, formset):
        messages.error(self.request, 'يرجى تصحيح الأخطاء أدناه.')
        return self.render_to_response(self.get_context_data(form=form, document_formset=formset))


class StudentDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'students.delete_student'
    model = Student
    template_name = 'students/student_confirm_delete.html'
    pk_url_kwarg = 'student_id'
    success_url = reverse_lazy('students:student_list')
    def form_valid(self, form):
        messages.success(self.request, f"تم حذف الطالب '{self.object.full_name}' بنجاح.")
        return super().form_valid(form)


# ==============================================================================
#                        LETTER GENERATION VIEWS
# ==============================================================================

class BaseLetterView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'students.can_create_correspondence'
    selection_template_name = 'students/letters/select_students_for_letter.html'
    letter_template_name = ''
    letter_type_code = ''

    def get(self, request, *args, **kwargs):
        student_id = request.GET.get('student_id')
        if student_id:
            student_queryset = Student.objects.filter(pk=student_id)
            if not student_queryset.exists():
                raise Http404("No Student found matching the query.")
            return self.render_letter(request, student_queryset)

        all_students = Student.objects.all().order_by('first_name', 'last_name')
        context = {
            'students': all_students,
            'page_title': 'اختيار طلاب لإنشاء خطاب',
            'view': self
        }
        return render(request, self.selection_template_name, context)

    def post(self, request, *args, **kwargs):
        selected_student_ids = request.POST.getlist('student_ids')
        if not selected_student_ids:
            messages.error(request, 'لم تقم باختيار أي طالب.')
            return redirect(request.path_info)
        students_to_print = Student.objects.filter(id__in=selected_student_ids)
        return self.render_letter(request, students_to_print)

    def get_letter_context(self, request, students_queryset):
        # تم إضافة request هنا
        raise NotImplementedError("Subclasses must implement get_letter_context.")

    def render_letter(self, request, students_queryset):
        try:
            with transaction.atomic():
                counter, created = ReferenceCounter.objects.select_for_update().get_or_create(letter_type_code=self.letter_type_code)
                counter.last_sequence += 1
                counter.save()
                year_short = str(timezone.now().year)[-2:]
                sequence_str = str(counter.last_sequence).zfill(3)
                new_ref_number = f"{self.letter_type_code}-{year_short}-{sequence_str}"
        except Exception as e:
            messages.error(request, f"فشل إنشاء الرقم المرجعي: {e}")
            return redirect(request.path_info)

        exec_dir = ExecutiveDirector.objects.first()
        today = timezone.now().date()
        hijri_today = Gregorian(today.year, today.month, today.day).to_hijri()

        context = {
            'students': students_queryset,
            'gregorian_date': today.strftime('%Y/%m/%d'),
            'hijri_date': f"{hijri_today.year}/{hijri_today.month:02d}/{hijri_today.day:02d}",
            'exec_name': getattr(exec_dir, 'name', ''),
            'exec_title': getattr(exec_dir, 'title', ''),
            'exec_institute': getattr(exec_dir, 'institute', ''),
            'signature_url': exec_dir.signature.url if exec_dir and exec_dir.signature else None,
            'reference_number': new_ref_number,
        }
        
        # --- هذا هو السطر الذي تم تصحيحه ---
        letter_specific_context = self.get_letter_context(request, students_queryset)
        context.update(letter_specific_context)

        new_letter_record = GeneratedLetter.objects.create(
            reference_number=new_ref_number,
            letter_type=letter_specific_context.get('subject', 'غير محدد'),
            created_by=request.user
        )
        new_letter_record.students.set(students_queryset)
        return render(request, self.letter_template_name, context)


class GenerateMedicalCheckLetterView(BaseLetterView):
    """Generates the letter for medical check-ups."""
    letter_template_name = 'students/letters/medical_check_letter.html'
    letter_type_code = 'MED'
    page_title = 'إنشاء خطاب فحص طبي'

    def get_letter_context(self, request, students_queryset):
        correspondent = Correspondent.objects.filter(category='المختبر الوطني').first()

        # منطق تحديد النص بناءً على عدد الطلاب وجنسهم
        if students_queryset.count() == 1:
            student = students_queryset.first()
            word = "الأخ" if student and student.gender == 'M' else "الأخت"
            gender_specific_phrase = f"لـ {word} الموضحة بياناته أدناه"
        else:
            gender_specific_phrase = "للإخوة الموضحة أسمائهم في الجدول أدناه"
        
        body_text = (
            "بالإشارة إلى الموضوع أعلاه، "
            f"نرجو تكرمكم بعمل فحص طبي {gender_specific_phrase} لترتيب إقامة الدراسة لدينا بالمركز."
        )

        context = {
            'subject': 'الموضوع: طلب فحص طبي',
            'body_text': body_text,
            'correspondent': correspondent,
        }

        # --- هذا هو المنطق الجديد لتحديد سلوك ما بعد الطباعة ---
        # إذا كان الطلب فرديًا (GET)، أرسل إشارة الإغلاق
        if request.method == 'GET':
            context['post_print_action'] = 'close'
        # إذا كان الطلب جماعيًا (POST)، لن يتم إرسال الإشارة، وسيتم تنفيذ قسم else في القالب
        
        return context


class GenerateExitReentryVisaLetterView(BaseLetterView):
    """Generates the letter for exit/re-entry visa requests."""
    letter_template_name = 'students/letters/exit_reentry_visa_letter.html'
    letter_type_code = 'V'

    def get_letter_context(self, request, students_queryset):
        correspondent = Correspondent.objects.filter(category='مدير الجوازات').first()
        student = students_queryset.first()

        # --- هذا هو التعديل الجديد لتحديد النص بناءً على الجنس ---
        if student and student.gender == 'M':
            # في حالة المذكر
            gender_specific_phrase = "الأخ الموضح بياناته في الجدول أدناه يريد"
        else:
            # في حالة المؤنث (أو كقيمة افتراضية)
            gender_specific_phrase = "الأخت الموضحة بياناتها في الجدول أدناه تريد"
        # --- نهاية التعديل ---

        # الآن نستخدم المتغير الجديد في بناء نص الخطاب
        body_text = (
            "يهديكم مركز الفخرية للدراسات الشرعية أطيب التحايا متمنيين لكم دوام التوفيق والنجاح في مهامكم.. "
            f"وبالإشارة إلى الموضوع أعلاه نود إفادتكم بأن {gender_specific_phrase} تأشيرة خروج وعودة فنرجو منكم التعاون في منح التأشيرة وتسهيل اجراءاتها."
        )

        return {
            'subject': 'الموضوع: طلب تأشيرة خروج وعودة',
            'body_text': body_text,
            'correspondent': correspondent,
        }


class GenerateResidenceRenewalLetterView(BaseLetterView):
    """Generates the letter for residence renewal requests."""
    letter_template_name = 'students/letters/residence_renewal_letter.html'
    letter_type_code = 'REV' # رمز مختصر لـ Residence

    def get_letter_context(self, request, students_queryset):
        # نفترض أن المخاطب هو نفسه مدير الجوازات
        correspondent = Correspondent.objects.filter(category='مدير الجوازات').first()
        student = students_queryset.first()

        # --- التعديل الجديد: تحديد متغيرين للنص بناءً على الجنس ---
        if student and student.gender == 'M':
            # في حالة المذكر
            subject_phrase = "الأخ المذكور بياناته"
            pronoun_phrase = "مزاولته"  # ضمير المذكر
        else:
            # في حالة المؤنث (أو كقيمة افتراضية)
            subject_phrase = "الأخت المذكورة بياناتها"
            pronoun_phrase = "مزاولتها"  # ضمير المؤنث
        # --- نهاية التعديل ---

        # الآن نستخدم كلا المتغيرين في بناء نص الخطاب
        body_text = (
            "يهديكم مركز الفخرية للدراسات الشرعية أطيب التحايا متمنين لكم دوام التوفيق والنجاح في مهامكم.. "
            f"واشارة إلى الموضوع أعلاه، نرجو تكرمكم بتجديد إقامة {subject_phrase} أدناه لغرض الدراسة لدينا "
            "بالمركز، "
            f"ونتعهد أمامكم بعدم {pronoun_phrase} أي عمل، وفي حالة المخالفة لذلك نكون عرضة للإجراءات "
            "القانونية التي تتخذ من قبلكم ونتحمل نفقة ترحيله ودفع الغرامات القانونية."
        )

        return {
            'subject': 'الموضوع: طلب تجديد إقامة',
            'body_text': body_text,
            'correspondent': correspondent,
        }


class TransferResidenceLetterView(BaseLetterView):
    """Generates the letter for transferring residence data."""
    letter_template_name = 'students/letters/transfer_residence_letter.html'
    letter_type_code = 'TRA' # رمز لـ Transfer

    def get_letter_context(self, request, students_queryset):
        correspondent = Correspondent.objects.filter(category='مدير الجوازات').first()
        student = students_queryset.first()

        # --- هذا هو التعديل الجديد لتطبيق النص المطلوب ---

        # 1. تحديد الضمير الصحيح (جوازه / جوازها)
        if student and student.gender == 'M':
            possessive_pronoun = "جوازه"
        else:
            possessive_pronoun = "جوازها"

        # 2. الحصول على البيانات المطلوبة من نموذج الطالب
        student_name = student.full_name if student else "[اسم الطالب]"
        old_passport = student.passport_number_old or "[رقم الجواز القديم]"
        new_passport = student.passport_number or "[رقم الجواز الجديد]"

        # 3. بناء النص الكامل باستخدام البيانات
        greeting = "يهديكم مركز الفخرية للدراسات الشرعية أطيب التحايا متمنيين لكم دوام التوفيق والنجاح في مهامكم.."
        main_request = (
            "وبالإشارة إلى الموضوع أعلاه، نرجو تكرمكم بنقل بيانات إقامة "
            f"({student_name}) من {possessive_pronoun} القديم رقم ({old_passport}) إلى {possessive_pronoun} الجديد رقم ({new_passport})."
        )
        
        body_text = f"{greeting}\n\n{main_request}"

        return {
            'subject': 'الموضوع: طلب نقل بيانات الإقامة',
            'body_text': body_text,
            'correspondent': correspondent,
        }
        
        return ctx # <-- تم إصلاح هذا الخطأ


# أضف هذا الكلاس الجديد في ملف views.py

class GenerateStudyVisaLetterView(BaseLetterView):
    """Generates the letter for a new study visa request."""
    letter_template_name = 'students/letters/study_visa_letter.html'
    letter_type_code = 'SVI' # رمز لتأشيرة دراسة

    def get_letter_context(self, request, students_queryset):
        # المخاطب هو مدير الجوازات
        correspondent = Correspondent.objects.filter(category='مدير الجوازات').first()
        student = students_queryset.first()

        # --- تحديد الصياغة بناءً على الجنس ---
        if student and student.gender == 'M':
            # نص المذكر
            gender_specific_phrase = f"الأخ الموضحة بياناته في الجدول أدناه تقدم بطلب للدراسة لدينا وتم قبول طلبه"
        else:
            # نص المؤنث
            gender_specific_phrase = f"الأخت الموضحة بياناتها في الجدول أدناه تقدمت بطلب للدراسة لدينا وتم قبول طلبها"
        
        body_text = (
            "يهديكم مركز الفخرية للدراسات الشرعية أطيب التحايا متمنين لكم دوام التوفيق والنجاح في مهامكم.. "
            f"وبالإشارة إلى الموضوع أعلاه نود إفادتكم بأنه {gender_specific_phrase} فنرجو منكم التعاون في منحه التأشيرة وتسهيل اجراءاته."
        )

        return {
            'subject': 'الموضوع: طلب تأشيرة دراسة',
            'body_text': body_text,
            'correspondent': correspondent,
        }


class GenerateIssueResidenceLetterView(BaseLetterView):
    """Generates the letter to issue a new student residence permit."""
    letter_template_name = 'students/letters/issue_residence_letter.html'
    letter_type_code = 'IRE' # رمز لـ Issue Residence

    def get_letter_context(self, request, students_queryset):
        # المخاطب هو مدير الجوازات
        correspondent = Correspondent.objects.filter(category='مدير الجوازات').first()
        student = students_queryset.first()

        # --- تحديد الصياغة بناءً على الجنس ---
        if student and student.gender == 'M':
            # نص المذكر
            gender_specific_phrase = "للأخ المذكور بياناته"
        else:
            # نص المؤنث
            gender_specific_phrase = "للأخت المذكورة بياناتها"
        
        body_text = (
            "يهديكم مركز الفخرية للدراسات الشرعية أطيب التحايا متمنين لكم دوام التوفيق والنجاح في مهامكم.. "
            f"إشارة إلى الموضوع أعلاه، نرجو تكرمكم بصرف إقامة {gender_specific_phrase} أدناه لغرض الدراسة لدينا بالمركز، "
            "ونتعهد أمامكم بعدم مزاولته أي عمل، وفي حالة المخالفة لذلك نكون عرضة للإجراءات القانونية التي تتخذ من قبلكم ونتحمل نفقة ترحيله ودفع الغرامات القانونية."
        )

        return {
            'subject': 'الموضوع: طلب صرف إقامة طالب',
            'body_text': body_text,
            'correspondent': correspondent,
        }


class GenerateNormalExitVisaLetterView(BaseLetterView):
    """Generates the letter for a normal exit visa request."""
    letter_template_name = 'students/letters/normal_exit_visa_letter.html'
    letter_type_code = 'NEX' # رمز لـ Normal Exit

    def get_letter_context(self, request, students_queryset):
        # المخاطب هو مدير الجوازات
        correspondent = Correspondent.objects.filter(category='مدير الجوازات').first()
        student = students_queryset.first()

        # --- تحديد الصياغة بناءً على الجنس ---
        if student and student.gender == 'M':
            # نص المذكر
            gender_specific_phrase = "الأخ الموضحة بياناته في الجدول أدناه يريد"
        else:
            # نص المؤنث
            gender_specific_phrase = "الأخت الموضحة بياناتها في الجدول أدناه تريد"
        
        body_text = (
            "يهديكم مركز الفخرية للدراسات الشرعية أطيب التحايا متمنين لكم دوام التوفيق والنجاح في مهامكم.. "
            f"وبالإشارة إلى الموضوع أعلاه نود إفادتكم بأنه {gender_specific_phrase} تأشيرة خروج عادي فنرجو منكم التعاون في منحه التأشيرة وتسهيل اجراءاته."
        )

        return {
            'subject': 'الموضوع: طلب تأشيرة خروج عادي',
            'body_text': body_text,
            'correspondent': correspondent,
        }


class GenerateFinalExitVisaLetterView(BaseLetterView):
    """Generates the letter for a final exit visa request."""
    letter_template_name = 'students/letters/final_exit_visa_letter.html'
    letter_type_code = 'FEX' # تم توحيد الرمز ليكون أوضح

    # --- هذا هو التعديل الرئيسي: إضافة request إلى تعريف الدالة ---
    def get_letter_context(self, request, students_queryset):
        # المخاطب هو مدير الجوازات
        correspondent = Correspondent.objects.filter(category='مدير الجوازات').first()
        student = students_queryset.first()

        # تحديد الصياغة بناءً على الجنس
        if student and student.gender == 'M':
            # نص المذكر
            gender_specific_phrase = "بأنه الأخ الموضح بياناته في الجدول أدناه يريد تأشيرة خروج نهائي"
        else:
            # نص المؤنث
            gender_specific_phrase = "بأن الأخت الموضحة بياناتها في الجدول أدناه تريد تأشيرة خروج نهائي"
        
        body_text = (
            "يهديكم مركز الفخرية للدراسات الشرعية أطيب التحايا متمنين لكم دوام التوفيق والنجاح في مهامكم.. "
            f"وبالإشارة إلى الموضوع أعلاه نود إفادتكم {gender_specific_phrase} فنرجو منكم التعاون في منحها التأشيرة وتسهيل اجراءاته."
        )

        return {
            'subject': 'الموضوع: طلب تأشيرة خروج نهائي',
            'body_text': body_text,
            'correspondent': correspondent,
        }


class GenerateNewStudentsListLetterView(BaseLetterView):
    """Generates the letter for a list of new students."""
    letter_template_name = 'students/letters/new_students_list_letter.html'
    letter_type_code = 'NSTU'
    page_title = 'إنشاء كشف بأسماء الطلاب الجدد'

    def get_letter_context(self, request, students_queryset):
        # استخدام فئة إنجليزية (أفضل ممارسة)
        # تأكد من وجود هذه الفئة في لوحة التحكم لجهة "الأمن السياسي"
        correspondent = Correspondent.objects.filter(category='الأمن السياسي').first()
        
        body_text = (
            "يهديكم مركز الفخرية للدراسات الشرعية أطيب التحايا متمنين لكم دوام التوفيق والنجاح في مهامكم.. "
            "وبالإشارة إلى الموضوع أعلاه نرجو تكرمكم بالاطلاع على كشف الطلاب الجدد بالفخرية للدراسات الشرعية:"
        )

        context = {
            'subject': 'الموضوع: كشف بأسماء الطلاب الجدد',
            'body_text': body_text,
            'correspondent': correspondent,
        }

        # --- هذا هو المنطق الديناميكي المطلوب ---
        # إذا كان الطلب فرديًا (GET)، أرسل إشارة الإغلاق
        if request.method == 'GET':
            context['post_print_action'] = 'close'
        
        # إذا كان الطلب جماعيًا (POST)، لن يتم إضافة الإشارة،
        # وبالتالي سينفذ القالب الجزء الخاص بالعودة للرئيسية (else)
        
        return context
        



class GenerateEntryPermitLetterView(BaseLetterView):
    """Generates the letter for an entry permit."""
    letter_template_name = 'students/letters/entry_permit_letter.html'
    letter_type_code = 'ENP' # تم توحيد الرمز
    page_title = 'إنشاء موافقة دخول'

    # --- هذا هو التعديل الرئيسي: إضافة request إلى تعريف الدالة ---
    def get_letter_context(self, request, students_queryset):
        # تم تغيير الفئة لتكون باللغة الإنجليزية (أفضل ممارسة)
        correspondent = Correspondent.objects.filter(category='الأمن القومي').first()

        # منطق متقدم لتحديد الصياغة بناءً على العدد والجنس
        count = students_queryset.count()
        if count == 1:
            student = students_queryset.first()
            if student.gender == 'M':
                dynamic_phrase = "تقدم إلينا الأخ الموضح بياناته في الجدول أدناه بطلب للدراسة لدينا بالمركز وتم قبول طلبه فنرجو منكم التعاون في السماح له بالدخول"
            else:
                dynamic_phrase = "تقدمت إلينا الأخت الموضحة بياناتها في الجدول أدناه بطلب للدراسة لدينا بالمركز وتم قبول طلبها فنرجو منكم التعاون في السماح لها بالدخول"
        else:
            all_female = all(s.gender == 'F' for s in students_queryset)
            if all_female:
                dynamic_phrase = "تقدمن إلينا الأخوات الموضحة بياناتهن في الجدول أدناه بطلب للدراسة لدينا بالمركز وتم قبول طلبهن فنرجو منكم التعاون في السماح لهن بالدخول"
            else: # مجموعة مختلطة أو ذكور فقط
                dynamic_phrase = "تقدم إلينا الإخوة الموضحة بياناتهم في الجدول أدناه بطلب للدراسة لدينا بالمركز وتم قبول طلبهم فنرجو منكم التعاون في السماح لهم بالدخول"
        
        body_text = (
            "يهديكم مركز الفخرية للدراسات الشرعية أطيب التحايا متمنين لكم دوام التوفيق والنجاح في مهامكم.. "
            f"وبالإشارة إلى الموضوع أعلاه نود إفادتكم بأنه {dynamic_phrase} وتسهيل اجراءاتهم:"
        )

        return {
            'subject': 'الموضوع: توجيهاتكم بمنح موافقة دخول',
            'body_text': body_text,
            'correspondent': correspondent,
        }



class GenerateEntryPermitNSLetterView(BaseLetterView):
    """Generates the letter for a list of new students."""
    letter_template_name = 'students/letters/new_students_list_letter.html'
    letter_type_code = 'NSEN'
    page_title = 'إنشاء كشف بأسماء الطلاب الجدد'

    def get_letter_context(self, request, students_queryset):
        # استخدام فئة إنجليزية (أفضل ممارسة)
        # تأكد من وجود هذه الفئة في لوحة التحكم لجهة "الأمن السياسي"
        correspondent = Correspondent.objects.filter(category='الأمن القومي').first()
        
        body_text = (
            "يهديكم مركز الفخرية للدراسات الشرعية أطيب التحايا متمنين لكم دوام التوفيق والنجاح في مهامكم.. "
            "وبالإشارة إلى الموضوع أعلاه نرجو تكرمكم بالاطلاع على كشف الطلاب الجدد بالفخرية للدراسات الشرعية:"
        )

        context = {
            'subject': 'الموضوع: كشف بأسماء الطلاب الجدد',
            'body_text': body_text,
            'correspondent': correspondent,
        }

        # --- هذا هو المنطق الديناميكي المطلوب ---
        # إذا كان الطلب فرديًا (يأتي من صفحة تفاصيل الطالب عبر GET)، أرسل إشارة الإغلاق
        if request.method == 'GET':
            context['post_print_action'] = 'close'
        
        # إذا كان الطلب جماعيًا (يأتي من صفحة اختيار الطلاب عبر POST)، 
        # لن يتم إضافة الإشارة، وبالتالي سينفذ القالب الجزء الخاص بالعودة للرئيسية (else)
        
        return context



class GenerateReceptionDelegateLetterView(BaseLetterView):
    """Generates the letter for authorizing a reception delegate."""
    letter_template_name = 'students/letters/reception_delegate_letter.html'
    letter_type_code = 'RECP'

    # لقد قمنا بتخصيص دالة render_letter بالكامل لهذا الكلاس
    # لأنها تتعامل مع طلبات GET التي تحتوي على بيانات إضافية
    def render_letter(self, request, students_queryset):
        # استخراج البيانات الإضافية من رابط GET
        arrival_date_str = request.GET.get('arrival_date')
        delegate_name = request.GET.get('delegate_name', '[اسم المندوب]')

        # حساب اليوم من التاريخ
        try:
            arrival_date_obj = datetime.strptime(arrival_date_str, '%Y-%m-%d').date()
            arabic_weekdays = ["الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]
            arrival_day = arabic_weekdays[arrival_date_obj.weekday()]
            formatted_arrival_date = arrival_date_obj.strftime('%Y/%m/%d')
        except (ValueError, TypeError):
            arrival_day = "[اليوم]"
            formatted_arrival_date = "[التاريخ]"
            
        # إنشاء الرقم المرجعي
        try:
            with transaction.atomic():
                counter, _ = ReferenceCounter.objects.select_for_update().get_or_create(letter_type_code=self.letter_type_code)
                counter.last_sequence += 1
                counter.save()
                year_short = str(timezone.now().year)[-2:]
                sequence_str = str(counter.last_sequence).zfill(3)
                new_ref_number = f"{self.letter_type_code}-{year_short}-{sequence_str}"
        except Exception as e:
            messages.error(request, f"فشل إنشاء الرقم المرجعي: {e}")
            return redirect(request.path_info)

        # تجهيز النص الديناميكي للخطاب
        student = students_queryset.first()
        if student and student.gender == 'M':
            subject_phrase = "الطالب المذكور بياناته"
            arrival_verb = "سيصل"
            reception_pronoun = "لاستقباله"
        else:
            subject_phrase = "الطالبة المذكورة بياناتها"
            arrival_verb = "ستصل"
            reception_pronoun = "لاستقبالها"
        
        body_text = (
            "نهديكم أطيب التحية وبالإشارة إلى الموضوع أعلاه نحيطكم علما بأن "
            f"{subject_phrase} أدناه {arrival_verb} يوم {arrival_day} الموافق {formatted_arrival_date}م وعليه فإننا نفوض {delegate_name} "
            f"مندوب من قبلنا {reception_pronoun} فنرجو منكم التوجيه إلى الجهات المعنية لتسهيل الإجراءات."
        )
        
        # --- هذا هو التعديل المطلوب: جلب بيانات المدير التنفيذي ---
        exec_dir = ExecutiveDirector.objects.first()
        today = timezone.now().date()
        hijri_today = Gregorian(today.year, today.month, today.day).to_hijri()

        context = {
            'students': students_queryset,
            'gregorian_date': today.strftime('%Y/%m/%d'),
            'hijri_date': f"{hijri_today.year}/{hijri_today.month:02d}/{hijri_today.day:02d}",
            'reference_number': new_ref_number,
            'correspondent': None,
            'subject': 'الموضوع: تفويض مندوب لديكم في المطار لاستقبال طلاب لدينا',
            'body_text': body_text,
            # تم تصحيح هذا الجزء لجلب البيانات بدلاً من إرسال قيمة فارغة
            'exec_name': getattr(exec_dir, 'name', ''),
            'exec_title': getattr(exec_dir, 'title', ''),
            'exec_institute': getattr(exec_dir, 'institute', ''),
            'signature_url': exec_dir.signature.url if exec_dir and exec_dir.signature else None,
        }

        # تسجيل الخطاب وعرضه للطباعة
        new_letter_record = GeneratedLetter.objects.create(reference_number=new_ref_number, letter_type=context.get('subject'), created_by=request.user)
        new_letter_record.students.set(students_queryset)
        
        return render(request, self.letter_template_name, context)

    # نعيد تعريف دالة post لتكون متوافقة مع الحالة الجماعية إذا أردنا استخدامها لاحقًا
    def post(self, request, *args, **kwargs):
        # في هذه الحالة، طلب POST سيعرض صفحة اختيار الطلاب مجددًا لإدخال البيانات
        # لأن البيانات الإضافية (التاريخ والمندوب) ضرورية
        return self.get(request, *args, **kwargs)


class GenerateYemeniaAirwaysLetterView(BaseLetterView):
    """Generates the letter for Yemenia Airways."""
    letter_template_name = 'students/letters/yemenia_airways_letter.html'
    letter_type_code = 'AIR' # رمز لـ Yemenia Airways

    # بما أن هذا الخطاب يحتاج بيانات إضافية، سنقوم بتخصيص دالة post
    def post(self, request, *args, **kwargs):
        selected_student_ids = request.POST.getlist('student_ids')
        if not selected_student_ids:
            messages.error(request, 'لم تقم باختيار أي طالب.')
            return redirect(request.path_info)
        
        students_queryset = Student.objects.filter(id__in=selected_student_ids)

        # استخراج تاريخ الوصول من النموذج
        arrival_date_str = request.POST.get('arrival_date')

        # 1. إنشاء الرقم المرجعي
        try:
            with transaction.atomic():
                counter, _ = ReferenceCounter.objects.select_for_update().get_or_create(letter_type_code=self.letter_type_code)
                counter.last_sequence += 1
                counter.save()
                year_short = str(timezone.now().year)[-2:]
                sequence_str = str(counter.last_sequence).zfill(3)
                new_ref_number = f"{self.letter_type_code}-{year_short}-{sequence_str}"
        except Exception as e:
            messages.error(request, f"فشل إنشاء الرقم المرجعي: {e}")
            return redirect(request.path_info)

        # 2. تجهيز النص الديناميكي للخطاب
        correspondent = Correspondent.objects.filter(category='yemenia_airways').first()
        try:
            arrival_date_obj = datetime.strptime(arrival_date_str, '%Y-%m-%d').date()
            arabic_weekdays = ["الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]
            arrival_day = arabic_weekdays[arrival_date_obj.weekday()]
            formatted_arrival_date = arrival_date_obj.strftime('%Y/%m/%d')
        except (ValueError, TypeError):
            arrival_day = "[اليوم]"
            formatted_arrival_date = "[التاريخ]"

        count = students_queryset.count()
        if count == 1:
            student = students_queryset.first()
            subject_phrase = "الطالب الموضح بياناته" if student.gender == 'M' else "الطالبة الموضحة بياناتها"
        else:
            subject_phrase = "الطلاب المذكورة بياناتهم"

        body_text = (
            "نهديكم أطيب التحية كما نحيطكم علما بأن "
            f"{subject_phrase} أدناه قد تقدموا بطلب الدراسة لدينا بالمركز وتم قبول طلبهم فنرجو منكم التعاون في السماح لهم بالدخول وتسهيل اجراءاتهم وسيصلون يوم "
            f"{arrival_day} {formatted_arrival_date}م عبر مطار سيئون فنرجو منكم التوجيه إلى الجهات المعنية لتسهيل الإجراءات."
        )
        
        # 3. تجميع السياق الكامل
        exec_dir = ExecutiveDirector.objects.first()
        today = timezone.now().date()
        hijri_today = Gregorian(today.year, today.month, today.day).to_hijri()
        context = {
            'students': students_queryset,
            'gregorian_date': today.strftime('%Y/%m/%d'),
            'hijri_date': f"{hijri_today.year}/{hijri_today.month:02d}/{hijri_today.day:02d}",
            'reference_number': new_ref_number,
            'correspondent': correspondent,
            'subject': None, # هذا الخطاب ليس له موضوع
            'body_text': body_text,
            'exec_name': getattr(exec_dir, 'name', ''),
            'exec_title': getattr(exec_dir, 'title', ''),
            'exec_institute': getattr(exec_dir, 'institute', ''),
            'signature_url': exec_dir.signature.url if exec_dir and exec_dir.signature else None,
        }

        # 4. تسجيل الخطاب وعرضه للطباعة
        new_letter_record = GeneratedLetter.objects.create(reference_number=new_ref_number, letter_type="خطاب الخطوط اليمنية", created_by=request.user)
        new_letter_record.students.set(students_queryset)
        return render(request, self.letter_template_name, context)

class GenerateAcceptanceStatementLetterView(View): # لاحظ أنه يرث من View مباشرة
    """Generates the letter for a statement of acceptance."""
    letter_template_name = 'students/letters/acceptance_statement_letter.html'
    letter_type_code = 'ACP'

    def get(self, request, *args, **kwargs):
        student_id = request.GET.get('student_id')
        correspondent_name = request.GET.get('correspondent_name', '(اسم الجهة)')
        correspondent_title = request.GET.get('correspondent_title', '(الوصف)')

        if not student_id:
            return HttpResponse("خطأ: لم يتم تحديد طالب.", status=400)

        student = get_object_or_404(Student, pk=student_id)
        students_queryset = Student.objects.filter(pk=student_id)

        # 1. إنشاء الرقم المرجعي
        try:
            with transaction.atomic():
                counter, _ = ReferenceCounter.objects.select_for_update().get_or_create(letter_type_code=self.letter_type_code)
                counter.last_sequence += 1
                counter.save()
                year_short = str(timezone.now().year)[-2:]
                sequence_str = str(counter.last_sequence).zfill(3)
                new_ref_number = f"{self.letter_type_code}-{year_short}-{sequence_str}"
        except Exception as e:
            messages.error(request, f"فشل إنشاء الرقم المرجعي: {e}")
            return redirect(request.path_info)

        # 2. تجهيز النص الديناميكي للخطاب
        if student.gender == 'M':
            gender_specific_phrase = "تقدم إلينا الأخ الموضح بياناته في الكشف أدناه بطلب للدراسة لدينا بالمركز وقد تم قبول طلب دراسته فنرجو منكم تحويل إقامته علينا"
        else:
            gender_specific_phrase = "تقدمت إلينا الأخت الموضحة بياناتها في الكشف أدناه بطلب للدراسة لدينا بالمركز وقد تم قبول طلب دراستها فنرجو منكم تحويل إقامتها علينا"
        
        body_text = (
            "يهديكم مركز الفخرية للدراسات الشرعية أطيب التحايا متمنين لكم دوام التوفيق والنجاح في مهامكم.. "
            f"وبالإشارة إلى الموضوع أعلاه نود إفادتكم بأنه {gender_specific_phrase}."
        )

        # 3. تجميع السياق الكامل
        exec_dir = ExecutiveDirector.objects.first()
        today = timezone.now().date()
        hijri_today = Gregorian(today.year, today.month, today.day).to_hijri()
        context = {
            'students': students_queryset,
            'gregorian_date': today.strftime('%Y/%m/%d'),
            'hijri_date': f"{hijri_today.year}/{hijri_today.month:02d}/{hijri_today.day:02d}",
            'reference_number': new_ref_number,
            'correspondent_name': correspondent_name,
            'correspondent_title': correspondent_title,
            'subject': 'الموضوع: إفادة قبول للدراسة لدينا بالمركز',
            'body_text': body_text,
            'exec_name': getattr(exec_dir, 'name', ''),
            'exec_title': getattr(exec_dir, 'title', ''),
            'exec_institute': getattr(exec_dir, 'institute', ''),
            'signature_url': exec_dir.signature.url if exec_dir and exec_dir.signature else None,
        }

        # 4. تسجيل الخطاب وعرضه للطباعة
        GeneratedLetter.objects.create(reference_number=new_ref_number, letter_type=context.get('subject'), created_by=request.user)
        new_letter_record = GeneratedLetter.objects.latest('id')
        new_letter_record.students.set(students_queryset)
        
        return render(request, self.letter_template_name, context)



class GenerateGroupAcceptanceLetterView(BaseLetterView):
    """
    Generates a group "Statement of Acceptance" letter addressed to 
    'To Whom It May Concern'.
    """
    letter_template_name = 'students/letters/acceptance_statement_letter.html'
    letter_type_code = 'ACP' # Group Acceptance

    def get_letter_context(self, request, students_queryset):
        # هذا الخطاب الجماعي ليس له مخاطب محدد
        correspondent = None

        # منطق لتحديد الصياغة بناءً على العدد والجنس
        count = students_queryset.count()
        if count == 1:
            student = students_queryset.first()
            if student.gender == 'M':
                gender_specific_phrase = "تقدم إلينا الأخ الموضح بياناته في الكشف أدناه بطلب للدراسة لدينا بالمركز وقد تم قبول طلب دراسته فنرجو منكم تحويل إقامته علينا"
            else:
                gender_specific_phrase = "تقدمت إلينا الأخت الموضحة بياناتها في الكشف أدناه بطلب للدراسة لدينا بالمركز وقد تم قبول طلب دراستها فنرجو منكم تحويل إقامتها علينا"
        else:
            all_female = all(s.gender == 'F' for s in students_queryset)
            if all_female:
                gender_specific_phrase = "تقدمن إلينا الأخوات الموضحة بياناتهن في الكشف أدناه بطلب للدراسة لدينا بالمركز وقد تم قبول طلب دراستهن فنرجو منكم تحويل إقامتهن علينا"
            else: # مجموعة مختلطة أو ذكور فقط
                gender_specific_phrase = "تقدم إلينا الإخوة الموضحة بياناتهم في الكشف أدناه بطلب للدراسة لدينا بالمركز وقد تم قبول طلب دراستهم فنرجو منكم تحويل إقامتهم علينا"

        body_text = (
            "يهديكم مركز الفخرية للدراسات الشرعية أطيب التحايا متمنين لكم دوام التوفيق والنجاح في مهامكم.. "
            f"وبالإشارة إلى الموضوع أعلاه نود إفادتكم بأنه {gender_specific_phrase}."
        )

        return {
            'subject': 'الموضوع: إفادة قبول للدراسة لدينا بالمركز',
            'body_text': body_text,
            'correspondent': correspondent,
            'post_print_action': 'close',
        }


class GenerateEnrollmentCertificateLetterView(BaseLetterView):
    """Generates the letter for a proof of enrollment certificate."""
    letter_template_name = 'students/letters/enrollment_certificate_letter.html'
    letter_type_code = 'ECE' # رمز لـ Enrollment Certificate

    def get_letter_context(self, request, students_queryset):
        student = students_queryset.first()

        # --- تحديد الصياغة بناءً على الجنس ---
        if student and student.gender == 'M':
            # نص المذكر
            gender_specific_phrase = "الأخ المذكور بياناته أدناه طالب لدينا بالمركز وقد أعطي هذه الإفادة بناء على طلبه"
        else:
            # نص المؤنث
            gender_specific_phrase = "الأخت المذكورة بياناتها أدناه طالبة لدينا بالمركز وقد أعطيت هذه الإفادة بناء على طلبها"
        
        body_text = (
            "نهديكم أطيب التحية وبالإشارة إلى الموضوع أعلاه نحيطكم علما بأن "
            f"{gender_specific_phrase}."
        )

        return {
            'subject': 'الموضوع: إفادة قيد',
            'body_text': body_text,
            'correspondent': None, # هذا الخطاب موجه إلى "من يهمه الأمر"
            'post_print_action': 'close',
        }



# أضف هذا الكلاس الجديد في ملف views.py

class GenerateGroupTripCertificateView(BaseLetterView):
    """Generates the letter for a group trip certificate."""
    letter_template_name = 'students/letters/group_trip_certificate.html'
    letter_type_code = 'G-TRIP' # رمز لـ Group Trip
    page_title = 'إنشاء إفادة رحلة جماعية'

    def get_letter_context(self, request, students_queryset):
        # استخراج البيانات الإضافية من النموذج الذي يظهر في النافذة المنبثقة
        travel_date_str = request.POST.get('travel_date')
        destination = request.POST.get('destination', '[الوجهة]')

        # حساب اليوم والتاريخ الهجري تلقائيًا
        try:
            travel_date_obj = datetime.strptime(travel_date_str, '%Y-%m-%d').date()
            arabic_weekdays = ["الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]
            travel_day = arabic_weekdays[travel_date_obj.weekday()]
            formatted_travel_date = travel_date_obj.strftime('%d/%m/%Y')
            hijri_travel_date_obj = Gregorian(travel_date_obj.year, travel_date_obj.month, travel_date_obj.day).to_hijri()
            formatted_hijri_date = f"{hijri_travel_date_obj.day:02d}/{hijri_travel_date_obj.month:02d}/{hijri_travel_date_obj.year}"
        except (ValueError, TypeError):
            travel_day, formatted_travel_date, formatted_hijri_date = "[اليوم]", "[التاريخ]", "[التاريخ الهجري]"
        
        # منطق لتحديد الصياغة بناءً على العدد والجنس
        if students_queryset.count() > 1 and all(s.gender == 'F' for s in students_queryset):
             subject_phrase = "الطالبات المذكورة بياناتهن"
             pronoun_they = "وهن متوجهات"
             pronoun_them = "لهن"
        else:
             subject_phrase = "الإخوة الموضحة بياناتهم"
             pronoun_they = "وهم متوجهون"
             pronoun_them = "لهم"

        body_text = (
            "يهديكم مركز الفخرية للدراسات الشرعية أطيب التحايا متمنين لكم دوام التوفيق والنجاح في مهامكم.. "
            f"نود إفادتكم بأن {subject_phrase} في الجدول أدناه طلاب لدينا وهم تحت مسؤوليتنا وعلى كفالتنا، "
            f"{pronoun_they} إلى {destination} يوم {travel_day} تاريخ {formatted_travel_date}م الموافق {formatted_hijri_date}هـ، "
            f"ثم العودة لمواصلة دراستهم لدينا فنرجو منكم السماح {pronoun_them} بالمرور وتسهيل اجراءاتهم."
        )

        return {
            'correspondent': None, # إلى من يهمه الأمر
            'subject': "الموضوع: إفادة قيد", # هذا هو الموضوع الموجود في الصورة
            'body_text': body_text,
            'post_print_action': 'redirect'
        }


        

