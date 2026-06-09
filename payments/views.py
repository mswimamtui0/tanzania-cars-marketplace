from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import stripe
from django.conf import settings
from reservations.models import Reservation
from .models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def create_payment(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, buyer=request.user)
    
    if request.method == 'POST':
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(reservation.reservation_fee * 100),
                currency='tzs',
                metadata={'reservation_id': reservation.id}
            )
            
            payment = Payment.objects.create(
                user=request.user,
                reservation=reservation,
                amount=reservation.reservation_fee,
                payment_method='stripe',
                stripe_payment_intent_id=intent.id
            )
            
            return render(request, 'payments/process.html', {
                'client_secret': intent.client_secret,
                'payment': payment
            })
        except Exception as e:
            messages.error(request, f'Payment error: {str(e)}')
            return redirect('checkout', reservation_id=reservation.id)
    
    return render(request, 'payments/create.html', {'reservation': reservation})

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, 'whsec_test_webhook_secret')
        
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            payment = Payment.objects.get(stripe_payment_intent_id=payment_intent['id'])
            payment.status = 'completed'
            payment.completed_at = timezone.now()
            payment.save()
            
            # Update reservation status
            payment.reservation.status = 'confirmed'
            payment.reservation.save()
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'status': 'success'})