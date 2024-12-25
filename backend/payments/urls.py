from django.urls import path
from payments import views

urlpatterns = [
    path('create_payment/', views.create_payment, name='create_payment'),
    path('verify_payment/', views.verify_payment, name='verify_payment'),
    path('get_payment_status/<int:order_id>/', views.get_payment_status, name='get_payment_status'),
    path('refund_payment/<int:order_id>/', views.refund_payment, name='refund_payment'),
    path('get_refund_status/<int:order_id>/', views.get_refund_status, name='get_refund_status'),
]

