from django.urls import path
from . import views
from .webhooks import stripe_webhook


urlpatterns = [
    path('history/', views.PaymentHistoryView.as_view(), name='payment_history'),
    path('success/', views.payment_success, name='payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
    path('webhook/', stripe_webhook, name='stripe_webhook'),
]
