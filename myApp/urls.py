from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from myApp import views

urlpatterns = [
    # Home Page
    path('', views.home, name='home'),

    # Authentication
    path('auth/signup/', views.signup, name='signup'),
    path('auth/signin/', views.signin, name='signin'),

    #User Profile
    path('profile/', views.user_profile, name='user_profile'),

    # Produce endpoints
    path('produce/', views.produce_list, name='produce_list'),
    path('produce/create/', views.produce_create, name='produce_create'),
    path('produce/update/<int:pk>/', views.produce_update, name='produce_update'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout-process/', views.checkout_process, name='checkout_process'),
    path('cart/update/<int:item_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('cart/remove/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)