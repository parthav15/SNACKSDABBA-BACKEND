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
