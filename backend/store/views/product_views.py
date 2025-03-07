from django.shortcuts import render
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.core.files.storage import default_storage
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from store.models import User, Product
from store.views.user_views import jwt_encode, jwt_decode, auth_customer

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
        page = int(request.POST.get('page', 1))
        paginator = Paginator(Product.objects.filter(is_featured=True).order_by("-created_at"), 10)
        
        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            return JsonResponse({'success': False, 'message': 'Invalid page.'}, status=400)
        except EmptyPage:
            return JsonResponse({'success': False, 'message': 'No more products.'}, status=404)
        
        products_list = []
        for product in products:
            products_list.append({
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
            })
        
        total_pages = paginator.num_pages
        
        return JsonResponse({
            'success': True, 
            'message': 'Featured products retrieved successfully.',
            'products': products_list,
            'pagination': {
                'page': page,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_previous': page > 1,
            }
        }, status=200)
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Product not found.'}, status=404)
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
@csrf_exempt
def get_brand_names(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
    try:
        brand_names = Product.objects.values_list('brand', flat=True).distinct()
        brand_names_list = list(brand_names)
        
        return JsonResponse({'success': True, 'message': 'Brand names retrieved successfully.', 'brand_names': brand_names_list}, status=200)
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Product not found.'}, status=404)
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)

@csrf_exempt
def get_products_by_brand(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
    try:
        brand = request.POST.get('brand')
        if not brand:
            return JsonResponse({'success': False, 'message': 'Brand is required.'}, status=400)
        
        products = Product.objects.filter(brand=brand).values(
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
    
@csrf_exempt
def search_product(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)

    try:
        search_query = request.POST.get('search_query')
        products = Product.objects.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))

        products_list = []
        for product in products:
            products_list.append({
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
            })

        return JsonResponse({'success': True, 'message': 'Products retrieved successfully.', 'products': products_list}, status=200)
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Product not found.'}, status=404)

    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
@csrf_exempt
def get_products_by_latest(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
    try:
        page = int(request.POST.get('page', 1))
        paginator = Paginator(Product.objects.all().order_by("-created_at"), 10)

        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            return JsonResponse({'success': False, 'message': 'Invalid page.'}, status=400)
        except EmptyPage:
            return JsonResponse({'success': False, 'message': 'No more products.'}, status=404)

        products_list = []
        for product in products:
            products_list.append({
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
            })

        total_pages = paginator.num_pages

        return JsonResponse({
            'success': True, 
            'message': 'Products retrieved successfully.',
            'products': products_list,
            'pagination': {
                'page': page,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_previous': page > 1,
            }
        }, status=200)
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Product not found.'}, status=404)

    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)

@csrf_exempt
def get_discounted_products(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)

    try:
        products = Product.objects.filter(discount_price__gt=0).values(
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
        
        return JsonResponse({'success': True, 'message': 'Discounted products retrieved successfully.', 'products': products_list}, status=200)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)

@csrf_exempt
def create_bulk_products(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
    try:
        products = json.loads(request.POST.get('products'))

        for product in products:
            Product.objects.create(
                name=product['name'],
                description=product['description'],
                price=product['price'],
                discount_price=product.get('discount_price', 0.00),
                stock=product['stock'],
                category_id=product['category_id'],
                image=product['image'],
                video_url=product.get('video_url', ''),
                attributes=product.get('attributes', {}),
                is_featured=product.get('is_featured', False),
                rating=product.get('rating', 0.0),
                brand=product.get('brand', ''),
                meta_keywords=product.get('meta_keywords', ''),
                meta_description=product.get('meta_description', '')
            )
        
        return JsonResponse({'success': True, 'message': 'Bulk products created successfully.'}, status=201)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
