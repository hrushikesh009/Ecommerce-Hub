from django.contrib import admin
from . import models


admin.site.register(models.Product)
admin.site.register(models.Coupon)
admin.site.register(models.Payment_gateway)
admin.site.register(models.Shipping_method)
admin.site.register(models.OrderItem)
admin.site.register(models.CartItem)
admin.site.register(models.Coupons_used)
admin.site.register(models.Attributes_assoc)




@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title','parent','active']

class OrderItemInline(admin.TabularInline):
    model = models.OrderItem
    extra = 1

class WishListItemInline(admin.TabularInline):
    model = models.WishListItem
    extra = 1

class CartItemInline(admin.TabularInline):
    model = models.CartItem
    extra = 1


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    inlines =[OrderItemInline]


@admin.register(models.Cart)
class OrderAdmin(admin.ModelAdmin):
    inlines =[CartItemInline]




@admin.register(models.WishList)
class WishlistAdmin(admin.ModelAdmin):
    inlines =[WishListItemInline]
