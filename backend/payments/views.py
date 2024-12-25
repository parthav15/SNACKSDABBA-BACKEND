from django.shortcuts import render
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from store.models import Order, Payment
from store.views.user_views import jwt_decode, auth_admin, auth_customer

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@csrf_exempt
def create_payment(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
    try:
        order_id = request.POST.get('order_id')
        if not order_id:
            return JsonResponse({'success': False, 'message': 'Order ID is required.'}, status=400)
        
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Order not found.'}, status=404)
        
        total_price = order.total_price

        razorpay_order = client.Order.create(
            amount=total_price * 100,
            currency = 'INR',
            receipt = f'snacks_dabba_order_{order.id}',
            payment_capture = 1
        )

        payment = Payment.objects.create(
            order=order,
            amount=total_price,
            razorpay_order_id=razorpay_order['id'],
        )
        payment.save()

        return JsonResponse({'success': True, 'message': 'Payment created successfully.', 'razorpay_order_id': razorpay_order['id']}, status=200)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    
@csrf_exempt
def verify_payment(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
    try:
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_signature_id = request.POST.get('razorpay_signature')

        if not razorpay_payment_id or not razorpay_order_id or not razorpay_signature_id:
            return JsonResponse({'success': False, 'message': 'Razorpay Payment ID, Razorpay Order ID, and Razorpay Signature ID are required.'}, status=400)
        
        try:
            payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
        except Payment.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Payment not found.'}, status=404)
        
        verify_signature = client.utility.verify_payment_signature({
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_order_id': razorpay_order_id,
            'razorpay_signature': razorpay_signature_id,
        })

        if verify_signature:
            payment_details = client.payment.fetch(razorpay_payment_id)
            payment_method = payment_details.get('method', '')

            payment.status = 'Paid'
            payment.save()

            order = payment.order
            order.payment_status = 'Paid'
            order.payment_method = payment_method
            order.save()

            return JsonResponse({'success': True, 'message': 'Payment verified successfully.', 'payment_method': payment_method}, status=200)
        else:
            return JsonResponse({'success': False, 'message': 'Payment verification failed.'}, status=400)
    except razorpay.errors.SignatureVerificationError:
        if payment:
            payment.status = 'Failed'
            payment.save()
        return JsonResponse({'success': False, 'message': 'Payment verification failed.'}, status=400)
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)

@csrf_exempt
def get_payment_status(request, order_id):
    if request.method == 'POST':
        try:
            bearer = request.headers.get('Authorization')
            if not bearer:
                return JsonResponse({'success':  False, 'message': 'Authorization header is required.'}, status=400)
            
            token = bearer.split()[1]
            if not auth_customer(token) and not auth_admin(token):
                return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
            
            order = Order.objects.get(id=order_id)
            payment = order.payment
            status = payment.status
            order_status = order.status

            return JsonResponse({'success': True, 'message': 'Payment status retrieved successfully.', 'status': status, 'order_status': order_status}, status=200)
        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Order not found.'}, status=404)
        except Payment.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Payment not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
@csrf_exempt
def refund_payment(request, order_id):
    if request.method == 'POST':
        try:
            bearer = request.headers.get('Authorization')
            if not bearer:
                return JsonResponse({'success': False, 'message': 'Authorization header is required.'}, status=401)
            
            token = bearer.split()[1]
            if not auth_admin(token):
                return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
            
            order = Order.objects.get(id=order_id)
            payment = order.payment
            if payment.status != 'Paid':
                return JsonResponse({'success': False, 'message': 'Payment is not paid yet.'}, status=400)
            
            refund_amount = payment.amount
            refund_currency = 'INR'
            refund_response = client.payment.refund(payment.razorpay_payment_id, {
                'amount': refund_amount * 100,
                'currency': refund_currency,
                'notes': {
                    'order_id': order_id,
                    'reason': 'Customer requested refund.'
                }
            })

            payment.status = 'Refunded'
            payment.refund_response = refund_response
            payment.refund_id = refund_response['id']
            payment.save()

            order.status = 'Refunded'
            order.payment_status = 'Refunded'
            order.save()

            return JsonResponse({'success': True, 'message': 'Payment refunded successfully.'}, status=200)
        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Order not found.'}, status=404)
        except Payment.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Payment not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
@csrf_exempt
def get_refund_status(request, order_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=405)
    
    try:
        bearer = request.headers.get('Authorization')
        if not bearer:
            return JsonResponse({'success':  False, 'message': 'Authorization header is required.'}, status=400)
            
        token = bearer.split()[1]
        if not auth_customer(token) and not auth_admin(token):
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
        
        order = Order.objects.get(id=order_id)
        payment = order.payment
        if payment.status != 'Refunded' and payment.status != 'ParitalRefunded':
            return JsonResponse({'success': False, 'message': 'Payment is not in refunded or partial refunded state.'}, status=400)
        
        refund_id = payment.refund_id

        refund = client.refund.fetch(refund_id)

        refund_status = refund['status']
        refund_amount = refund['amount']
        refund_currency = refund['currency']

        return JsonResponse({
            'success': True,
            'message': 'Refund status retrieved successfully.',
            'refund_status': refund_status,
            'refund_amount': refund_amount,
            'refund_currency': refund_currency
        }, status=200)
    except Order.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Order not found.'}, status=404)
    except Payment.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Payment not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=400)
