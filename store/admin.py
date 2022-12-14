from django.contrib import admin
from . import models

admin.site.register(models.Profile)
admin.site.register(models.contact_us)
admin.site.register(models.Address)

# @admin.register(models.User)
# class UserAdmin(BaseUserAdmin):
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('username', 'password1', 'password2','email','first_name','last_name'),
#         }),
#     )

# @admin.register(models.Product)
# class ProductAdmin(admin.ModelAdmin):
#     autocomplete_fields = ['category']
#     list_display = ['id','image','title','category_title','unit_price','inventory','last_update']
#     list_editable = ['unit_price']
#     list_select_related = ['category']
#     list_per_page = 20
#     search_fields = ['title']
#     list_filter = ['category','last_update','unit_price']

#     @admin.display(ordering='category')
#     def category_title(self,product):
#         return product.category.title



# @admin.register(models.Profile)
# class CustomerAdmin(admin.ModelAdmin):
#     list_display = ['id','username','email','orders','date_joined']
#     list_editable = ['membership']
#     list_select_related = ['user']
#     ordering = ['user__username']
#     list_per_page = 10
#     list_filter = ['user__date_joined','membership']
#     search_fields = ['user__username','user__email']
#     inlines = [AddressInline]

#     @admin.display(ordering='user__date_joined')
#     def date_joined(self,customer):
#         return customer.user.date_joined

#     @admin.display(ordering='user__username')
#     def username(self,customer):
#         return customer.user.username
    
#     @admin.display(ordering='user__email')
#     def email(self,customer):
#         return customer.user.email
    
#     def __str__(self) -> str:
#         return "{}".format(self.user.username)


#     @admin.display(ordering='orders')
#     def orders(self,customer):
#         url = (
#             reverse('admin:store_order_changelist') +
#             '?' +
#             urlencode({
#                 'customer_id' : str(customer.id)
#             })
#         )
#         return  format_html('<a href="{}">{}</a>',url,customer.orders)

#     def get_queryset(self, request):
#         return super().get_queryset(request).annotate(
#             orders = Count('order')
#         )

# class OrderItemInline(admin.TabularInline):
#     model = models.OrderItem
#     extra = 1

# @admin.register(models.Order)
# class OrderAdmin(admin.ModelAdmin):
#     list_display = ['id','customer','payment_status','total_price','placed_at']
#     list_per_page = 10
#     list_editable = ['payment_status']
#     list_filter = ['id','payment_status','placed_at']
#     search_fields = ['customer__user__username']
#     inlines =[OrderItemInline]
#     autocomplete_fields = ['customer']

    
#     def total_price(self,Order):
#         order = models.OrderItem.objects.select_related('product').filter(order_id = Order.id)
#         return sum([(item.quantity * item.product.unit_price)for item in order])

# @admin.register(models.Return)
# class ReturnAdmin(admin.ModelAdmin):
#     list_display = ['id','order','customer','product','quantity','status','placed_at','updated_at']
#     list_per_page = 10
#     list_editable = ['status']
#     list_filter = ['id','status','placed_at','updated_at','order']
#     search_fields = ['order__customer__user__username','product__title']

#     @admin.display(ordering = 'order_id')
#     def order(self,Return):
#         return Return.order.id
    
#     @admin.display(ordering = 'order__customer')
#     def customer(self,Return):
#         return Return.order.customer

    


# @admin.register(models.Category)
# class CategoryAdmin(admin.ModelAdmin):
#     list_display = ['title','products_count']
#     search_fields = ['title']

#     @admin.display(ordering = 'products_count')
#     def products_count(self,category):
#         # syntax reverse('admin:app_model_page)
#         url = (
#             reverse('admin:store_product_changelist') + 
#             '?' +
#             urlencode({
#                 'category__id': str(category.id)
#             }))
#         return format_html('<a href = "{}">{}</a>',url,category.products_count)
        
    
#     def get_queryset(self, request):
#         return super().get_queryset(request).annotate(
#             products_count = Count('products')
            
#         )

# @admin.register(models.Coupon)
# class CouponAdmin(admin.ModelAdmin):
#     list_display = ['title','code','discount','start_date','end_date']
#     list_per_page = 10


# @admin.register(models.CartItem)
# class CartItemAdmin(admin.ModelAdmin):
#     list_display = ['cart','product','quantity']


# admin.site.register(models.Cart)







