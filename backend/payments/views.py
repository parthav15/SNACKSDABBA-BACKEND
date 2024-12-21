from django.shortcuts import render
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from store.models import Order, Payment

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

        razorpay_order = razorpay.Order.create(
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