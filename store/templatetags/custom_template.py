from django import template
from Product.models import Category, WishList,WishListItem,Attributes_assoc,Product_categories

register = template.Library()

@register.simple_tag
def check_if_product_in_user_wishlist(request,user_id,product_id):
    try:
        if WishListItem.objects.filter(WishList.objects.filter(user=user_id)).filter(product = product_id).count() > 0:
            return True
        return False
    except Exception as e:
        return False

@register.filter
def get_attribute_values(attribute_name,product_id):
    data = Attributes_assoc.objects.filter(product_attribute__name = attribute_name).filter(product=product_id).filter(active=True)
    return data

@register.filter
def get_products_based_on_category(category_id):
    data = Product_categories.objects.select_related('product').filter(category=category_id)
    return data




