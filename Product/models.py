from datetime import date
from uuid import uuid4

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.deletion import CASCADE, PROTECT


class common(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modify_at = models.DateTimeField(auto_now=True)
    created_by= models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_created_by_user',on_delete=models.DO_NOTHING)
    modify_by= models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_modify_by_user',on_delete=models.DO_NOTHING)
    active = models.BooleanField()

    class Meta:
        abstract = True

class Category(common):
    parent = models.ForeignKey('self',blank=True,null=True,related_name="children",on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    

    def __str__(self) -> str:
        return self.title


    class Meta:
        ordering = ['title']
        verbose_name_plural = "categories"

class Product(common):
    title = models.CharField(max_length=100)
    sku = models.CharField(max_length=45)
    short_description = models.CharField(max_length=255)
    long_description = models.TextField(null=True,blank=True)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(1)])
    special_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(1)],null=True,blank=True)
    special_price_from = models.DateField(null=True,blank=True)
    special_price_to = models.DateField(null=True,blank=True)
    quantity = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0)]
    )
    meta_title = models.CharField(max_length=45,blank=True,null=True)
    meta_description = models.TextField(null=True,blank=True)
    meta_keywords = models.TextField(null=True,blank=True)
    is_featured = models.BooleanField()

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ['title']
    
    def check_if_special_price(self):
        if self.special_price:
            if self.special_price_from <= date.today() <= self.special_price_to:
                return True
        return False

    def check_inventory(self):
        if self.quantity <= 0:
            return True
        return False

    def get_attribute_name(self):
        product_attribute = self.attributes_assoc_set.all()
        product_attribute_name = []
        if product_attribute.count() > 0:
            for attribute in product_attribute.filter(active=True):
                if attribute.product_attribute.name not in product_attribute_name:
                    product_attribute_name.append(attribute.product_attribute.name)
            return product_attribute_name
        return None

class Images(common):
    product = models.ForeignKey(Product,on_delete=CASCADE)
    image_name = models.CharField(max_length=100)
    image = models.ImageField()
    

    def __str__(self):
        return self.image_name

class Attributes(common):
    name = models.CharField(max_length=45)

    def __str__(self):
        return self.name


class Attribute_values(common):
    product_attribute = models.ForeignKey(Attributes,on_delete=CASCADE)
    attribute_value = models.CharField(max_length=45)

    def __str__(self):
        return self.attribute_value

class Attributes_assoc(common):
    product = models.ForeignKey(Product,on_delete=CASCADE)
    product_attribute = models.ForeignKey(Attributes,on_delete=CASCADE)
    product_attribute_value = models.ForeignKey(Attribute_values,on_delete=CASCADE)

class Product_categories(common):
    product = models.ForeignKey(Product,on_delete=CASCADE)
    category = models.ForeignKey(Category,on_delete=CASCADE)


class Cart(common):
    id = models.UUIDField(primary_key=True,default=uuid4)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def total_price(self):
        cart_item = self.items.all()
        return sum([(item.quantity * item.unit_price)for item in cart_item])

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return self.user.username



class CartItem(common):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE , related_name = 'items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)]
    )
    attribute = models.JSONField(null=True,blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2,validators=[MinValueValidator(1)])

    class Meta:
        unique_together = [['cart','product']]

    def total(self):
        return (self.quantity * self.unit_price)

class WishList(common):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.user.username

class WishListItem(common):
    wishlist = models.ForeignKey(WishList,on_delete=CASCADE,related_name= 'wishitems')
    product = models.ForeignKey(Product,on_delete=models.CASCADE)

class Shipping_method(common):
    name =  models.CharField(max_length=255)
    delivery_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0)]
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)])

    def __str__(self) -> str:
        return self.name

class Payment_gateway(common):
    name = models.CharField(max_length=45)

    def __str__(self) -> str:
        return self.name

class Order(common):
    STATUS_PENDING = 'P'
    STATUS_PROCESSING = 'O'
    STATUS_SHIPPED = 'S'
    STATUS_DELIVERED = 'D'
    STATUS_CHOICES= [
        (STATUS_PENDING, 'Pending'),
        (STATUS_PROCESSING, 'Processing'),
        (STATUS_SHIPPED, 'Shipped'),
        (STATUS_DELIVERED, 'Delivered')
    ]
    
    id = models.UUIDField(primary_key=True,default=uuid4)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    shipping_method = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(0)])
    AWB_NO = models.CharField(max_length=100)
    payment_gateway = models.ForeignKey(Payment_gateway,on_delete=PROTECT)
    transaction_id = models.CharField(max_length=255,null=True,blank=True)
    placed_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, default=STATUS_PENDING)
    grand_total = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)])
    shipping_charges = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(0)])
    coupon = models.ForeignKey('Coupon',on_delete=PROTECT,null=True,blank=True)
    billing_address = models.TextField()
    billing_city = models.CharField(max_length=100)
    billing_state = models.CharField(max_length=100)
    billing_country =  models.CharField(max_length=100)
    billing_postcode = models.CharField(max_length=45)
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_country =  models.CharField(max_length=100)
    shipping_postcode = models.CharField(max_length=45)


    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return str(self.id)

    def total_price(self):
        order = self.orderitem_set.all()
        return sum([(item.quantity * item.unit_price)for item in order])

    # def set_grand_total(self):
    #     if self.coupon:
    #         self.grand_total =  (self.total_price() + self.shipping_charges) - ((self.total_price() + self.shipping_charges)*(self.coupon.percent_off/100))
    #     else:
    #         self.grand_total =  (self.total_price() + self.shipping_charges)


class OrderItem(common):
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT,related_name='orderitems')
    quantity = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)]
    )
    unit_price = models.DecimalField(max_digits=10, decimal_places=2,validators=[MinValueValidator(1)])
    attribute = models.JSONField(null=True,blank=True)

    def total(self):
        return (self.quantity * self.unit_price)

class Coupon(common):
    code = models.CharField(max_length=45,unique=True)
    percent_off = models.DecimalField(max_digits=10, 
        decimal_places=2,validators=[MinValueValidator(0),MaxValueValidator(100)])
    no_of_uses = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0)]
    )

    def __str__(self) -> str:
        return self.code

class Coupons_used(common):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon,on_delete=CASCADE)



