# students/urls.py (النسخة المصححة)

from django.urls import path
from .views import (
    StudentListView,
    StudentDetailView,
    StudentCreateView,
    StudentUpdateView,
    StudentDeleteView,
    TransferResidenceLetterView,
    GenerateMedicalCheckLetterView,
    GenerateExitReentryVisaLetterView,
    GenerateResidenceRenewalLetterView,
    GenerateStudyVisaLetterView,
    GenerateIssueResidenceLetterView,
    GenerateNormalExitVisaLetterView,
    GenerateFinalExitVisaLetterView,
)

app_name = 'students'

urlpatterns = [
    # Student CRUD URLs
    path('list/', StudentListView.as_view(), name='student_list'),
    path('add/', StudentCreateView.as_view(), name='student_create'),
    path('<int:student_id>/', StudentDetailView.as_view(), name='student_detail'),
    path('<int:student_id>/edit/', StudentUpdateView.as_view(), name='student_update'),
    path('<int:student_id>/delete/', StudentDeleteView.as_view(), name='student_delete'),

    # Letter Generation URLs
    path('letters/medical-check-request/', GenerateMedicalCheckLetterView.as_view(), name='generate_medical_check_letter'),
    path('letters/exit-reentry-visa/', GenerateExitReentryVisaLetterView.as_view(), name='generate_exit_reentry_visa_letter'),
    
    # Single Letter URLs
    path('letter/transfer-residence/', TransferResidenceLetterView.as_view(), name='transfer_residence_letter'),
    path('letter/study-visa/', GenerateStudyVisaLetterView.as_view(), name='generate_study_visa_letter'),
    path('letter/issue-residence/', GenerateIssueResidenceLetterView.as_view(), name='generate_issue_residence_letter'),
    path('letter/normal-exit-visa/', GenerateNormalExitVisaLetterView.as_view(), name='generate_normal_exit_visa_letter'),
    path('letter/final-exit-visa/', GenerateFinalExitVisaLetterView.as_view(), name='generate_final_exit_visa_letter'),
    
    # 2. تم حذف "views." من السطر التالي لأنه لم يعد ضروريًا
    path('letter/residence-renewal/', GenerateResidenceRenewalLetterView.as_view(), name='generate_residence_renewal_letter'),
]