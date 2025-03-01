from django.urls import path
from .views import *

urlpatterns = [
    path('update_info/', update_info_view, name='update_info'),
    path('student_statements/', student_statements_view, name='student_statements'),
    path('new_statement/', new_statement_view, name='new_statement'),
    path('get_courses/', get_courses, name='get_courses'),
]