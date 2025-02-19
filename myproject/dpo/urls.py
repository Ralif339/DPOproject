from django.urls import path, include
from .views import *


urlpatterns = [
    path('students/', students_view, name="students"),
    path('groups/', groups_view, name="groups"),
    path('statements/', statements_view, name="statements"),
    path('commission/', commission_view, name="commission"),
    path('orders/', orders_view, name="orders"),
    path('teachers/', teachers_view, name="teachers"),
    path('courses/', courses_view, name="courses"),
    path('group_add/', add_group_view, name="group_add"),
]