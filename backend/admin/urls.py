from django.urls import path, include
from . import views

urlpatterns = [
    path('admin_login/', views.admin_login, name='admin_login'),
]