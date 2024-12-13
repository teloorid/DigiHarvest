from django.db import models
from django.conf import settings
from django.utils.timezone import now
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    FARMER = 'Farmer'
    SELLER = 'Seller'
    DISTRIBUTOR = 'Distributor'
    ADMIN = 'Admin'

    ROLE_CHOICES = [
        (FARMER, 'Farmer'),
        (SELLER, 'Seller'),
        (DISTRIBUTOR, 'Distributor'),
        (ADMIN, 'Admin'),
    ]

    profile_pic = models.ImageField(upload_to='uploads/profile_pics/', null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return self.username

class Produce(models.Model):
    ORGANIC_CHOICES = [
        (True, 'Organic'),
        (False, 'Inorganic'),
    ]

    STATUS_CHOICES = [
        ('Planted', 'Planted'),
        ('Growing', 'Growing'),
        ('Harvested', 'Harvested'),
        ('Failed', 'Failed'),
        ('Delayed', 'Delayed'),
    ]

    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='produce')
    produce_name = models.CharField(max_length=255)
    organic = models.BooleanField(choices=ORGANIC_CHOICES, default=True)
    quantity = models.FloatField(help_text="Amount in kilograms or tons")
    expected_harvest_date = models.DateField()
    planting_date = models.DateField()
    description = models.TextField()
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    actual_harvest_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Planted')
    status_last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(default=now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.produce_name} ({self.status}) - {self.farmer.username}"

class ProduceImage(models.Model):
    produce = models.ForeignKey(Produce, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='uploads/produce_images/')
    created_at = models.DateTimeField(default=now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Image for {self.produce.produce_name}"


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return sum(item.produce.price_per_unit * item.quantity for item in self.items.all())

    def __str__(self):
        return f"Cart for {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    produce = models.ForeignKey(Produce, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.produce.produce_name} x {self.quantity}"

    @property
    def total_price(self):
        return self.produce.price_per_unit * self.quantity

class BillingDetails(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='billing_details')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    company_name = models.CharField(max_length=200, blank=True, null=True)
    country = models.CharField(max_length=100)
    street_address = models.CharField(max_length=255)
    apartment = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postcode = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    order_notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name} - {self.country}'

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    billing_details = models.ForeignKey(BillingDetails, on_delete=models.SET_NULL, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Order {self.id} - {self.user.username}'

