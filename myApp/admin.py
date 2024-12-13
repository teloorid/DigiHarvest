from django.contrib import admin
from .models import User, Produce, ProduceImage, Cart, CartItem, BillingDetails, Order

# Register the User model
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone_number', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_superuser')

# Register the Produce model
@admin.register(Produce)
class ProduceAdmin(admin.ModelAdmin):
    list_display = ('produce_name', 'farmer', 'quantity', 'price_per_unit', 'status', 'expected_harvest_date')
    search_fields = ('produce_name', 'farmer__username')
    list_filter = ('status', 'organic')

# Register the ProduceImage model
@admin.register(ProduceImage)
class ProduceImageAdmin(admin.ModelAdmin):
    list_display = ('produce', 'created_at')

# Register the Cart model
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')

# Register the CartItem model
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'produce', 'quantity')

# Register the BillingDetails model
@admin.register(BillingDetails)
class BillingDetailsAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'country', 'city', 'postcode')
    search_fields = ('user__username', 'email', 'country', 'city')

# Register the Order model
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_price', 'order_date')
    list_filter = ('order_date',)
