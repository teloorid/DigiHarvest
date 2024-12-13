from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from django.db.models import Avg
from django.http import HttpResponse, JsonResponse
import csv

from myApp import models
from django.forms.models import model_to_dict
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login
from .models import Produce, Cart, CartItem
from .utils import mpesa_stk_push


# Create your views here.
def home(request):
    produces = Produce.objects.filter(farmer=request.user) if request.user.is_authenticated else []
    return render(request, 'index.html', {'produces': produces})

def signup(request):
    if request.method == 'POST':
        # Collect data from the request
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        role_name = request.POST.get('role', 'farmer')  # Default role is 'farmer'

        # Validate the password confirmation
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('signup')

        # Create the user
        user = models.User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        user.role = role_name
        user.save()

        # Success message after creating the user
        messages.success(request, f'User {user.username} created successfully!')

        # Redirect to the index page
        return redirect('home')

    return render(request, 'login.html')

@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    user = request.user

    if request.method == 'GET':
        # Handle missing profile_pic (default to empty string or placeholder)
        user_data = model_to_dict(user,
                                  fields=['id', 'username', 'email', 'role', 'profile_pic', 'bio', 'phone_number'])

        # Check if profile_pic exists, if not, use a default image or an empty value
        if not user_data.get('profile_pic'):
            user_data['profile_pic'] = 'https://newprofilepic.photo-cdn.net//assets/images/article/profile.jpg?90af0c8'  # or use a default URL e.g., 'https://example.com/default.png'

        return Response(user_data)

    elif request.method == 'PATCH':
        # Update user fields directly
        allowed_fields = ['username', 'email', 'role', 'profile_pic', 'bio', 'phone_number']
        for field in allowed_fields:
            if field in request.data:
                setattr(user, field, request.data[field])
        user.save()

        updated_data = model_to_dict(user,
                                     fields=['id', 'username', 'email', 'role', 'profile_pic', 'bio', 'phone_number'])

        # Ensure profile_pic is not None if not updated
        if not updated_data.get('profile_pic'):
            updated_data['profile_pic'] = ''  # Or use a default image URL

        return Response(updated_data)

    elif request.method == 'DELETE':
        # Delete the user's account
        user.delete()
        return Response({"detail": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

@csrf_exempt
def signin(request):
    if request.method == 'POST':
        # Collect login data from the request
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate the user
        user = authenticate(username=username, password=password)

        if user:
            # Login the user by setting the session data
            login(request, user)

            # Check if user already has a token
            token, created = Token.objects.get_or_create(user=user)

            # Success message after logging in
            messages.success(request, f'Welcome back, {user.username}!')

            # Redirect to the homepage or dashboard
            return redirect('home')  # Change 'home' to your appropriate redirect target

        else:
            # Error message if authentication fails
            messages.error(request, 'Invalid username or password.')

            # Redirect back to the login page
            return redirect('signin')  # Change 'login' to your login URL name

    return render(request, 'login.html')

def remove_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect("cart")



# List Produce (GET)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def produce_list(request):
    # Only show produce for the authenticated user
    produces = models.Produce.objects.all().order_by('id')
    total_count = produces.count()
    produce_data = [
        {
            'produce_name': produce.produce_name,
            'quantity': produce.quantity,
            'status': produce.status,
            'expected_harvest_date': produce.expected_harvest_date,
            'actual_harvest_date': produce.actual_harvest_date
        }
        for produce in produces
    ]
    return render(request, 'market.html', {'produces': produces, 'total_count': total_count })


# Create Produce (POST)
@permission_classes([permissions.IsAuthenticated])
@login_required
def produce_create(request):
    if request.method == 'POST':
        # Collect data from the request
        produce_name = request.POST.get('produce_name')
        quantity = request.POST.get('quantity')
        expected_harvest_date = request.POST.get('expected_harvest_date')
        planting_date = request.POST.get('planting_date')
        description = request.POST.get('description', '')  # Optional field
        price_per_unit = request.POST.get('price_per_unit')
        organic = request.POST.get('organic', 'true') == 'true'  # Convert to boolean
        status = request.POST.get('status', 'Planted')  # Default status is 'Planted'
        image_files = request.FILES.getlist('image_files')  # Multiple file uploads

        # Validate required fields
        if not (produce_name and quantity and expected_harvest_date and planting_date and price_per_unit):
            messages.error(request, 'All required fields must be filled out.')
            return redirect('produce_create')

        # Create the produce entry
        produce = models.Produce.objects.create(
            farmer=request.user,
            produce_name=produce_name,
            quantity=quantity,
            expected_harvest_date=expected_harvest_date,
            planting_date=planting_date,
            description=description,
            price_per_unit=price_per_unit,
            organic=organic,
            status=status,
        )

        # Handle image uploads
        for image_file in image_files:
            models.ProduceImage.objects.create(produce=produce, image=image_file)

        # Success message after creating the produce
        messages.success(request, f'Produce "{produce_name}" created successfully!')

        # Redirect to the produce list or home page
        return redirect('produce_create')

    return render(request, 'produce-create.html')

def update_cart_quantity(request, item_id):
    if request.method == "POST":
        # Get the cart item
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

        # Get the new quantity from the request
        new_quantity = int(request.POST.get("quantity", cart_item.quantity))

        # Update the quantity
        if new_quantity > 0:
            cart_item.quantity = new_quantity
            cart_item.save()
            messages.success(request, "Quantity updated successfully.")
        else:
            messages.error(request, "Quantity must be greater than zero.")

    # Redirect back to the cart page
    return redirect("cart")


# Update Produce (PUT/PATCH)
@api_view(['PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def produce_update(request, pk):
    try:
        produce = models.Produce.objects.get(pk=pk, farmer=request.user)
    except models.Produce.DoesNotExist:
        return Response({"detail": "Produce not found."}, status=status.HTTP_404_NOT_FOUND)

    # Check if status is changing from Harvested
    new_status = request.data.get("status", produce.status)
    valid_statuses = ['Planted', 'Growing', 'Harvested']

    if new_status not in valid_statuses:
        return Response({"status": "Invalid status value."}, status=status.HTTP_400_BAD_REQUEST)
    if produce.status == "Harvested" and new_status != "Harvested":
        return Response({"status": "Once harvested, status cannot change."}, status=status.HTTP_400_BAD_REQUEST)

    # Update the produce fields
    produce.produce_name = request.data.get('produce_name', produce.produce_name)
    produce.quantity = request.data.get('quantity', produce.quantity)
    produce.expected_harvest_date = request.data.get('expected_harvest_date', produce.expected_harvest_date)
    produce.planting_date = request.data.get('planting_date', produce.planting_date)
    produce.description = request.data.get('description', produce.description)
    produce.price_per_unit = request.data.get('price_per_unit', produce.price_per_unit)
    produce.status = new_status

    # Handle image files if provided
    image_files = request.data.get('image_files', [])
    for image_file in image_files:
        models.ProduceImage.objects.create(produce=produce, image=image_file)

    produce.save()
    return Response({"produce_name": produce.produce_name}, status=status.HTTP_200_OK)

@login_required
def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))

        # Get the product object
        product = Produce.objects.get(id=product_id)

        # Get or create the cart for the user
        cart, created = models.Cart.objects.get_or_create(user=request.user)

        # Check if the product is already in the cart
        cart_item, created = models.CartItem.objects.get_or_create(cart=cart, produce=product)

        # If the product is already in the cart, update the quantity
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return JsonResponse({
            "success": True,
            "message": f"{product.produce_name} added to cart.",
            "cartItemCount": cart.items.count()  # Example: Total items in the cart
        })

    return JsonResponse({"success": False, "message": "Invalid request."}, status=400)

@login_required
def cart_view(request):
    try:
        cart = models.Cart.objects.get(user=request.user)
    except models.Cart.DoesNotExist:
        cart = None

    return render(request, 'cart.html', {'cart': cart})

def checkout(request):
    cart = models.Cart.objects.get(user=request.user)
    return render(request, 'checkout.html', {'cart': cart})

def checkout_process(request):
    if request.method == 'POST':
        # Get billing details from the form
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        company_name = request.POST.get('company_name')
        country = request.POST.get('country')
        street_address = request.POST.get('street_address')
        apartment = request.POST.get('apartment')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postcode = request.POST.get('postcode')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        order_notes = request.POST.get('order_notes')

        # Save billing details to the database
        billing_details = models.BillingDetails.objects.create(
            user=request.user,
            first_name=first_name,
            last_name=last_name,
            company_name=company_name,
            country=country,
            street_address=street_address,
            apartment=apartment,
            city=city,
            state=state,
            postcode=postcode,
            phone=phone,
            email=email,
            order_notes=order_notes,
        )
        billing_details.save()

        cart = models.Cart.objects.get(user=request.user)

        # Assume cart is already handled and total is calculated
        total_amount = cart.total_price()

        # Convert Decimal to float
        total_amount_float = float(total_amount)

        # Trigger M-Pesa STK Push for payment
        mpesa_response = mpesa_stk_push(phone, total_amount_float)

        if mpesa_response.get('ResponseCode') == '0':
            # Redirect to a success page or render a success template
            return redirect('checkout')
        else:
            # Handle failure (e.g., show an error message)
            print(mpesa_response.get('ResponseCode'))
            return JsonResponse({'error': 'Payment initiation failed'}, status=400)
    else:
        return redirect('checkout')  # Handle GET request



# Export Produce Data (CSV)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def produce_export(request):
    produces = models.Produce.objects.filter(farmer=request.user)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="produce.csv"'
    writer = csv.writer(response)
    writer.writerow(['Produce Name', 'Quantity', 'Status', 'Expected Harvest Date', 'Actual Harvest Date'])

    for produce in produces:
        writer.writerow([produce.produce_name, produce.quantity, produce.status, produce.expected_harvest_date,
                         produce.actual_harvest_date])
    return response


# Subscribe to Notifications (POST)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def produce_subscribe(request):
    # Logic to subscribe the user to notifications
    return Response({"message": "Subscribed to notifications."}, status=status.HTTP_200_OK)


# Insights (GET)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def produce_insights(request):
    queryset = models.Produce.objects.filter(farmer=request.user)
    stats = {
        "total_produce": queryset.count(),
        "harvested": queryset.filter(status='Harvested').count(),
        "growing": queryset.filter(status='Growing').count(),
        "planted": queryset.filter(status='Planted').count(),
        "average_quantity": queryset.aggregate(avg=Avg('quantity'))['avg'],
        "top_produce_by_quantity": queryset.order_by('-quantity').first()
    }
    stats['top_produce_by_quantity'] = stats['top_produce_by_quantity'].produce_name if stats[
        'top_produce_by_quantity'] else None
    return Response(stats)


# Share Produce Link (POST)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def produce_share(request, pk):
    try:
        produce = models.Produce.objects.get(pk=pk, farmer=request.user)
    except models.Produce.DoesNotExist:
        return Response({"detail": "Produce not found."}, status=status.HTTP_404_NOT_FOUND)

    link = f"https://yourdomain.com/produce/{pk}/share"
    return Response({"link": link}, status=status.HTTP_200_OK)


# Marketplace Produce (GET)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def produce_marketplace(request):
    produces = models.Produce.objects.filter(status='Harvested')
    produce_data = [
        {
            'produce_name': produce.produce_name,
            'quantity': produce.quantity,
            'status': produce.status,
            'expected_harvest_date': produce.expected_harvest_date,
            'actual_harvest_date': produce.actual_harvest_date
        }
        for produce in produces
    ]
    return Response(produce_data)
