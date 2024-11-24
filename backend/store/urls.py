from django.urls import path
from store import views

urlpatterns = [
    # User Management URLs
    path('user_register/', views.user_register, name='register'),
    path('user_login/', views.user_login, name='login'),
    path('user_get_details/', views.user_get_details, name='user_get_details'),
    
    # Category URLs

    # Product URLs
]
