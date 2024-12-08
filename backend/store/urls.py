from django.urls import path
from store import user_views, product_views

urlpatterns = [
    # User Management URLs
    path('user_register/', user_views.user_register, name='register'),
    path('user_login/', user_views.user_login, name='login'),
    path('user_get_details/', user_views.user_get_details, name='user_get_details'),
    path('user_edit/', user_views.user_edit, name='user_edit'),
    
    # Category URLs

    # Product URLs
    path('list_products/', product_views.list_products, name='list_products'),
    path('get_product/<int:product_id>/', product_views.get_product, name='get_product'),
    path('get_products_by_category/<int:category_id>/', product_views.get_products_by_category, name='get_product_by_category'),
    path('get_products_by_featured/', product_views.get_products_by_featured, name='get_products_by_featured'),
    path('get_products_by_brand/', product_views.get_products_by_brand, name='get_products_by_brand'),
]
