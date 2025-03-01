from django.urls import path
from . import views
from .views import CustomLoginView
from .views import student_detail, student_edit, delete_student

urlpatterns = [
    path('', views.home, name='home'),
    path('add/', views.add_student, name='add_student'),
    path('students/', views.student_list, name='student_list'),
    path('student/<int:student_id>/', views.student_detail, name='student_detail'),
    path('student/<int:student_id>/edit/', student_edit, name='student_edit'),
    path('student/delete/<int:student_id>/', delete_student, name='delete_student'),
    path('login/', CustomLoginView.as_view(), name='login'),
]


