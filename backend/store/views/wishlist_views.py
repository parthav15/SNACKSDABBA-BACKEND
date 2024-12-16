from django.shortcuts import render
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.core.files.storage import default_storage
from django.db.models import Q

from store.models import User, Product, Cart, CartItem, Wishlist
from store.views.user_views import jwt_encode, jwt_decode, auth_customer

import string
import random
import json
import datetime

@csrf_exempt
def add_to_wishlist(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
    try:
        bearer = request.headers.get('Authorization')
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_customer(token):
            return JsonResponse({'success': False, 'message': 'Invalid Token Data.'}, status=401)
        
        decoded_token = jwt_decode(token)
        user_email = decoded_token.get('email')

        if not user_email:
            return JsonResponse({'success': False, 'message': 'Invalid Token Data.'}, status=401)
        
        user = User.objects.get(email__iexact=user_email)

        product_id = request.POST.get('product_id')

        if not product_id:
            return JsonResponse({'success': False, 'message': 'Product ID is required.'}, status=400)
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Product not found.'}, status=404)
        
        if Wishlist.objects.filter(user=user, product=product).exists():
            return JsonResponse({'success': False, 'message': 'Product is already in wishlist.'}, status=400)
        
        Wishlist.objects.create(user=user, product=product)

        return JsonResponse({'success': True, 'message': 'Product added to wishlist successfully.', 'product': {
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
        }}, status=201)
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
@csrf_exempt
def remove_from_wishlist(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
    try:
        bearer = request.headers.get('Authorization')
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_customer(token):
            return JsonResponse({'success': False, 'message': 'Invalid Token Data.'}, status=401)
        
        decoded_token = jwt_decode(token)
        user_email = decoded_token.get('email')

        if not user_email:
            return JsonResponse({'success': False, 'message': 'Invalid Token Data.'}, status=401)
        
        user = User.objects.get(email__iexact=user_email)

        product_id = request.POST.get('product_id')

        if not product_id:
            return JsonResponse({'success': False, 'message': 'Product ID is required.'}, status=400)
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Product not found'}, status=404)
        
        try:
            wishlist_item = Wishlist.objects.get(user=user, product=product)
        except Wishlist.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Product not found in wishlist.'}, status=404)
        
        wishlist_item.delete()

        return JsonResponse({'success': True, 'message': 'Product removed from wishlist successfully.', 'product': {
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
        }}, status=200)
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
@csrf_exempt
def get_wishlist_products(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
    try:
        bearer = request.headers.get('Authorization')
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_customer(token):
            return JsonResponse({'success': False, 'message': 'Invalid Token Data.'}, status=401)
        
        decoded_token = jwt_decode(token)
        user_email = decoded_token.get('email')

        if not user_email:
            return JsonResponse({'success': False, 'message': 'Invalid Token Data.'}, status=401)
        
        user = User.objects.get(email__iexact=user_email)

        wishlist_prducts = Wishlist.objects.filter(user=user).values('product')

        wishlist_products_list = []
        for product in wishlist_prducts:
            wishlist_products_list.append({
                'id': product['product'],
                'name': Product.objects.get(id=product['product']).name,
                'description': Product.objects.get(id=product['product']).description,
                'price': Product.objects.get(id=product['product']).price,
                'discount_price': Product.objects.get(id=product['product']).discount_price,
                'stock': Product.objects.get(id=product['product']).stock,
                'category': Product.objects.get(id=product['product']).category.name,
                'image': Product.objects.get(id=product['product']).image,
                'video_url': Product.objects.get(id=product['product']).video_url,
                'attributes': Product.objects.get(id=product['product']).attributes,
                'is_featured': Product.objects.get(id=product['product']).is_featured,
                'rating': Product.objects.get(id=product['product']).rating,
                'brand': Product.objects.get(id=product['product']).brand,
                'meta_keywords': Product.objects.get(id=product['product']).meta_keywords,
                'meta_description': Product.objects.get(id=product['product']).meta_description
            })
        
        return JsonResponse({'success': True, 'message': 'Wishlist products retrieved successfully.', 'products': wishlist_products_list}, status=200)
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)

