from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_user, name='register'),
    path('user_reg/', views.register_user, name='user_reg'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('registration/', RedirectView.as_view(pattern_name='login', permanent=False), name='registration'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),

    # Legacy charity routes → new module
    path(
        'apply/donor/',
        RedirectView.as_view(pattern_name='charity:blood:apply_donor', permanent=False),
        name='apply_donor',
    ),
    path(
        'apply/charity/',
        RedirectView.as_view(pattern_name='charity:medical:apply_recipient', permanent=False),
        name='apply_charity',
    ),
    path(
        'category/<int:category_id>/',
        RedirectView.as_view(url='/charity/', permanent=False),
        name='view_donors',
    ),
    path(
        'send-request/<int:donor_id>/',
        RedirectView.as_view(pattern_name='charity:hub', permanent=False),
        name='send_request',
    ),
    path(
        'respond/<int:request_id>/<str:action>/',
        RedirectView.as_view(pattern_name='charity:my_dashboard', permanent=False),
        name='respond_request',
    ),
    # Legacy registration aliases
    path(
        'charity_user_reg/',
        RedirectView.as_view(pattern_name='charity:hub', permanent=False),
        name='charity_user_reg',
    ),
    path(
        'seller_reg/',
        RedirectView.as_view(pattern_name='register', permanent=False),
        name='seller_reg',
    ),

    # E-Commerce Module
    path('list_product/', views.list_product, name='list_product'),
    path('seller_register/', views.seller_register, name='seller_register'),
    path('seller/dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('add_product/', views.add_product, name='add_product'),
    path('my-products/', views.my_products, name='my_products'),
    path('seller/product/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('seller/product/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('seller/rejected/', views.seller_rejected, name='seller_rejected'),
    path('seller/pending/', views.seller_pending, name='seller_pending'),
    path('seller/entry/', views.seller_entry, name='seller_entry'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),

    # Cart URLs
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/<int:item_id>/', views.update_cart, name='update_cart'),
    path('remove-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    # Checkout & Payment
    path('checkout/', views.checkout_view, name='checkout'),
    path('payment/<int:order_id>/', views.payment_view, name='payment'),
    path('payment-success/', views.payment_success, name='payment_success'),
]
