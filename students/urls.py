# students/urls.py  🚩 النسخة المنسَّقة

from django.urls import path
from .views import (
    StudentListView, StudentDetailView, StudentCreateView,
    StudentUpdateView, StudentDeleteView,
    # --- خطابات ---
    TransferResidenceLetterView, GenerateMedicalCheckLetterView,
    GenerateExitReentryVisaLetterView, GenerateResidenceRenewalLetterView,
    GenerateStudyVisaLetterView, GenerateIssueResidenceLetterView,
    GenerateNormalExitVisaLetterView, GenerateFinalExitVisaLetterView,
    GenerateNewStudentsListLetterView, GenerateEntryPermitLetterView,
    GenerateEntryPermitNSLetterView, GenerateReceptionDelegateLetterView,
    GenerateYemeniaAirwaysLetterView, GenerateAcceptanceStatementLetterView,
    GenerateGroupAcceptanceLetterView, GenerateEnrollmentCertificateLetterView,
    GenerateGroupTripCertificateView, HomeView, dashboard_data,
    EntryVisaFormView, ResidenceRenewalFormView, ForeignServiceRequestFormView,
    ExitVisaFormView
)

app_name = "students"

urlpatterns = [
    path("dashboard-data/", dashboard_data, name="dashboard_data"),
    # -------- CRUD الطلاب --------
    path("list/", StudentListView.as_view(), name="student_list"),
    path("add/",  StudentCreateView.as_view(), name="student_create"),
    path("<int:pk>/",          StudentDetailView.as_view(), name="student_detail"),
    path("<int:pk>/edit/",     StudentUpdateView.as_view(), name="student_update"),
    path("<int:pk>/delete/", StudentDeleteView.as_view(), name="student_delete"),

    # -------- مسارات الخطابات الفردية --------
    path("letter/transfer-residence/",  TransferResidenceLetterView.as_view(), name="transfer_residence_letter"),
    path("letters/medical-check-request/", GenerateMedicalCheckLetterView.as_view(), name="generate_medical_check_letter"),
    path("letters/exit-reentry-visa/",  GenerateExitReentryVisaLetterView.as_view(), name="generate_exit_reentry_visa_letter"),
    path("letter/study-visa/",          GenerateStudyVisaLetterView.as_view(), name="generate_study_visa_letter"),
    path("letter/issue-residence/",     GenerateIssueResidenceLetterView.as_view(), name="generate_issue_residence_letter"),
    path("letter/normal-exit-visa/",    GenerateNormalExitVisaLetterView.as_view(), name="generate_normal_exit_visa_letter"),
    path("letter/final-exit-visa/",     GenerateFinalExitVisaLetterView.as_view(), name="generate_final_exit_visa_letter"),
    path("letter/residence-renewal/",   GenerateResidenceRenewalLetterView.as_view(), name="generate_residence_renewal_letter"),
    path("letter/new-students-list/",   GenerateNewStudentsListLetterView.as_view(), name="generate_new_students_list_letter"),
    path("letter/entry-permit/",        GenerateEntryPermitLetterView.as_view(), name="generate_entry_permit_letter"),
    path("letter/entry-permit-ns/",     GenerateEntryPermitNSLetterView.as_view(), name="generate_entry_permit_ns_letter"),
    path("letter/reception-delegate/",  GenerateReceptionDelegateLetterView.as_view(), name="generate_reception_delegate_letter"),
    path("letter/yemenia-airways/",     GenerateYemeniaAirwaysLetterView.as_view(), name="generate_yemenia_airways_letter"),
    path("letter/acceptance-statement/",       GenerateAcceptanceStatementLetterView.as_view(), name="generate_acceptance_statement_letter"),
    path("letter/group-acceptance-statement/", GenerateGroupAcceptanceLetterView.as_view(), name="generate_group_acceptance_letter"),
    path("letter/enrollment-certificate/",     GenerateEnrollmentCertificateLetterView.as_view(), name="generate_enrollment_certificate_letter"),
    path("letter/group-trip-certificate/",     GenerateGroupTripCertificateView.as_view(), name="generate_group_trip_certificate"),

    path("student/<int:pk>/forms/entry-visa/",          EntryVisaFormView.as_view(), name="entry_visa_form", ),
    path("student/<int:pk>/forms/residence-renewal/",   ResidenceRenewalFormView.as_view(), name="residence_renewal_form",),
    path("student/<int:pk>/forms/foreign-service/",     ForeignServiceRequestFormView.as_view(), name="foreign_service_form",),
    path("student/<int:pk>/forms/exit-visa/", ExitVisaFormView.as_view(), name="exit_visa_form",),
]
