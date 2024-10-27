from django.urls import path, include
from . import views

urlpatterns = [
    path('admin_login/', views.admin_login, name='admin_login'),
    
    # User management URLs
    path('users_list/', views.users_list, name='users_list'),
    
    # Category Management URLs
    path('add_category/', views.add_category, name='add_category'),
    path('update_category/', views.update_category, name='update_category'),
    path('delete_category/', views.delete_category, name='delete_category'),
]