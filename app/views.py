from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum
from decimal import Decimal
import razorpay
from django.conf import settings

from .forms import LoginForm, MyUserCreationForm, ProductForm
from .models import CustomUser, Product, SellerProfile, Cart, CartItem, Order, OrderItem
from .decorators import seller_required


def home(request):
    return render(request, 'index.html')


def register_user(request):
    if request.user.is_authenticated:
        return redirect('charity:my_dashboard')
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome to Take Care! Your account was created.')
            return redirect('charity:my_dashboard')
    else:
        form = MyUserCreationForm()
    return render(request, 'auth/register.html', {'form': form})


class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'auth/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        if hasattr(user, 'user_type') and user.user_type == CustomUser.SELLER:
            return reverse_lazy('seller_dashboard')
        return self.get_redirect_url() or reverse_lazy('charity:my_dashboard')


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required
def user_dashboard(request):
    return redirect('charity:my_dashboard')


# ==========================================
# E-COMMERCE MODULE VIEWS
# ==========================================

@login_required
def seller_register(request):
    # Already approved seller
    if request.user.user_type == CustomUser.SELLER and request.user.status:
        return redirect('seller_dashboard')

    if request.method == 'POST':
        seller, created = SellerProfile.objects.get_or_create(
            user=request.user,
            defaults={
                'business_name': request.POST.get('business_name'),
                'tax_id': request.POST.get('tax_id'),
                'category': request.POST.get('category'),
            }
        )

        # If already exists → just go to pending
        if not created:
            return redirect('seller_pending')

        request.user.user_type = CustomUser.SELLER
        request.user.status = False
        request.user.save()

        return redirect('seller_pending')

    return render(request, 'seller/seller_register.html')


@login_required
def seller_dashboard(request):
    try:
        seller = request.user.seller_profile
    except SellerProfile.DoesNotExist:
        return redirect('seller_register')

    # 1. Check rejection FIRST
    if seller.is_rejected:
        return redirect('seller_rejected')

    # 2. Check if they are still pending
    if not seller.is_approved:
        return redirect('seller_pending')

    # 3. If neither, show dashboard
    return render(request, 'seller/dashboard.html')


@login_required
def seller_entry(request):
    try:
        seller = request.user.seller_profile
    except SellerProfile.DoesNotExist:
        return redirect('seller_register')

    # Always check rejection as the priority
    if seller.is_rejected:
        return redirect('seller_rejected')

    if not seller.is_approved:
        return redirect('seller_pending')

    return redirect('seller_dashboard')


@login_required
def seller_rejected(request):
    try:
        seller = request.user.seller_profile
    except SellerProfile.DoesNotExist:
        return redirect('seller_register')
    return HttpResponse(f"REJECTED ❌<br>Reason: {seller.rejection_reason}")


@login_required
def seller_pending(request):
    try:
        seller = request.user.seller_profile
        seller.refresh_from_db()
    except Exception:
        return redirect('seller_dashboard')

    # If approved → dashboard
    if seller.is_approved:
        if seller.is_rejected:
            seller.is_rejected = False
            seller.rejection_reason = ""
            seller.save()
        return redirect('seller_dashboard')

    return render(request, 'seller/seller_pending.html', {'seller': seller})


@login_required
@seller_required
def add_product(request):
    if request.method == 'POST':
        Product.objects.create(
            name=request.POST.get('name'),
            price=request.POST.get('price'),
            description=request.POST.get('description'),
            stock=request.POST.get('stock'),
            image=request.FILES.get('image'),
            created_by=request.user
        )
        return redirect('seller_dashboard')

    return render(request, 'seller/add_product.html')


@login_required
@seller_required
def my_products(request):
    products = Product.objects.filter(created_by=request.user)
    return render(request, 'seller/my_products.html', {'products': products})


@login_required
@seller_required
def edit_product(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        created_by=request.user
    )

    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.price = request.POST.get('price')
        product.stock = request.POST.get('stock')
        product.description = request.POST.get('description')

        if request.FILES.get('image'):
            product.image = request.FILES.get('image')

        product.save()
        return redirect('my_products')

    return render(request, 'seller/edit_product.html', {'product': product})


@login_required
@seller_required
def delete_product(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        created_by=request.user
    )
    product.delete()
    return redirect('my_products')


def list_product(request):
    products = Product.objects.all().order_by('-created_at')
    cart_count = 0

    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_count = cart.items.count()
        except Cart.DoesNotExist:
            cart_count = 0

    return render(request, 'shopping/list_product.html', {
        'products': products,
        'cart_count': cart_count
    })


def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'shopping/product_details.html', {
        'product': product
    })


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    # Recalculate cart count for the session/header
    total_qty = cart.items.aggregate(total=Sum('quantity'))['total'] or 0
    request.session['cart_count'] = total_qty 
    
    return redirect('cart')


@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    total_price = sum(item.subtotal() for item in cart_items)

    return render(request, 'cart/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'cart_count': cart_items.count()
    })


@login_required
def update_cart(request, item_id):
    cart_item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )

    if request.method == "POST":
        action = request.POST.get('action')
        
        # 1. Handle the Plus/Minus Button Clicks
        if action == 'increase':
            cart_item.quantity += 1
            cart_item.save()
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
        
        # 2. Handle Manual Input
        else:
            try:
                quantity = int(request.POST.get('quantity', 1))
            except (ValueError, TypeError):
                quantity = 1
            if quantity > 0:
                cart_item.quantity = quantity
                cart_item.save()
            else:
                cart_item.delete()

    return redirect('cart')


@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart = cart_item.cart
    cart_item.delete()

    # Recalculate cart count for the session/header
    total_qty = cart.items.aggregate(total=Sum('quantity'))['total'] or 0
    request.session['cart_count'] = total_qty

    return redirect('cart')


@login_required
def checkout_view(request):
    cart = get_object_or_404(Cart, user=request.user)
    items = cart.items.all()

    if not items.exists():
        return redirect('list_product')

    total_price = sum(item.subtotal() for item in items)

    if request.method == 'POST':
        order = Order.objects.create(
            user=request.user,
            full_name=request.POST['full_name'],
            phone=request.POST['phone'],
            address=request.POST['address'],
            city=request.POST['city'],
            pincode=request.POST['pincode'],
            total_price=total_price,
            status='Pending'
        )

        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=item.product.price,
                quantity=item.quantity
            )

        # Clear cart items upon proceeding to checkout/payment
        items.delete()

        return redirect('payment', order_id=order.id)

    return render(request, 'cart/checkout.html', {
        'cart_items': items,
        'total_price': total_price
    })


@login_required
def payment_view(request, order_id):
    # Initialize Razorpay client
    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    # Fetch order and cast price
    order = get_object_or_404(Order, id=order_id, user=request.user)
    amount = int(order.total_price)

    # Create Razorpay order
    razorpay_order = client.order.create({
        "amount": amount * 100,  # paise
        "currency": "INR",
        "payment_capture": 1
    })

    # Update order with razorpay ID
    order.razorpay_order_id = razorpay_order["id"]
    order.status = 'Paid'
    order.save()

    context = {
        "order_id": razorpay_order["id"],
        "amount": amount,
        "razorpay_key": settings.RAZORPAY_KEY_ID
    }
    return render(request, "payment/payment.html", context)


@login_required
def payment_success(request):
    return HttpResponse("🎉 Payment Successful")
