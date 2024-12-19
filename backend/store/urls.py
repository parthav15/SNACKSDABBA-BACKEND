from django.urls import path
from store.views import user_views, product_views, cart_views, wishlist_views, shippingaddress_views, billingaddress_views, order_views, category_views

urlpatterns = [
    # User Management URLs
    path('user_register/', user_views.user_register, name='register'),
    path('user_login/', user_views.user_login, name='login'),
    path('user_get_details/', user_views.user_get_details, name='user_get_details'),
    path('user_edit/', user_views.user_edit, name='user_edit'),
    
    # Category URLs
    path('list_categories/', category_views.list_categories, name='list_categories'),

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

    # Wishlist URLs
    path('add_to_wishlist/', wishlist_views.add_to_wishlist, name='add_to_wishlist'),
    path('remove_from_wishlist/', wishlist_views.remove_from_wishlist, name='remove_from_wishlist'),
    path('get_wishlist_products/', wishlist_views.get_wishlist_products, name='get_wishlist_products'),
    path('clear_wishlist/', wishlist_views.clear_wishlist, name='clear_wishlist'),
    path('wishlist_count/', wishlist_views.wislist_count, name='wishlist_count'),

    # Shipping Address URLs
    path('add_shipping_address/', shippingaddress_views.add_shipping_address, name='add_shipping_address'),
    path('update_shipping_address/', shippingaddress_views.update_shipping_address, name='update_shipping_address'),
    path('delete_shipping_address/', shippingaddress_views.delete_shipping_address, name='delete_shipping_address'),
    path('get_shipping_address/', shippingaddress_views.get_shipping_address, name='get_shipping_address'),
    path('list_shipping_address/', shippingaddress_views.list_shipping_address, name='list_shipping_address'),

    # Billing Address URLs
    path('add_billing_address/', billingaddress_views.add_billing_address, name='add_billing_address'),
    path('update_billing_address/', billingaddress_views.update_billing_address, name='update_billing_address'),
    path('delete_billing_address/', billingaddress_views.delete_billing_address, name='delete_billing_address'),
    path('get_billing_address/', billingaddress_views.get_billing_address, name='get_billing_address'),
    path('list_billing_address/', billingaddress_views.list_billing_address, name='list_billing_address'),

    # Order URLs
    path('create_order/', order_views.create_order, name='create_order'),
    path('get_order_details/', order_views.get_order_details, name='get_order_details'),
    path('add_order_item/', order_views.add_order_item, name='add_order_item'),
    path('remove_order_item/', order_views.remove_order_item, name='remove_order_item'),
    path('update_shipping_address_order/', order_views.update_shipping_address_order, name='update_shipping_address_order'),
    path('update_billing_address_order/', order_views.update_billing_address_order, name='update_billing_address_order'),
    path('list_orders/', order_views.list_orders, name='list_orders'),
]
