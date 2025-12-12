import stripe
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Payment


@csrf_exempt
def stripe_webhook(request):
    # 1. Verify signature (SECURITY)
    try:
        event = stripe.Webhook.construct_event(
            request.body,
            request.META.get('HTTP_STRIPE_SIGNATURE'),
            settings.STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        return HttpResponseForbidden("Invalid signature")
    except Exception:
        return HttpResponse(status=400)
    
    # 2. Ignore events without reference
    session = event['data']['object']
    payment_id = session.get('client_reference_id')
    if not payment_id:
        print("Event without refernce")
        return HttpResponse(status=200)  
    
    # 3. Handle event types
    match event['type']:
        # Payment succeeded
        case 'checkout.session.completed':
            payment_status = "PAID"
            payment_stripe_id = session.get('id')
        # Payment failed   
        case 'checkout.session.expired':
            payment_status = "FAILED"
            payment_stripe_id = None
        # Ignore other events
        case _:
            print(f"Ignored event: {event['type']}")
            return HttpResponse(status=200)
    
    # 4. Fetch record
    try:
        payment = Payment.objects.get(id=payment_id)
    except Payment.DoesNotExist:
        print(f"Payment {payment_id} not found.")
        return HttpResponse(status=200)

    # 5. Save updates
    payment.status = payment_status
    payment.stripe_id = payment_stripe_id
    payment.save()

    return HttpResponse(status=200)
