from django.urls import path, include
from . import views

urlpatterns = [
    path('admin_login/', views.admin_login, name='admin_login'),
    
    # User management URLs
    path('users_list/', views.users_list, name='users_list'),
    
    # Category Management URLs
    path('add_category/', views.add_category, name='add_category'),
    path('update_category/<int:category_id>/', views.update_category, name='update_category'),
    path('delete_category/', views.delete_category, name='delete_category'),
    path('category_list/', views.list_categories, name='list_categories'),

    # Product Management URLs
    path('add_product/', views.add_product, name='add_product'),
    path('update_product/', views.update_product, name='update_product'),
    path('delete_product/', views.delete_product, name='delete_product'),
    path('product_list/', views.list_products, name='list_products'),

    # Carousel Images Management URLs
    path('add_carousel_image/', views.add_carousel_image, name='add_carousel_image'),
    path('update_carousel_image/', views.update_carousel_image, name='update_carousel_image'),
    path('delete_carousel_image/', views.delete_carousel_image, name='delete_carousel_image'),
    path('list_carousel_images/', views.list_carousel_images, name='list_carousel_images'),
    path('list_carousel_images_order/', views.list_carousel_images_order, name='list_carousel_images_order'),
    path('get_carousel_image/', views.get_carousel_image, name='get_carousel_image'),
    path('increment_carousel_image_click_count/<int:carousel_image_id>', views.increment_carousel_image_click_count, name='increment_carousel_image_click_count'),
]