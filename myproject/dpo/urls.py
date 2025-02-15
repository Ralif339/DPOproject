from django.urls import path, include
from .views import *


urlpatterns = [
    path('students/', students_view, name="students"),
    path('groups/', groups_view, name="groups"),
    path('statements/', statements_view, name="statements"),
    path('commission/', commission_view, name="commission"),
    path('orders/', orders_view, name="orders"),
]