from django.urls import path, include
from .views import *


urlpatterns = [
    path('students/', students_view, name="students"),
    path('student_profile/<int:student_id>/', student_profile_view, name="student_profile"),
    path('groups/', groups_view, name="groups"),
    path('group/<int:group_id>', group_detail_view, name="group_detail"),
    path('statements/', statements_view, name="statements"),
    path('commission/', commission_view, name="commission"),
    path('orders/', orders_view, name="orders"),
    path('teachers/', teachers_view, name="teachers"),
    path('courses/', courses_view, name="courses"),
    path('course_edit/<int:course_id>/', course_edit_view, name='course_edit'),
    path('group_add/', add_group_view, name="group_add"),
    path('course_add/', add_course_view, name="course_add"),
    path('teacher_add/', add_teacher_view, name="teacher_add"),
    path('commission_add/', add_commission_view, name="commission_add"),
]