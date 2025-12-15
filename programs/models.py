from django.db import models
from django.conf import settings
from django.utils.text import slugify
import uuid

class Program(models.Model):
    title = models.CharField(
        max_length=255,
        null=True,
    )
    description = models.TextField(blank=True)
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    is_reg_open = models.BooleanField(default=True)
    start_time = models.DateTimeField(
        null=True,
        blank=True
    )
    reg_deadline = models.DateTimeField(
        null=True,
        blank=True
    )
    location = models.CharField(
        max_length=255,
        blank=True
    )
    category = models.CharField(
        max_length=100,
        blank=True
    )
    
    stripe_product_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    stripe_price_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # This is the link generator
    public_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:200]
        super().save(*args, **kwargs)

    def get_public_link(self, request=None):
        link = f"programs/register/{self.public_id}/"
        if request:
            return request.build_absolute_uri(link)
        return link

    def __str__(self):
        return self.title

class Session(models.Model):
    program = models.ForeignKey(
        Program,
        related_name="sessions",
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.title} ({self.start_date} → {self.end_date})"

class Registration(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    program = models.ForeignKey(
        Program,
        related_name="registrations",
        on_delete=models.CASCADE
    )
    participant_name = models.CharField(max_length=255)
    email = models.EmailField(
        null=True,
        blank=True
    )
    quantity = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("PENDING", "Pending"),
            ("PAID", "Paid"),
            ("CANCELLED", "Cancelled"),
        ],
        default="PENDING"
    )
    # stripe session id or payment id
    payment_reference = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.participant_name} — {self.program.name}"
