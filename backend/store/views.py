from django.shortcuts import render
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout

from store.models import User

import string
import random
import json
import jwt


def jwt_encode(email):
    encoded_token = jwt.encode({'email': email}, settings.SECRET_KEY, algorithm='HS256')
    return encoded_token

def jwt_decode(token):
    decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    return decoded_token

def auth_customer(token):
    decoded_token = jwt_decode(token)
    email = decoded_token['email']
    customer = User.objects.filter(email=email, is_customer=True).first()
    if customer:
        return True
    else:
        return False

def auth_admin(token):
    decoded_token = jwt_decode(token)
    email = decoded_token['email']
    admin = User.objects.filter(email=email, is_staff=True).first()
    if admin:
        return True
    else:
        return False
    
def generate_random_password(length=8):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))
    
@csrf_exempt
def user_register(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
    try:
        data = json.loads(request.body)
        required_fields = ['email']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return JsonResponse({'success': False, 'message': f'Missing required fields: {", ".join(missing_fields)}'}, status=400)
        
        email = data.get('email').strip()
        first_name = data.get('first_name').strip()
        last_name = data.get('last_name').strip()
        phone_number = data.get('phone_number').strip()
        password = data.get('password').strip()
        login_by = data.get('login_by')

        if login_by == 2:
            password = generate_random_password()

        if User.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'message': 'User Already Exists.'}, status=409)
        
        username = email.split('@')[0]

        hashed_password = make_password(password)

        encoded_token = jwt_encode(email)

        User.objects.create(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            password=hashed_password,
            login_by=login_by,
            is_customer=True,
            profile_picture='profile_pictures/default.png'
            )

        return JsonResponse({'success': True, 'message': 'User Registered Successfully.', 'token': encoded_token}, status=201)
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invlaid JSON in request body.'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
@csrf_exempt
def user_login(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
    try:
        data = json.loads(request.body)

        email = data.get('email').strip()
        password = data.get('password').strip()

        if not email or not password:
            return JsonResponse({'success': False, 'message': 'Missing email or password.'}, status=400)
        
        user = authenticate(request, username=email, password=password)

        if user is not None:
            if user.is_customer:
                login(request, user)
                token = jwt_encode(user.email)
                return JsonResponse({'success': True, 'message': 'Login Successful.', 'token': token}, status=200)
            else:
                return JsonResponse({'success': False, 'message': 'User is not a customer.'}, status=400)
        else:
            return JsonResponse({'success': False, 'message': 'Invalid login credentials..'}, status=401)
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invlaid JSON in request body.'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
@csrf_exempt
def user_logout(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
        
    try:
        if request.user.is_authenticated:
            logout(request)
            return JsonResponse({'success': True, 'message': 'Logout successful.'}, status=200)
        else:
            return JsonResponse({'success': False, 'message': 'User is not authenticated.'}, status=401)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
@csrf_exempt
def user_get_details(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
    try:
        bearer = request.headers.get('Authorization')
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_customer(token):
            return JsonResponse({'success': False, 'message': 'Invalid token.'}, status=401)
        
        decoded_token = jwt_decode(token)
        user_email = decoded_token.get('email')

        if not user_email:
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
        
        user_obj = User.objects.get(email__iexact=user_email)

        user_details = {
            'id': user_obj.id,
            'email': user_obj.email,
            'first_name': user_obj.first_name,
            'last_name': user_obj.last_name,
            'username': user_obj.username,
            'phone_number': user_obj.phone_number,
            'marital_status': user_obj.marital_status,
            'dob': user_obj.dob.strftime('%Y-%m-%d') if user_obj.dob else None,
            'nationality': user_obj.nationality,
            'gender': user_obj.gender,
            'country': user_obj.country,
            'city': user_obj.city,
            'address': user_obj.address,
            'zip_code': user_obj.zip_code,
            'profile_picture': user_obj.profile_picture.url if user_obj.profile_picture else None,
            'two_factor': user_obj.two_factor,
        }

        return JsonResponse({'success': True, 'message': 'User details fetched successfully.', 'user_details': user_details}, status=200)
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=400)