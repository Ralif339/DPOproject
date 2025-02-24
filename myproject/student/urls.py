from django.urls import path
from .views import update_info_view, new_statement_view

urlpatterns = [
    path('update_info/', update_info_view, name='update_info'),
    path('new_statement/', new_statement_view, name='new_statement'),
]