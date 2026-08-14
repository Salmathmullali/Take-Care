from django.contrib import admin
from .models import CustomUser, CharityOption, DonorApplication, CharityApplication, DonorRequest

@admin.register(DonorApplication)
class DonorAppAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'status', 'applied_at')
    list_filter = ('status',)
    # Admin fills 'admin_message' to explain why they accepted/rejected
    fields = ('user', 'category', 'status', 'admin_message', 'description')

@admin.register(CharityApplication)
class CharityAppAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'status', 'applied_at')
    list_filter = ('status',)
    fields = ('user', 'category', 'status', 'admin_message', 'reason')

admin.site.register(CustomUser)
admin.site.register(CharityOption)
admin.site.register(DonorRequest)


# --- E-Commerce Admin Registration ---
from .models import Product, SellerProfile, Cart, CartItem, Order, OrderItem

admin.site.register(Product)

@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'user', 'is_approved')
    actions = ['approve_seller', 'reject_seller']

    def approve_seller(self, request, queryset):
        for seller in queryset:
            seller.is_approved = True
            seller.save()

            user = seller.user
            user.user_type = CustomUser.SELLER
            user.status = True
            user.save()

        self.message_user(request, "Selected sellers have been approved.")

    def reject_seller(self, request, queryset):
        queryset.update(is_rejected=True, is_approved=False)
        for seller in queryset:
            user = seller.user
            user.user_type = CustomUser.NORMAL
            user.status = False
            user.save()

        self.message_user(request, "Selected sellers have been rejected.")


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at')
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product', 'quantity')
    list_filter = ('cart', 'product')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'status', 'created_at')
    inlines = [OrderItemInline]