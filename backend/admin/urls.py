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
    path('category_list/', views.list_categories, name='list_categories'),

    # Product Management URLs
    path('add_product/', views.add_product, name='add_product'),
    path('update_product/', views.update_product, name='update_product'),
    path('delete_product/', views.delete_product, name='delete_product'),
    path('product_list/', views.list_products, name='list_products'),
]