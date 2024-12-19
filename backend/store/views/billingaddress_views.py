from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
import json
from store.models import BillingAddress, User
from store.views.user_views import jwt_decode, auth_customer

@csrf_exempt
def add_billing_address(request):
    if request.method == 'POST':
        bearer = request.headers.get('Authorization')
        if bearer is not None:
            try:
                token = bearer.split(' ')[1]
                if auth_customer(token):
                    decoded_token = jwt_decode(token)
                    user_email = decoded_token['email']
                    user = User.objects.get(email__iexact=user_email)

                    phone_number = request.POST.get('phone_number', '')
                    address_line1 = request.POST.get('address_line1', '')
                    address_line2 = request.POST.get('address_line2', '')
                    city = request.POST.get('city', '')
                    state = request.POST.get('state', '')
                    postal_code = request.POST.get('postal_code', '')
                    country = request.POST.get('country', '')

                    billing_address = BillingAddress.objects.create(
                        user=user,
                        phone_number=phone_number,
                        address_line1=address_line1,
                        address_line2=address_line2,
                        city=city,
                        state=state,
                        postal_code=postal_code,
                        country=country
                    )

                    return JsonResponse({
                        'success': True,
                        'message': 'Billing address added successfully.',
                        'billing_address': {
                            'id': billing_address.id,
                            'phone_number': billing_address.phone_number,
                            'address_line1': billing_address.address_line1,
                            'address_line2': billing_address.address_line2,
                            'city': billing_address.city,
                            'state': billing_address.state,
                            'postal_code': billing_address.postal_code,
                            'country': billing_address.country,
                        }
                    }, status=200)
                else:
                    return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
            except Exception as e:
                return JsonResponse({'success': False, 'message': str(e)}, status=401)
        else:
            return JsonResponse({'success': False, 'message': 'Authorization header not found.'}, status=401)
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)

@csrf_exempt
def update_billing_address(request):
    if request.method == 'POST':
        bearer = request.headers.get('Authorization')
        if bearer is not None:
            try:
                token = bearer.split(' ')[1]
                if auth_customer(token):
                    decoded_token = jwt_decode(token)
                    user_email = decoded_token['email']
                    user = User.objects.get(email__iexact=user_email)

                    billing_address_id = request.POST.get('billing_address_id')
                    phone_number = request.POST.get('phone_number', '')
                    address_line1 = request.POST.get('address_line1', '')
                    address_line2 = request.POST.get('address_line2', '')
                    city = request.POST.get('city', '')
                    state = request.POST.get('state', '')
                    postal_code = request.POST.get('postal_code', '')
                    country = request.POST.get('country', '')

                    billing_address = BillingAddress.objects.get(id=billing_address_id, user=user)
                    billing_address.phone_number = phone_number
                    billing_address.address_line1 = address_line1
                    billing_address.address_line2 = address_line2
                    billing_address.city = city
                    billing_address.state = state
                    billing_address.postal_code = postal_code
                    billing_address.country = country
                    billing_address.save()

                    return JsonResponse({'success': True, 'message': 'Billing address updated successfully.'}, status=200)
                else:
                    return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
            except ObjectDoesNotExist:
                return JsonResponse({'success': False, 'message': 'Billing address not found.'}, status=404)
            except Exception as e:
                return JsonResponse({'success': False, 'message': str(e)}, status=400)
        else:
            return JsonResponse({'success': False, 'message': 'Authorization header not found.'}, status=401)
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)

@csrf_exempt
def get_billing_address(request):
    if request.method == 'POST':
        bearer = request.headers.get('Authorization')
        if bearer is not None:
            try:
                token = bearer.split(' ')[1]
                if auth_customer(token):
                    decoded_token = jwt_decode(token)
                    user_email = decoded_token['email']
                    user = User.objects.get(email__iexact=user_email)

                    billing_address_id = request.POST.get('billing_address_id')
                    billing_address = BillingAddress.objects.get(id=billing_address_id, user=user)

                    return JsonResponse({
                        'success': True,
                        'message': 'Billing address retrieved successfully.',
                        'billing_address': {
                            'id': billing_address.id,
                            'phone_number': billing_address.phone_number,
                            'address_line1': billing_address.address_line1,
                            'address_line2': billing_address.address_line2,
                            'city': billing_address.city,
                            'state': billing_address.state,
                            'postal_code': billing_address.postal_code,
                            'country': billing_address.country,
                        }
                    }, status=200)
                else:
                    return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
            except ObjectDoesNotExist:
                return JsonResponse({'success': False, 'message': 'Billing address not found.'}, status=404)
            except Exception as e:
                return JsonResponse({'success': False, 'message': str(e)}, status=400)
        else:
            return JsonResponse({'success': False, 'message': 'Authorization header not found.'}, status=401)
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)

@csrf_exempt
def list_billing_address(request):
    if request.method == 'POST':
        bearer = request.headers.get('Authorization')
        if bearer is not None:
            try:
                token = bearer.split(' ')[1]
                if auth_customer(token):
                    decoded_token = jwt_decode(token)
                    user_email = decoded_token['email']
                    user = User.objects.get(email__iexact=user_email)

                    billing_address = BillingAddress.objects.filter(user=user).values(
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
                            'message': 'Billing address fetched successfully.',
                            'billing_address': list(billing_address)
                        },
                        status=200
                    )
                else:
                    return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
            except Exception as e:
                return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
        else:
            return JsonResponse({'success': False, 'message': 'Authorization header not found.'}, status=401)
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
@csrf_exempt
def delete_billing_address(request):
    if request.method == 'POST':
        bearer = request.headers.get('Authorization')
        if bearer is not None:
            try:
                token = bearer.split(' ')[1]
                if auth_customer(token):
                    decoded_token = jwt_decode(token)
                    user_email = decoded_token['email']
                    user = User.objects.get(email__iexact=user_email)

                    billing_address_id = request.POST.get('billing_address_id')
                    if not billing_address_id:
                        return JsonResponse({'success': False, 'message': 'Billing address ID is required.'}, status=400)

                    try:
                        billing_address = BillingAddress.objects.get(id=billing_address_id, user=user)
                        billing_address.delete()
                        return JsonResponse({'success': True, 'message': 'Billing address deleted successfully.'}, status=200)
                    except BillingAddress.DoesNotExist:
                        return JsonResponse({'success': False, 'message': 'Billing address not found.'}, status=404)
                else:
                    return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
            except Exception as e:
                return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
        else:
            return JsonResponse({'success': False, 'message': 'Authorization header not found.'}, status=401)
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
