from django.shortcuts import render
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.core.files.storage import default_storage
from django.db.models import Q

from store.models import User, Product, Cart, CartItem, Wishlist, ShippingAddress
from store.views.user_views import jwt_encode, jwt_decode, auth_customer

import string
import random
import json
import datetime

@csrf_exempt
def add_shipping_address(request):
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

        phone_number = request.POST.get('phone_number', '')
        address_line1 = request.POST.get('address_line1', '')
        address_line2 = request.POST.get('address_line2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        postal_code = request.POST.get('postal_code', '')
        country = request.POST.get('country', '')

        shipping_address = ShippingAddress.objects.create(
            user=user,
            phone_number=phone_number,
            address_line1=address_line1,
            address_line2=address_line2,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country
        )

        return JsonResponse(
            {
                'success': True,
                'message': 'Shipping address added successfully.',
                'shipping_address': {
                    'id': shipping_address.id,
                    'phone_number': shipping_address.phone_number,
                    'address_line1': shipping_address.address_line1,
                    'address_line2': shipping_address.address_line2,
                    'city': shipping_address.city,
                    'state': shipping_address.state,
                    'postal_code': shipping_address.postal_code,
                    'country': shipping_address.country,
                }
            },
            status=200
        )
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
@csrf_exempt
def update_shipping_address(request):
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

        shipping_address_id = request.POST.get('shipping_address_id', '')
        if not shipping_address_id:
            return JsonResponse({'success': False, 'message': 'Shipping address ID is required.'}, status=400)

        try:
            shipping_address = ShippingAddress.objects.get(id=shipping_address, user=user)
        except ShippingAddress.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Shipping Address not found.'}, status=404)
        
        phone_number = request.POST.get('phone_number', shipping_address.phone_number)
        address_line1 = request.POST.get('address_line1', shipping_address.address_line1)
        address_line2 = request.POST.get('address_line2', shipping_address.address_line2)
        city = request.POST.get('city', shipping_address.city)
        state = request.POST.get('state', shipping_address.state)
        postal_code = request.POST.get('postal_code', shipping_address.postal_code)
        country = request.POST.get('country', shipping_address.country)

        shipping_address.phone_number = phone_number
        shipping_address.address_line1 = address_line1
        shipping_address.address_line2 = address_line2
        shipping_address.city = city
        shipping_address.state = state
        shipping_address.postal_code = postal_code
        shipping_address.country = country

        shipping_address.save()

        return JsonResponse(
            {
                'success': True,
                'message': 'Shipping address updated successfully.',
                'shipping_address': {
                    'id': shipping_address.id,
                    'phone_number': shipping_address.phone_number,
                    'address_line1': shipping_address.address_line1,
                    'address_line2': shipping_address.address_line2,
                    'city': shipping_address.city,
                    'state': shipping_address.state,
                    'postal_code': shipping_address.postal_code,
                    'country': shipping_address.country,
                }
            },
            status=200
        )
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)

@csrf_exempt
def delete_shipping_address(request):
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

        shipping_address_id = request.POST.get('shipping_address_id', '')
        if not shipping_address_id:
            return JsonResponse({'success': False, 'message': 'Shipping address ID is required.'}, status=400)

        try:
            shipping_address = ShippingAddress.objects.get(id=shipping_address_id, user=user)
        except ShippingAddress.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Shipping Address not found.'}, status=404)
        
        shipping_address.delete()

        return JsonResponse({'success': True, 'message': 'Shipping address deleted successfully.'}, status=200)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)

@csrf_exempt
def list_shipping_address(request):
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

        shipping_address = ShippingAddress.objects.filter(user=user).values(
            'id',
            'phone_number',
            'address_line1',
            'address_line2',
            'city',
            'state',
            'postal_code',
            'country'
        )

        return JsonResponse(
            {
                'success': True,
                'message': 'Shipping address fetched successfully.',
                'shipping_address': list(shipping_address)
            },
            status=200
        )
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
@csrf_exempt
def get_shipping_address(request):
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

        shipping_address_id = request.POST.get('shipping_address_id')

        try:
            shipping_address = ShippingAddress.objects.get(user=user, id=shipping_address_id)
        except ShippingAddress.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Shipping address not found.'}, status=404)
        
        return JsonResponse(
            {
                'success': True,
                'message': 'Shipping address fetched successfully.',
                'shipping_address': {
                    'id': shipping_address.id,
                    'phone_number': shipping_address.phone_number,
                    'address_line1': shipping_address.address_line1,
                    'address_line2': shipping_address.address_line2,
                    'city': shipping_address.city,
                    'state': shipping_address.state,
                    'postal_code': shipping_address.postal_code,
                    'country': shipping_address.country,
                }
            },
            status=200
        )
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
