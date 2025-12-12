from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount', 'status', 'stripe_id', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'stripe_id')
