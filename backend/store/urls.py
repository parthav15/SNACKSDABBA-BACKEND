from django.urls import path
from store.views import user_views, product_views, cart_views

urlpatterns = [
    # User Management URLs
    path('user_register/', user_views.user_register, name='register'),
    path('user_login/', user_views.user_login, name='login'),
    path('user_get_details/', user_views.user_get_details, name='user_get_details'),
    path('user_edit/', user_views.user_edit, name='user_edit'),
    
    # Category URLs

    # Product URLs
    path('search_products/', product_views.search_product, name='search_product'),
    path('list_products/', product_views.list_products, name='list_products'),
    path('get_product/<int:product_id>/', product_views.get_product, name='get_product'),
    path('get_products_by_category/<int:category_id>/', product_views.get_products_by_category, name='get_product_by_category'),
    path('get_products_by_featured/', product_views.get_products_by_featured, name='get_products_by_featured'),
    path('get_products_by_brand/', product_views.get_products_by_brand, name='get_products_by_brand'),
    path('get_products_by_latest/', product_views.get_products_by_latest, name='get_products_by_latest'),    
    path('get_discounted_products/', product_views.get_discounted_products, name='get_discounted_products'),
    path('create_bulk_products/', product_views.create_bulk_products, name='create_bulk_products'),

    # Cart URLs
    path('create_cart/', cart_views.create_cart, name='create_cart'),
    path('get_cart/', cart_views.get_cart, name='get_cart'),
    path('update_cart/', cart_views.update_cart, name='update_cart'),
    path('delete_cart/', cart_views.delete_cart, name='delete_cart'),
    path('clear_cart/', cart_views.clear_cart, name='clear_cart'),
    path('add_item_to_cart/', cart_views.add_item_to_cart, name='add_item_to_cart'),
    path('get_cart_items/', cart_views.get_cart_items, name='get_cart_items'),
    path('get_cart_item/', cart_views.get_cart_item, name='get_cart_item'),
    path('update_item_quantity/', cart_views.update_item_quantity, name='update_item_quantity'),
]
