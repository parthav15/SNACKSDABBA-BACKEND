from django.shortcuts import render, redirect
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.core.files.storage import default_storage
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

from store.models import User, Cart

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

        user = User.objects.create(
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

        Cart.objects.create(user=user)
        
        html_content = render_to_string('email_templates/verify_email.html', {
            'full_name': f'{first_name} {last_name}',
            'action_url': f'{settings.BACKEND_URL}api/activate_email/?token={encoded_token}',
            'logo_url': f'{settings.BACKEND_URL}media/images/logo-ct.png',
            'backend_url': settings.BACKEND_URL,
            'frontend_url': settings.FRONTEND_URL
        })

        email_message = EmailMessage(
            subject='Please verify your email',
            body=html_content,
            from_email=settings.EMAIL_HOST_USER,
            to=[email],
        )

        email_message.content_subtype = 'html'
        email_message.send(fail_silently=False)

        return JsonResponse({'success': True, 'message': 'A confirmation Email has been sent, Please verify the email to complete registration.', 'token': encoded_token}, status=201)
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON in request body.'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
@csrf_exempt
def activate_email(request):
    token = request.GET.get('token')
    if not token:
        return JsonResponse({'success': False, 'message': 'Token is required.'}, status=400)
    
    try:
        decoded_token = jwt_decode(token)
        user = User.objects.get(email=decoded_token['email'])
        email = user.email
        
        user.is_email = True
        user.save()

        html_content = render_to_string('email_templates/activate_email.html', {
            'full_name': f'{user.first_name} {user.last_name}',
            'logo_url': f'{settings.BACKEND_URL}media/images/logo-ct.png',
            'action_url': {settings.FRONTEND_URL}
        })
        
        email_message = EmailMessage(
            subject='Welcome to Snacks Dabba',
            body=html_content,
            from_email=settings.EMAIL_HOST_USER,
            to=[email],
        )

        email_message.content_subtype = 'html'
        email_message.send(fail_silently=False)

        return redirect(settings.FRONTEND_URL)
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found.'}, status=404)
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

                html_content = render_to_string('email_templates/activate_email.html', {
                    'full_name': f'{user.first_name} {user.last_name}',
                    'logo_url': f'{settings.BACKEND_URL}media/images/logo-ct.png',
                    'action_url': {settings.FRONTEND_URL}
                })
                
                email_message = EmailMessage(
                    subject='Welcome back to Snacks Dabba',
                    body=html_content,
                    from_email=settings.EMAIL_HOST_USER,
                    to=[email],
                )

                email_message.content_subtype = 'html'
                email_message.send(fail_silently=False)
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
    
@csrf_exempt
def user_edit(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST'}, status=405)
    
    try:
        bearer = request.headers.get('Authorization')
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authorization header is required.'}, status=401)
        
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
            return JsonResponse({'success': False, 'message': 'User not found'}, status=404)
        
        print(request.POST)
        print(request.FILES)
        
        user.first_name = request.POST.get('first_name', user.first_name).strip()
        user.last_name = request.POST.get('last_name', user.last_name).strip()
        user.username = request.POST.get('username', user.username).strip()
        user.phone_number = request.POST.get('phone_number', user.phone_number).strip()
        user.dob = request.POST.get('dob', user.dob)
        user.marital_status = request.POST.get('marital_status', user.marital_status).strip()
        user.nationality = request.POST.get('nationality', user.nationality).strip()
        user.gender = request.POST.get('gender', user.gender).strip()
        user.country = request.POST.get('country', user.country).strip()
        user.city = request.POST.get('city', user.city).strip()
        user.address = request.POST.get('address', user.address).strip()
        user.zip_code = request.POST.get('zip_code', user.zip_code).strip()
        profile_picture = request.FILES.get('profile_picture')

        if profile_picture:
            user.profile_picture = profile_picture
            user.save()
            user.refresh_from_db()
            print(user.profile_picture.url)
        user.save()
        
        return JsonResponse({'success': True, 'message': 'User updated successfully.'}, status=200)
 
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
@csrf_exempt
def user_change_password(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
    try:
        bearer = request.headers.get('Authorization')
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authorization header is required.'}, status=401)
        
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
        
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')

        if user.check_password(old_password):
            user.password = make_password(new_password)
            user.save()
            return JsonResponse({'success': True, 'message': 'Password changed successfully.'}, status=200)
        else:
            return JsonResponse({'success': False, 'message': 'Incorrect old password.'}, status=400)

    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)