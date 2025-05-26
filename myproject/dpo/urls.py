from django.urls import path, include
from .views import *


urlpatterns = [
    path('students/', students_view, name="students"),
    path('student_profile/<int:student_id>/', student_profile_view, name="student_profile"),
    path('student_edit/<int:student_id>/', student_edit_view, name="student_edit"),
    path('groups/', groups_view, name="groups"),
    path('group/<int:group_id>', group_detail_view, name="group_detail"),
    path('groups/edit/<int:group_id>/', edit_group_view, name='edit_group'),
    path('commission_group_add/<int:group_id>', commission_group_add_view, name="commission_group_add"),
    path('commission_group_edit/<int:group_id>', commission_group_edit_view, name="commission_group_edit"),
    path('statements/', statements_view, name="statements"),
    path('commission/', commission_view, name="commission"),
    path('documents/', documents_view, name="documents"),
    path('enroll_order/<int:group_id>/', enroll_order_view, name="enroll_order"),
    path('commission_order/<int:group_id>/', commission_order_view, name="commission_order"),
    path('protocol/<int:group_id>/', protocol_view, name="protocol"),
    path('exam_sheet/<int:group_id>/', exam_sheet_view, name="exam_sheet"),
    path('expel_group/<int:group_id>/', expel_group_view, name="expel_group"),
    path('teachers/', teachers_view, name="teachers"),
    path('courses/', courses_view, name="courses"),
    path('course_edit/<int:course_id>/', course_edit_view, name='course_edit'),
    path('group_add/', add_group_view, name="group_add"),
    path('course_add/', add_course_view, name="course_add"),
    path('teacher_add/', add_teacher_view, name="teacher_add"),
    path('teacher_edit/<int:teacher_id>/', teacher_edit_view, name="teacher_edit"),
    path('commission_add/', add_commission_view, name="commission_add"),
    path('commission_edit/<int:member_id>/', commission_edit_view, name="commission_edit"),
    path("group/<int:group_id>/finish-course/", finish_course, name="finish_course"),
    path("lesson_log/<int:group_id>/", lesson_log_view, name="lesson_log"),
]