from django.shortcuts import render
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.core.files.storage import default_storage

from store.models import User, Product
from store.user_views import jwt_encode, jwt_decode, auth_customer

import string
import random
import json

@csrf_exempt
def list_products(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
    try:
        products = Product.objects.all().values(
            'id', 
            'name', 
            'description', 
            'price', 
            'discount_price',
            'stock', 
            'category__name', 
            'image',
            'video_url',
            'attributes',
            'is_featured',
            'rating',
            'brand',
            'meta_keywords',
            'meta_description'
        )
        products_list = list(products)
        
        return JsonResponse({'success': True, 'products': products_list}, status=200)
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
@csrf_exempt
def get_product(request, product_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
    try:
        product = Product.objects.get(id=product_id)
        products_list = {
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
        }

        return JsonResponse({'success': True, 'message': 'Product retrieved successfully.', 'product': products_list}, status=200)
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Product not found.'}, status=404)
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
@csrf_exempt
def get_products_by_category(request, category_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
    try:
        products = Product.objects.filter(category_id=category_id).values(
            'id', 
            'name', 
            'description', 
            'price', 
            'discount_price',
            'stock', 
            'category__name', 
            'image',
            'video_url',
            'attributes',
            'is_featured',
            'rating',
            'brand',
            'meta_keywords',
            'meta_description'
        )
        products_list = list(products)
        
        return JsonResponse({'success': True, 'message': 'Product retrieved successfully.', 'products': products_list}, status=200)
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Product not found.'}, status=404)
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
@csrf_exempt
def get_products_by_featured(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
    try:
        products = Product.objects.filter(is_featured=True).values(
            'id', 
            'name', 
            'description', 
            'price', 
            'discount_price',
            'stock', 
            'category__name', 
            'image',
            'video_url',
            'attributes',
            'is_featured',
            'rating',
            'brand',
            'meta_keywords',
            'meta_description'
        )
        products_list = list(products)
        
        return JsonResponse({'success': True, 'message': 'Featured products retrieved successfully.', 'products': products_list}, status=200)
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Product not found.'}, status=404)
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)

@csrf_exempt
def get_products_by_brand(request, brand_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
    try:
        products = Product.objects.filter(brand_id=brand_id).values(
            'id', 
            'name', 
            'description', 
            'price', 
            'discount_price',
            'stock', 
            'category__name', 
            'image',
            'video_url',
            'attributes',
            'is_featured',
            'rating',
            'brand',
            'meta_keywords',
            'meta_description'
        )
        products_list = list(products)
        
        return JsonResponse({'success': True, 'message': 'Brand products retrieved successfully.', 'products': products_list}, status=200)
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Product not found.'}, status=404)
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)