from django.shortcuts import render
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.core.files.storage import default_storage
from django.db.models import Q

from store.models import User, Product, Cart, CartItem, Wishlist, ShippingAddress, Order, OrderItem
from store.views.user_views import jwt_encode, jwt_decode, auth_customer

import string
import random
import json
import datetime

@csrf_exempt
def create_order(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
    try:
        bearer = request.headers.get('Authorization')
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_customer(token):
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
        
        decoded_token = jwt_decode(token)
        user_email = decoded_token.get('email')

        if not user_email:
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
        
        user = User.objects.get(email__iexact=user_email)

        cart_items = CartItem.objects.filter(user=user)
        if not cart_items.exists():
            return JsonResponse({'success': False, 'message': 'Cart is empty.'}, status=400)
        
        shipping_address_id = request.POST.get('shipping_address_id')
        if not shipping_address_id:
            return JsonResponse({'success': False, 'message': 'Shipping address ID is required.'}, status=400)
        
        try:
            shipping_address = ShippingAddress.objects.get(id=shipping_address_id)
        except ShippingAddress.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Shipping address not found.'}, status=404)
        
        is_gift = request.POST.get('is_gift', False)
        if is_gift not in [True, False]:
            return JsonResponse({'success': False, 'message': 'Invalid gift status.'}, status=400)
        
        gift_message = request.POST.get('gift_message', '')
        
        order = Order.objects.create(
            user=user,
            shipping_address=shipping_address,
            total_price=sum(item.product.price * item.quantity for item in cart_items),
            is_gift=is_gift,
            gift_message=gift_message,
        )

        order_items = []
        for cart_item in cart_items:
            order_item = OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price_at_purchase=cart_item.product.price,
            )
            order_items.append(order_item)
            cart_item.delete()

        return JsonResponse({'success': True, 'message': 'Order created successfully.', 'order_id': order.id, 'is_gift': order.is_gift, 'gift_message': order.gift_message}, status=200)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)

@csrf_exempt
def add_order_item(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
    try:
        bearer = request.headers.get('Authorization')
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_customer(token):
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
        
        decoded_token = jwt_decode(token)
        user_email = decoded_token.get('email')

        if not user_email:
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
        
        user = User.objects.get(email__iexact=user_email)

        order_id = request.POST.get('order_id')
        if not order_id:
            return JsonResponse({'success': False, 'message': 'Order ID is required.'}, status=400)

        try:
            order = Order.objects.get(id=order_id, user=user)
        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Order not found.'}, status=404)
        
        product_id = request.POST.get('product_id')
        if not product_id:
            return JsonResponse({'success': False, 'message': 'Product ID is required.'}, status=400)
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Product not found.'}, status=404)
        
        quantity = request.POST.get('quantity', 1)
        if not quantity.isdigit() or int(quantity) <= 0:
            return JsonResponse({'success': False, 'message': 'Invalid quantity.'}, status=400)
        
        order_item = OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price_at_purchase=product.price,
        )

        order.total_price += order_item.price_at_purchase * order_item.quantity
        order.save()

        order_items = OrderItem.objects.filter(order=order)
        order_details = {
            'id': order.id,
            'total_price': order.total_price,
            'order_items': [
                {
                    'id': item.id,
                    'product_id': item.product.id,
                    'product_name': item.product.name,
                    'quantity': item.quantity,
                    'price_at_purchase': item.price_at_purchase,
                }
                for item in order_items
            ]
        }
        return JsonResponse({'success': True, 'message': 'Order item added successfully.', 'order_id': order.id, 'order_details': order_details}, status=200)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
@csrf_exempt
def remove_order_item(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
    try:
        bearer = request.headers.get('Authorization')
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_customer(token):
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
        
        decoded_token = jwt_decode(token)
        user_email = decoded_token.get('email')

        if not user_email:
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
        
        user = User.objects.get(email__iexact=user_email)

        order_id = request.POST.get('order_id')
        if not order_id:
            return JsonResponse({'success': False, 'message': 'Order ID is required.'}, status=400)

        try:
            order = Order.objects.get(id=order_id, user=user)
        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Order not found.'}, status=404)
        
        order_item_id = request.POST.get('order_item_id')
        if not order_item_id:
            return JsonResponse({'success': True, 'message': 'Order item ID is required.'}, status=400)
        
        try:
            order_item = OrderItem.objects.get(id=order_item_id, order=order)
        except OrderItem.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Order Item not found.'}, status=404)
        
        order_item.delete()

        order.total_price -= order_item.price_at_purchase * order_item.quantity
        order.save()

        return JsonResponse({'success': True, 'message': 'Order item removed successfully.'}, status=200)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
@csrf_exempt
def update_shipping_address(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
    try:
        bearer = request.headers.get('Authorization')
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_customer(token):
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
        
        decoded_token = jwt_decode(token)
        user_email = decoded_token.get('email')

        if not user_email:
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
        
        user = User.objects.get(email__iexact=user_email)

        order_id = request.POST.get('order_id')
        if not order_id:
            return JsonResponse({'success': False, 'message': 'Order ID is required.'}, status=400)
        
        try:
            order = Order.objects.get(id=order_id, user=user)
        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Order not found.'}, status=404)
        
        shipping_address_id = request.POST.get('shipping_address_id')
        if not shipping_address_id:
            return JsonResponse({'success': False, 'message': 'Shipping Address ID is required.'}, status=400)
        
        try:
            shipping_address = ShippingAddress.objects.get(id=shipping_address_id, user=user)
        except ShippingAddress.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Shipping Address not found.'}, status=404)
        
        order.shipping_address = shipping_address
        order.save()

        return JsonResponse({'success': True, 'message': 'Shipping address updated successfully.'}, status=200)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)

    
@csrf_exempt
def get_order_details(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)