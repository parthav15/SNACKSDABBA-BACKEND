from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.core.files.storage import default_storage

from store.user_views import jwt_encode, jwt_decode, auth_admin
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
                'two_factor': user.two_factor,
                'login_by' : user.login_by,
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
        discount_price = request.POST.get('discount_price', '').strip()
        video_url = request.POST.get('video_url', '').strip()
        attributes = request.POST.get('attributes', '').strip()
        is_featured = request.POST.get('is_featured', 'false').strip().lower() == 'true'
        rating = float(request.POST.get('rating', 0.0))
        brand = request.POST.get('brand', '').strip()
        stock = request.POST.get('stock', '').strip()
        category_id = request.POST.get('category_id', '').strip()
        images = request.FILES.getlist('image')
        
        required_fields = ['name', 'description', 'price', 'stock', 'category_id']
        missing_fields = [field for field in required_fields if not request.POST.get(field)]
        if missing_fields:
            return JsonResponse({'success': False, 'message': f'Missing required fields: {", ".join(missing_fields)}'}, status=400)

        products_image_paths = []

        for image in images:
            image_path = default_storage.save(f'products/{image.name}', image)
            products_image_paths.append(image_path)

        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Category not found.'}, status=404)
        
        product = Product.objects.create(
            name=name,
            description=description,
            price=price,
            discount_price=discount_price,
            video_url=video_url,
            attributes=attributes,
            is_featured=is_featured,
            rating=rating,
            brand=brand,
            stock=stock,
            category=category,
            image=products_image_paths
        )
        
        return JsonResponse({'success': True, 'message': 'Product added successfully.', 'product_id': product.id}, status=200)
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
@csrf_exempt
def update_product(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)

    try:
        bearer = request.headers.get('Authorization')
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authorization header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_admin(token):
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
        
        required_fields = ['product_id', 'name', 'description', 'price', 'discount_price', 'video_url', 'attributes', 'is_featured', 'rating', 'brand', 'stock', 'category_id']
        missing_fields = [field for field in required_fields if field not in request.PUT]
        if missing_fields:
            return JsonResponse({'success': False, 'message': f'Missing required fields: {", ".join(missing_fields)}'}, status=400)
        
        try:
            product_id = request.POST.get('product_id', '').strip()
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Product not found'}, status=404)
        
        product.name = request.PUT.get('name', product.name).strip()
        product.description = request.PUT.get('description', product.description).strip()
        product.price = request.PUT.get('price', product.price).strip()
        product.discount_price = request.PUT.get('discount_price', product.discount_price).strip()
        product.video_url = request.PUT.get('video_url', product.video_url).strip()
        product.attributes = request.PUT.get('attributes', product.attributes)
        product.is_featured = request.PUT.get('is_featured', product.is_featured) == 'True'
        product.rating = request.PUT.get('rating', product.rating)
        product.brand = request.PUT.get('brand', product.brand).strip()
        product.stock = request.PUT.get('stock', product.stock).strip()
        product.category_id = request.PUT.get('category_id', product.category_id).strip()
        images = request.FILES.getlist('image')
        products_image_paths = []

        if images:
            for image in images:
                image_path = default_storage.save(f'products/{image.name}', image)
                products_image_paths.append(image_path)
            product.image = products_image_paths
        product.save()
        
        return JsonResponse({'success': True, 'message': 'Product updated successfully.', 'product_id': product.id}, status=200)
 
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
@csrf_exempt
def delete_product(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
    try:
        bearer = request.headers.get('Authorization')
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authorization header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_admin(token):
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
        
        try:
            product_id = request.POST.get('product_id', '').strip()
            product = Product.objects.get(id=product_id)
            product.delete()
            return JsonResponse({'success': True, 'message': 'Product deleted successfully.'}, status=200)
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Product not found.'}, status=404)
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
@csrf_exempt
def list_products(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
    try:
        bearer = request.headers.get('Authorization')
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authorization header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_admin(token):
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
        
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
        
        category_name = request.POST.get('category_name', '').strip()
        description = request.POST.get('description', '').strip()
        image = request.FILES.get('image')

        missing_fields = []
        if not category_name:
            missing_fields.append('category_name')
        if not description:
            missing_fields.append('description')
        if not image:
            missing_fields.append('image')
        
        if missing_fields:
            return JsonResponse({'success': False, 'message': f'Missing required fields: {", ".join(missing_fields)}'}, status=400)
        
        category = Category.objects.create(
            name=category_name,
            description=description,
            image=image
        )
        
        return JsonResponse({'success': True, 'message': 'Category added successfully.', 'category_id': category.id}, status=201)
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
        
@csrf_exempt
def update_category(request, category_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST. '}, status=405)
    
    try:
        bearer = request.headers.get('Authorization')
        
        if not bearer:
            return JsonResponse({'sucess': False, 'message': 'Authorization header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_admin(token):
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
        
        category = Category.objects.get(id=category_id)
        
        if not category:
            return JsonResponse({'success': False, 'message': 'Category not found.'}, status=404)
        
        name = request.POST.get('name', category.name).strip()
        description = request.POST.get('description', category.description).strip()
        image = request.POST.get('image', category.image)
        
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
        
        data = json.loads(request.body)
        category_id = data.get('category_id', '')
        category = Category.objects.get(id=category_id)
        
        if not category:
            return JsonResponse({'success': False, 'message': 'Category not found.'}, status=404)
        
        category.delete()
        
        return JsonResponse({'success': True, 'message': 'Category deleted successfully.'}, status=200)
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
@csrf_exempt
def list_categories(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
    try:
        categories = Category.objects.all().values('id', 'name', 'description', 'image')
        categories_list = list(categories)
        
        return JsonResponse({'success': True, 'categories': categories_list}, status=200)
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)