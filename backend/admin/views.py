from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from store.views import jwt_encode, jwt_decode, auth_user
from store.models import User
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