from django.urls import path
from .views import (
    HomeWithStatsView,
    StudentListView,
    StudentDetailView,
    StudentCreateView,
    StudentUpdateView,
    StudentDeleteView,
    CustomLoginView,
    StatisticsView,
    PassportRenewalView,
    TransferResidenceLetterView,
)

app_name = 'students'

urlpatterns = [
    path('', HomeWithStatsView.as_view(),         name='home'),
    path('login/', CustomLoginView.as_view(),     name='login'),

    # CRUD الطلاب
    path('students/',                          StudentListView.as_view(),   name='student_list'),
    path('students/add/',                      StudentCreateView.as_view(), name='student_create'),
    path('students/<int:student_id>/',         StudentDetailView.as_view(), name='student_detail'),
    path('students/<int:student_id>/edit/',    StudentUpdateView.as_view(), name='student_update'),
    path('students/<int:student_id>/delete/',  StudentDeleteView.as_view(), name='student_delete'),

    # الإحصائيات (JSON)
    path('students/stats/', StatisticsView.as_view(), name='statistics'),

    # نموذج تجديد جواز
    path('students/<int:student_id>/passport/',        PassportRenewalView.as_view(),        name='passport_renewal'),
    path('students/<int:student_id>/transfer-residence/', TransferResidenceLetterView.as_view(), name='transfer_residence_letter'),
]
