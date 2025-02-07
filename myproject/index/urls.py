from django.urls import include, path
from .views import index_view, register_view

urlpatterns = [
    path('', index_view, name='index'),
    path('users/', include('django.contrib.auth.urls')),
    path('register/', register_view, name='register')
]