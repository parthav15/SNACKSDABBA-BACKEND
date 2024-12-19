from django.shortcuts import render
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.core.files.storage import default_storage
from django.db.models import Q

from store.models import User, Product, Category
from store.views.user_views import jwt_encode, jwt_decode, auth_customer

import string
import random
import json

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