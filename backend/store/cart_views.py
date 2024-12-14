from django.shortcuts import render
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.core.files.storage import default_storage
from django.db.models import Q

from store.models import User, Product, Cart, CartItem
from store.user_views import jwt_encode, jwt_decode, auth_customer

import string
import random
import json
import datetime

@csrf_exempt
def create_cart(request):
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
        
        try:
            user = User.objects.get(email__iexact=user_email)
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User not found.'}, status=404)
        
        try:
            cart = Cart.objects.get(user=user)
            return JsonResponse({'success': True, 'message': 'Cart already exists.', 'cart_id': cart.id}, status=200)
        except Cart.DoesNotExist:
            cart = Cart.objects.create(user=user)
            return JsonResponse({'success': True, 'message': 'Cart created successfully.', 'cart_id': cart.id}, status=201)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)
    
@csrf_exempt
def get_cart(request):
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
        cart = Cart.objects.get(user=user)

        return JsonResponse({'success': True, 'message': 'Cart retrieved successfully.', 'cart_id': cart.id}, status=200)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)
    
@csrf_exempt
def update_cart(request):
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

        cart = Cart.objects.get(user=user)

        cart.modified_at = datetime.datetime.now()
        cart.save()

        return JsonResponse({'success': True, 'message': 'Cart Updated Successfully.'}, status=200)
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
    
@csrf_exempt
def delete_cart(request):
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
        
        cart = Cart.objects.get(user=user)
        cart.delete()
        
        return JsonResponse({'success': True, 'message': 'Cart deleted successfully.'}, status=200)
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)

@csrf_exempt
def clear_cart(request):
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
        
        cart = Cart.objects.get(user=user)
        cart.cart_items.all().delete()
        
        return JsonResponse({'success': True, 'message': 'Cart cleared successfully.'}, status=200)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
@csrf_exempt
def add_item_to_cart(request):
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

        cart = Cart.objects.get(user=user)

        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity', 1)

        if not product_id:
            return JsonResponse({'success': False, 'message': 'Product ID is required.'}, status=400)
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Product not found.'}, status=404)
        
        try:
            cart_item = CartItem.objects.get(cart=cart, product=product)
            cart_item.quantity += int(quantity)
            cart_item.save()
        except CartItem.DoesNotExist:
            CartItem.objects.create(cart=cart, product=product, quantity=int(quantity))

        return JsonResponse({'success': True, 'message': 'Item added to cart successfully.', 'product_name': product.name, 'quantity': cart_item.quantity}, status=200)
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
@csrf_exempt
def get_cart_items(request):
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
        
        cart = Cart.objects.get(user=user)
        
        cart_items = CartItem.objects.filter(cart=cart)

        items = []

        for item in cart_items:
            items.append({
                'id': item.id,
                'product_id': item.product.id,
                'product_name': item.product.name,
                'quantity': item.quantity,
                'created_at': item.created_at,
                'modified_at': item.modified_at
            })

        return JsonResponse({'success': True, 'message': 'Cart items retrieved successfully.', 'items': items}, status=200)
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
@csrf_exempt
def get_cart_item(request):
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
        
        cart = Cart.objects.get(user=user)
        
        product_id = request.POST.get('product_id')
        
        if not product_id:
            return JsonResponse({'success': False, 'message': 'Product ID is required.'}, status=400)
        
        try:
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
        except CartItem.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Item not found in cart'}, status=404)
        
        item = {
            'id': cart_item.id,
            'product_id': cart_item.product.id,
            'product_name': cart_item.product.name,
            'quantity': cart_item.quantity,
            'created_at': cart_item.created_at,
            'modified_at': cart_item.modified_at
        }
        
        return JsonResponse({'success': True, 'message': 'Cart item retrieved successfully.', 'item': item}, status=200)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
@csrf_exempt
def update_item_quantity(request):
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

        cart = Cart.objects.get(user=user)

        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity', 1)

        if not product_id:
            return JsonResponse({'success': False, 'message': 'Product ID is required.'}, status=400)
        
        try:
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
        except CartItem.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Item not found in the cart.'}, status=404)
        
        cart_item.quantity = quantity
        cart_item.save()
        
        product = cart_item.product
        
        return JsonResponse({
            'success': True,
            'message': 'Item quantity updated successfully.',
            'product': {
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': product.price,
                'discount_price': product.discount_price,
                'stock': product.stock,
                'category': product.category.name,
                'image': product.image,
                'video_url': product.video_url,
                'attributes': product.attributes,
                'is_featured': product.is_featured,
                'rating': product.rating,
                'brand': product.brand,
                'meta_keywords': product.meta_keywords,
                'meta_description': product.meta_description
            },
            'updated_quantity': cart_item.quantity
        }, status=200)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
