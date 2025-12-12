# payments/models.py
from django.db import models
from programs.models import Registration

class Payment(models.Model):
    registration_id = models.ForeignKey(
        Registration,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    name = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    status = models.CharField(
        max_length=10,
        choices=(
            ('PENDING', 'Pending'),
            ('PAID', 'Paid'),
            ('FAILED', 'Failed'),
        ),
        default='PENDING',
    )
    stripe_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return f"{self.name} - {self.amount} ({self.status})"
    