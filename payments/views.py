import stripe
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView
from .models import Payment

@login_required
def payment_success(request):
    messages.success(request, "Payment successful! Thank you.")
    return redirect('temp_dashboard')

@login_required
def payment_cancel(request):
    messages.warning(request, "Payment process was canceled.")
    return redirect('temp_dashboard')

class PaymentHistoryView(ListView):
    model = Payment
    template_name = 'payments/payment_history.html'
    context_object_name = 'payments'
    
    def get_queryset(self):
        # Only show payments for the logged-in user
        return Payment.objects.all().order_by('-created_at')
    