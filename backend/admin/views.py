from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.core.files.storage import default_storage

from store.views import jwt_encode, jwt_decode, auth_admin
from store.models import User, Product, Category
import json

@csrf_exempt
def admin_login(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
    data = json.loads(request.body)

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return JsonResponse({'success': False, 'message': 'Missing email or password.'}, status=400)
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Invalid email or password'}, status=400)
    
    user = authenticate(request, username=user.email, password=password)

    if user is not None:
        if user.is_staff:
            login(request, user)
            token = jwt_encode(user.email)
            return JsonResponse({'success': True, 'message': 'Login successful.', 'email': email, 'token': token}, status=200)
        else:
            return JsonResponse({'success': False, 'message': 'You do not have admin access.'}, status=403)
    else:
        return JsonResponse({'success': False, 'message': 'Invalid email or password'}, status=400)
    
    
##################################>>>>>>>>User Management API's<<<<<<<<<<<<<################################
@csrf_exempt
def users_list(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
    try:
        bearer = request.headers.get('Authorization')
        
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authentication Header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_admin(token):
            return JsonResponse({'success': False, 'message': 'Invalid Token.'}, status=401)
        
        users = User.objects.filter(is_customer=True)
        user_list = []
        
        for user in users:
            user_list.append({
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'username': user.username,
                'phone_number': user.phone_number,
                'date_of_birth': user.dob,
                'marital_status': user.marital_status,
                'date_joined': user.date_joined,
                'last_login': user.last_login,
            })
        return JsonResponse({'success': True, 'message': 'Users retrieved successfully.', 'user_list': user_list}, status=200)
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
        
##################################>>>>>>>>Product API's<<<<<<<<<<<<<################################
@csrf_exempt
def add_product(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
    try:
        bearer = request.headers.get('Authorization')
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authorization header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_admin(token):
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
        
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        price = request.POST.get('price', '').strip()
        stock = request.POST.get('stock', '').strip()
        category_id = request.POST.get('category_id', '').strip()
        image = request.FILES.get('image')
        
        required_fields = ['name', 'description', 'price', 'stock', 'category_id', 'image']
        missing_fields = [field for field in required_fields if field not in request.POST]
        if missing_fields:
            return JsonResponse({'success': False, 'message': f'Missing required fields: {", ".join(missing_fields)}'}, status=400)

        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Category not found.'}, status=404)
        
        product = Product.objects.create(
            name=name,
            description=description,
            price=price,
            stock=stock,
            category=category,
            image=image
        )
        
        return JsonResponse({'success': True, 'message': 'Product added successfully.', 'product_id': product.id}, status=200)
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
@csrf_exempt
def update_product(request):
    if request.method != 'PUT':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use PUT.'}, status=405)

    try:
        bearer = request.headers.get('Authorization')
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authorization header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_admin(token):
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
        
        try:
            product_id = request.PUT.get('product_id', '').strip()
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Product not found'}, status=404)
        
        product.name = request.POST.get('name', product.name).strip()
        product.description = request.POST.get('description', product.description).strip()
        product.price = request.POST.get('price', product.price).strip()
        product.stock = request.POST.get('stock', product.stock).strip()
        product.category_id = request.POST.get('category_id', product.category_id).strip()
        product.image = request.FILES.get('image', product.image)
        product.save()
        
        return JsonResponse({'success': True, 'message': 'Product updated successfully.', 'product_id': product.id}, status=200)
 
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
@csrf_exempt
def delete_product(request):
    if request.method != 'DELETE':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use DELETE.'}, status=405)
    
    try:
        bearer = request.headers.get('Authorization')
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authorization header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_admin(token):
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
        
        try:
            product_id = request.DELETE.get('product_id', '').strip()
            product = Product.objects.get(id=product_id)
            product.delete()
            return JsonResponse({'success': True, 'message': 'Product deleted successfully.'}, status=200)
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Product not found.'}, status=404)
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
    
##################################>>>>>>>>Category Management API's<<<<<<<<<<<<<################################
@csrf_exempt
def add_category(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
    try:
        bearer = request.headers.get('Authorization')
        
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authentication Header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_admin(token):
            return JsonResponse({'success': False, 'message': 'Invalid Token.'}, status=401)
        
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        image = request.FILES.get('image')
        
        if not name or not description or not image:
            return JsonResponse({'success': False, 'message': 'Missing required fields.'}, status=400)
        
        category = Category.objects.create(
            name=name,
            description=description,
            image=image
        )
        
        return JsonResponse({'success': True, 'message': 'Category added successfully.', 'category_id': category.id}, status=201)
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)    
        
@csrf_exempt
def update_category(request):
    if request.method != 'PUT':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use PUT. '}, status=405)
    
    try:
        bearer = request.headers.get('Authorization')
        
        if not bearer:
            return JsonResponse({'sucess': False, 'message': 'Authorization header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_admin(token):
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
        
        category_id = request.PUT.get('category_id', '').strip()
        category = Category.objects.get(id=category_id)
        
        if not category:
            return JsonResponse({'success': False, 'message': 'Category not found.'}, status=404)
        
        name = request.PUT.get('name', category.name).strip()
        description = request.PUT.get('description', category.description).strip()
        image = request.PUT.get('image', category.image)
        
        category.name = name
        category.description = description
        if image:
            category.image = image
        category.save()
        
        return JsonResponse({'success': True, 'message': 'Category updated successfully.', 'category_id': category.id}, status=200)
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
@csrf_exempt
def delete_category(request):
    if request.method != 'DELETE':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use DELETE.'}, status=405)
        
    try:
        bearer = request.headers.get('Authorization')
        
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authorization header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_admin(token):
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
        
        category_id = request.DELETE.get('category_id', '').strip()
        category = Category.objects.get(id=category_id)
        
        if not category:
            return JsonResponse({'success': False, 'message': 'Category not found.'}, status=404)
        
        category.delete()
        
        return JsonResponse({'success': True, 'message': 'Category deleted successfully.'}, status=200)
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)  