import json
import logging

from custom_admin.models import Banner_images, EmailTemplate
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.auth.views import (PasswordChangeView,
                                       PasswordResetConfirmView,
                                       PasswordResetDoneView,
                                       PasswordResetView)
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models.query_utils import Q
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.urls.base import reverse
from django.utils.html import strip_tags
from django.views.generic import CreateView
from django.views.generic.edit import UpdateView
from mailchimp_marketing import Client
from mailchimp_marketing.api_client import ApiClientError
from Product.models import (Cart, CartItem, Category, Coupon, Coupons_used,
                            Order, OrderItem, Payment_gateway, Product,
                            Product_categories, WishList, WishListItem)
from User.models import User

from store.decorators import unauthenticated_user
from store.forms import (AddressForm, BillAddressForm, ContactUsForm,
                         LoginForm, MyPasswordChangeForm, ProfileUpdateForm,
                         SignUpForm, TrackOrdersForm)
from store.helper import check_categorys_children, mail
from store.models import Address, contact_us


# Mailchimp Settings
api_key = settings.MAILCHIMP_API_KEY
server = settings.MAILCHIMP_DATA_CENTER
list_id = settings.MAILCHIMP_EMAIL_LIST_ID

logger = logging.getLogger('django')


def page_not_found_view(request, exception):
    return render(request, 'store/404.html', status=404)


def server_error_view(request):
    return render(request, 'store/500.html', status=500)


def HomeView(request):
    try:
        if request.method == 'GET':
            if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                min = request.GET['min']
                max = request.GET['max']
                store_url = '/store/?min={}&max={}'.format(min, max)
                response = {'url': store_url}
                return HttpResponse(json.dumps(response), content_type='application/json')
            else:
                try:
                    min = request.GET['min']
                    max = request.GET['max']
                except Exception as e:
                    min = 0
                    max = 1000
                featured_products = Product.objects.filter(is_featured=True).filter(
                    active=True).filter(price__gte=int(min), price__lte=int(max))
                categories = Category.objects.filter(
                    parent=None).filter(active=True)
                featured_categories = Category.objects.all()
                banner = Banner_images.objects.select_related('banner').filter(
                    banner__banner_path='/home/').filter(active=True)

                context = {
                    'categories': categories,
                    'featured_products': featured_products,
                    'featured_categories': featured_categories,
                    'banner': banner

                }
                return render(request, 'store/home.html', context=context)

    except Exception as e:
        logger.error(e)
        messages.error(request, 'Something Went Wrong!')
        return render(request, 'store/home.html')


@unauthenticated_user
def LoginView(request):
    try:
        signupform = SignUpForm()
        loginform = LoginForm()
        if request.method == 'POST' and 'Signup' in request.POST:
            signupform = SignUpForm(request.POST)
            if signupform.is_valid():
                signupform.save()
                uname = signupform.cleaned_data.get('username')
                pwd = signupform.cleaned_data.get('password1')
                user = authenticate(request, username=uname, password=pwd)
                if user is not None:
                    login(request, user)
                    group = Group.objects.get(name='customer')
                    group.user_set.add(user)
                    mail(
                        id=1,
                        context={'Email': user,
                                 'Username': user.username, 'Password': pwd},
                        user_email=[user]
                    )
                    admin_users = Group.objects.get(
                        name='admin').user_set.all()
                    mail(
                        id=5,
                        context={'Email': user, 'Username': user.username},
                        user_email=[user.email for user in admin_users]
                    )

                    messages.success(
                        request, 'Hii {}!, Email has been send to your registered Email Address with login credentails :)'.format(user.username))
                    return redirect('store:home-view')
                else:
                    messages.info(request, 'Something Went Wrong !')
                    return redirect('/store/login/')

        if request.method == 'POST' and 'Login' in request.POST:
            loginform = LoginForm(request, request.POST)
            if loginform.is_valid():

                uname = loginform.cleaned_data.get('username')
                pwd = loginform.cleaned_data.get('password')
                user = authenticate(request, username=uname, password=pwd)
                if user is not None:
                    login(request, user)
                    return redirect('store:home-view')
                else:
                    messages.warning(request, 'hi')

    except Exception as e:
        logger.error(e)
        messages.error(request, 'Something Went Wrong!')
    return render(request, 'store/login.html', {'signupform': signupform, 'loginform': loginform})


def LogoutView(request):
    try:
        logout(request)
    except Exception as e:
        logger.error(e)
    return redirect('store:home-view')


class MyPasswordResetView(PasswordResetView):
    email_template_name = 'default_email_template.html'
    template_name = "store/password-reset.html"
    from_email = settings.EMAIL_HOST_USER
    success_url = reverse_lazy('store:password_reset_done')
    html_email_template_name = 'default_email_template.html'

    def dispatch(self, *args, **kwargs):
        try:
            htmly = EmailTemplate.objects.get(id=2)
            open('store/templates/default_email_template.html', 'w').close()
            file = open('store/templates/default_email_template.html', 'w')
            file.write(htmly.content)
            file.close()
            return super(MyPasswordResetView, self).dispatch(*args, **kwargs)
        except Exception as e:
            logger.error(e)


class MyPasswordResetDoneView(PasswordResetDoneView):
    template_name = "store/password-reset-done.html"


class MyPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "store/password-reset-confirm.html"
    success_url = reverse_lazy('store:login-view')


class ContactUsView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    login_url = '/store/login/'
    model = contact_us
    form_class = ContactUsForm
    template_name = "store/contact-us.html"
    success_message = 'Your Message was Sent Successfully!'
    error_message = "Error sending the Message, check fields below."

    def form_valid(self, form):
        try:
            form.instance.created_by = self.request.user
            form.instance.modify_by = self.request.user
            Name = form.cleaned_data['name']
            Email = form.cleaned_data['email']
            Message = form.cleaned_data['message']
            Contact = form.cleaned_data['contact_no']
            admin_users = Group.objects.get(name='admin').user_set.all()
            mail(
                id=6,
                context={'Name': Name, 'Email': Email,
                         'Message': Message, 'Contact': Contact},
                user_email=[user.email for user in admin_users]
            )

            return super().form_valid(form)
        except Exception as e:
            logger.error(e)

    def get_success_url(self) -> str:
        try:
            return reverse('store:contact-us-view')
        except Exception as e:
            logger.error(e)


class ProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    login_url = '/store/login/'
    model = User
    form_class = ProfileUpdateForm
    template_name = "store/myaccount.html"
    success_message = 'Your Account was Updated Successfully!'
    error_message = "Error updating the Account, check fields below."

    def get_object(self, queryset=None):
        try:
            return self.request.user
        except Exception as e:
            logger.error(e)

    def get_success_url(self) -> str:
        try:
            return reverse('store:myaccount-view')
        except Exception as e:
            logger.error(e)


class MyPasswordChangeView(LoginRequiredMixin, SuccessMessageMixin, PasswordChangeView):
    login_url = '/store/login/'
    form_class = MyPasswordChangeForm
    template_name = "store/change-password.html"
    success_message = 'Your Password was Updated Successfully!'
    error_message = "Error updating the Password, check fields below."

    def get_success_url(self) -> str:
        try:
            return reverse('store:password-change-view')
        except Exception as e:
            logger.error(e)


def ProductDetailView(request, pk):
    try:
        product = Product.objects.get(id=pk)
        categories = Category.objects.filter(parent=None).filter(active=True)
        context = {
            'product': product,
            'categories': categories,
        }
        return render(request, 'store/product-details.html', context=context)

    except Exception as e:
        logger.error(e)
        messages.error(request, 'Something Went Wrong')
        return render(request, 'store/product-details.html')


def CategoryView(request, category_title):
    try:
        if request.method == 'GET':
            if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                min = request.GET['min']
                max = request.GET['max']
                category_url = '/store/category/{}/?min={}&max={}'.format(
                    category_title, min, max)
                response = {'url': category_url}
                return HttpResponse(json.dumps(response), content_type='application/json')
            else:
                try:
                    min = request.GET['min']
                    max = request.GET['max']
                except Exception as e:
                    min = 0
                    max = 1000
                categories = Category.objects.filter(
                    parent=None).filter(active=True)
                product = Product_categories.objects.filter(
                    category_id__in=check_categorys_children(
                        category_queryset=Category.objects.get(title=category_title))
                ).filter(active=True)
                products = Product.objects.filter(id__in=[p.product.id for p in product]).filter(
                    price__gte=int(min), price__lte=int(max))
                p = Paginator(products, 1)
                page = request.GET.get('page')
                product_list = p.get_page(page)
                page_nums = "a" * product_list.paginator.num_pages
                context = {
                    'categories': categories,
                    'product_list': product_list,
                    'page_nums': page_nums
                }
                return render(request, 'store/shop.html', context=context)
    except Exception as e:
        logger.error(e)
        messages.error(request, 'Something Went Wrong!')
        return render(request, 'store/shop.html')


@login_required(login_url='store:login-view')
def WishListView(request):
    try:
        try:
            wishlistitem = WishListItem.objects.select_related('product').filter(
                wishlist=WishList.objects.get(user=request.user.id))
        except WishList.DoesNotExist:
            wishlist_obj = WishList()
            wishlist_obj.user = User(pk=request.user.id)
            wishlist_obj.created_by = User(pk=request.user.id)
            wishlist_obj.modify_by = User(pk=request.user.id)
            wishlist_obj.active = True
            wishlist_obj.save()
            return redirect('store:wish-list-view')
        return render(request, 'store/wishlist.html', {'wishlistitems': wishlistitem})

    except Exception as e:
        logger.error(e)
        messages.error(request, 'Something Went Wrong!')
        return render(request, 'store/wishlist.html')


def WishListAddView(request, pk):
    try:
        if request.user.is_authenticated:
            try:
                query = WishList.objects.get(user=request.user.id)
            except WishList.DoesNotExist:
                wishlist_obj = WishList()
                wishlist_obj.user = User(pk=request.user.id)
                wishlist_obj.created_by = User(pk=request.user.id)
                wishlist_obj.modify_by = User(pk=request.user.id)
                wishlist_obj.active = True
                wishlist_obj.save()
                query = WishList.objects.get(id=wishlist_obj.id)
            if query:
                if WishListItem.objects.filter(wishlist=query.id).filter(product=pk).count() > 0:
                    messages.info(
                        request, "Product is already in the Wishlist :)")
                    return redirect('store:wish-list-view')

                wishlistitem_obj = WishListItem()
                wishlistitem_obj.wishlist = WishList(pk=query.id)
                wishlistitem_obj.product = Product(id=pk)
                wishlistitem_obj.created_by = User(pk=request.user.id)
                wishlistitem_obj.modify_by = User(pk=request.user.id)
                wishlistitem_obj.active = True
                wishlistitem_obj.save()
                return redirect('store:wish-list-view')
        else:
            messages.warning(
                request, "This functionality is restricted for login User! Please login First")
            return redirect('store:login-view')
    except Exception as e:
        logger.error(e)
        messages.error(request, "Something Went Wrong!")
        return redirect('store:wish-list-view')


@login_required(login_url='store:login-view')
def WishListDeleteView(request, pk):
    try:
        if request.method == "POST":
            name = request.POST.get('name')
            if name == 'WishList':
                if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                    obj = get_object_or_404(WishListItem, id=pk)
                    obj.delete()
            return redirect('store:wish-list-view')
    except Exception as e:
        logger.error(e)
        messages.error(request, "Something Went Wrong!")
        return redirect('store:wish-list-view')


@login_required(login_url='store:login-view')
def AddressListView(request):
    try:
        if request.method == "GET":
            address = Address.objects.filter(user=request.user.id).all()
            return render(request, 'store/address-list.html', {'address': list(address)})
    except Exception as e:
        logger.error(e)
        messages.error(request, "Something Went Wrong!")
        return render(request, 'store/address-list.html')


class AddressAddView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    login_url = '/admin/login/'
    model = Address
    form_class = AddressForm
    template_name = "store/address-add.html"
    success_message = 'Your Address was saved Successfully!'
    error_message = "Error saving the Address, check fields below."

    def form_valid(self, form):
        try:
            form.instance.user = self.request.user
            if Address.objects.filter(user=self.request.user.id).filter(address=form.instance.address).count() > 0:
                messages.info(self.request, "Address Already Exists :)")
                return HttpResponseRedirect('/store/address/add/')
            return super().form_valid(form)
        except Exception as e:
            logger.error(e)

    def form_submit(self, request):
        try:
            if request.method == 'POST':
                form = AddressForm(request.POST)
                if form.is_valid():
                    form.save()
                else:
                    messages.error(self.request, self.error_message)
                    return HttpResponseRedirect('/store/address/add/')
            return redirect('/store/address/')
        except Exception as e:
            logger.error(e)

    def get_success_url(self) -> str:
        try:
            return reverse('store:address-view')
        except Exception as e:
            logger.error(e)


class AddressEditView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    login_url = '/admin/login/'
    model = Address
    form_class = AddressForm
    template_name = "store/address-edit.html"
    success_message = 'Your Address was Updated Successfully!'
    error_message = "Error updating the Address, check fields below."

    def form_valid(self, form):
        try:
            form.instance.user = self.request.user
            return super().form_valid(form)
        except Exception as e:
            logger.error(e)

    def get_success_url(self) -> str:
        try:
            return reverse('store:address-view')
        except Exception as e:
            logger.error(e)


@login_required(login_url='store:login-view')
def AddressDeleteView(request, pk):
    try:
        if request.method == "POST":
            name = request.POST.get('name')
            if name == 'Address':
                if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                    obj = get_object_or_404(Address, id=pk)
                    obj.delete()
            return redirect('store:address-view')
    except Exception as e:
        logger.error(e)
        messages.error(request, "Something Went Wrong!")
        return redirect('store:address-view')


@login_required(login_url='store:login-view')
def CartListView(request):
    try:
        print("out")
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            print('in')
            cart_id = request.GET.get('cart_id')
            name = request.GET.get('name')
            if name == 'plus_cart':
                original_quantity = CartItem.objects.get(id=cart_id)
                if original_quantity.quantity + 1 <= original_quantity.product.quantity:
                    CartItem.objects.filter(id=cart_id).update(
                        quantity=original_quantity.quantity+1)
                else:
                    messages.warning(request, "The Max quantity is reached!")
                    return redirect('store:cart-list-view')

            elif name == 'minus_cart':
                original_quantity = CartItem.objects.get(id=cart_id)
                if original_quantity.quantity - 1 >= 1:
                    CartItem.objects.filter(id=cart_id).update(
                        quantity=original_quantity.quantity-1)
                else:
                    messages.warning(request, "The Min quantity is reached!")
                    return redirect('store:cart-list-view')

            elif name == "cart_quantity_changed":
                original_quantity = CartItem.objects.get(id=cart_id)
                if request.GET.get('value').isdigit():
                    if int(request.GET.get('value')) <= 0:
                        CartItem.objects.filter(id=cart_id).update(quantity=1)
                    elif int(request.GET.get('value')) <= original_quantity.product.quantity:
                        CartItem.objects.filter(id=cart_id).update(
                            quantity=request.GET.get('value'))
                    else:
                        messages.warning(
                            request, "The Max quantity is reached!")
                        return redirect('store:cart-list-view')
    except Exception as e:
        logger.error(e)
        messages.error(request, 'Something Went Wrong')
        return redirect('store:cart-list-view')

    try:
        try:
            cart_detail = Cart.objects.select_related('user').prefetch_related(
                'items__product').get(user=request.user.id)
            if CartItem.objects.filter(cart=cart_detail.id).count() == 0:
                messages.info(request, "Please add in Products to proceed!")

        except Cart.DoesNotExist:
            cart_obj = Cart()
            cart_obj.user = User(pk=request.user.id)
            cart_obj.created_by = User(pk=request.user.id)
            cart_obj.modify_by = User(pk=request.user.id)
            cart_obj.active = True
            cart_obj.save()
            return redirect('store:cart-list-view')

        cart_total = cart_detail.total_price()
        if cart_total <= 0:
            cart_total
        elif cart_total < 500:
            cart_total += 50
        coupon = None
        if 'coupon_code' in request.GET:
            coupon_code = request.GET.get('coupon_code')
            if coupon_code:
                try:
                    coupon = Coupon.objects.get(code=coupon_code)
                except Coupon.DoesNotExist:
                    messages.warning(request, "Invalid Coupon Code")
                    return redirect('store:cart-list-view')
                if coupon != None:
                    if coupon.no_of_uses <= 0:
                        messages.warning(
                            request, "The Coupon has reached the no of uses!")
                        return redirect('store:cart-list-view')
                    cart_total -= ((cart_total)*(coupon.percent_off/100))
                    cart_total = round(cart_total, 2)

        return render(request, 'store/cart.html', {'cart_detail': cart_detail, 'total': cart_total, 'coupon': coupon})

    except Exception as e:
        logger.error(e)
        messages.error(request, 'Something Went Wrong!')
        return render(request, 'store/cart.html')


def CartAddView(request, pk):
    try:
        if request.user.is_authenticated:
            if request.method == "POST":
                try:
                    query = Cart.objects.get(user=request.user.id)
                except Cart.DoesNotExist:
                    cart_obj = Cart()
                    cart_obj.user = User(pk=request.user.id)
                    cart_obj.created_by = User(pk=request.user.id)
                    cart_obj.modify_by = User(pk=request.user.id)
                    cart_obj.active = True
                    cart_obj.save()
                    query = Cart.objects.get(id=cart_obj.id)
                if query:
                    if CartItem.objects.filter(cart=query.id).filter(product=pk).count() > 0:
                        messages.info(
                            request, "Product is already in the Cart :)")
                        return redirect('store:cart-list-view')
                    else:
                        data = {}
                        for k, v in request.POST.items():
                            if k == 'csrfmiddlewaretoken' or k == 'Quantity':
                                pass
                            else:
                                data[k] = v
                        data = json.dumps(data)

                        with transaction.atomic():
                            cart_obj = CartItem()
                            cart_obj.cart = Cart(pk=query.id)
                            cart_obj.product = Product(id=pk)
                            product_query = Product.objects.get(id=pk)
                            if int(request.POST['Quantity']) > product_query.quantity:
                                messages.warning(
                                    request, 'Max Quantity has been reached!')
                                return HttpResponseRedirect('/store/product_detail/{}/'.format(product_query.id))
                            elif int(request.POST['Quantity']) < 1:
                                messages.warning(
                                    request, 'Quantity should be greater than 1')
                                return HttpResponseRedirect('/store/product_detail/{}/'.format(product_query.id))
                            else:
                                cart_obj.quantity = request.POST['Quantity']
                            cart_obj.created_by = User(pk=request.user.id)
                            cart_obj.modify_by = User(pk=request.user.id)
                            cart_obj.active = True
                            cart_obj.attribute = data
                            product_info = Product.objects.get(id=pk)
                            if product_info.check_if_special_price():
                                cart_obj.unit_price = product_info.special_price
                            else:
                                cart_obj.unit_price = product_info.price
                            cart_obj.save()
                            return redirect('store:cart-list-view')

            return render(request, 'store/cart-list.html')
        else:
            messages.warning(
                request, "This functionality is restricted for login User! Please login First")
            return redirect('store:login-view')
    except Exception as e:
        logger.error(e)
        messages.error(request, 'Something Went Wrong!')
        return redirect('store:cart-list-view')


@login_required(login_url='store:login-view')
def CartDeleteView(request, pk):
    try:
        if request.method == "POST":
            obj = get_object_or_404(CartItem, id=pk)
            obj.delete()
            return redirect('store:cart-list-view')

    except Exception as e:
        logger.error(e)
        messages.error(request, 'Something Went Wrong!')
        return redirect('store:cart-list-view')


def Transaction(**kwargs):
    with transaction.atomic():
        order_obj = Order()
        order_obj.user = User(pk=kwargs['request'])
        order_obj.AWB_NO = 'random'
        paymenttype = Payment_gateway.objects.get(
            name=kwargs['data']['PaymentType'])
        order_obj.payment_gateway = Payment_gateway(pk=paymenttype.id)
        cart_detail = kwargs['cart_detail']
        if cart_detail.total_price() < 500:
            order_obj.shipping_method = 50.00
            order_obj.shipping_charges = 50.00
        else:
            order_obj.shipping_charges = 0
            order_obj.shipping_method = 0
        order_obj.status = 'P'
        order_obj.grand_total = kwargs['cart_total']
        coupon = kwargs['coupon']
        if coupon != None:
            order_obj.coupon = Coupon(pk=coupon.id)
        if 'Fill_Address' in kwargs['data']:
            order_obj.billing_address = kwargs['data']['address']
            order_obj.billing_city = kwargs['data']['city']
            order_obj.billing_state = kwargs['data']['state']
            order_obj.billing_country = kwargs['data']['country']
            order_obj.billing_postcode = kwargs['data']['postcode']
            if 'Shipping' in kwargs['data']:
                order_obj.shipping_address = kwargs['data']['address']
                order_obj.shipping_city = kwargs['data']['city']
                order_obj.shipping_state = kwargs['data']['state']
                order_obj.shipping_country = kwargs['data']['country']
                order_obj.shipping_postcode = kwargs['data']['postcode']
        elif 'Address' in kwargs['data']:
            query = Address.objects.get(pk=kwargs['data']['Address'])
            order_obj.billing_address = query.address
            order_obj.billing_city = query.city
            order_obj.billing_state = query.state
            order_obj.billing_country = query.country
            order_obj.billing_postcode = query.postcode
            if 'Shipping' in kwargs['data']:
                order_obj.shipping_address = query.address
                order_obj.shipping_city = query.city
                order_obj.shipping_state = query.state
                order_obj.shipping_country = query.country
                order_obj.shipping_postcode = query.postcode
        order_obj.created_by = User(pk=kwargs['request'])
        order_obj.modify_by = User(pk=kwargs['request'])
        order_obj.active = True
        order_obj.save()
        for items in cart_detail.items.all():
            orderitem_obj = OrderItem()
            orderitem_obj.order = order_obj
            orderitem_obj.product = Product(pk=items.product.id)
            original_product_quantity = Product.objects.get(
                id=items.product.id)
            original_product_quantity.quantity = original_product_quantity.quantity - items.quantity
            original_product_quantity.save()
            orderitem_obj.quantity = items.quantity
            orderitem_obj.unit_price = items.unit_price
            orderitem_obj.attribute = items.attribute
            orderitem_obj.created_by = User(pk=kwargs['request'])
            orderitem_obj.modify_by = User(pk=kwargs['request'])
            orderitem_obj.active = True
            orderitem_obj.save()
            items.delete()
        if coupon != None:
            coupon_obj = Coupon.objects.get(pk=coupon.id)
            coupon_used_obj = Coupons_used()
            coupon_used_obj.order = order_obj
            coupon_used_obj.user = User(pk=kwargs['request'])
            coupon_used_obj.coupon = coupon_obj
            coupon_used_obj.created_by = User(pk=kwargs['request'])
            coupon_used_obj.modify_by = User(pk=kwargs['request'])
            coupon_used_obj.active = True
            coupon_used_obj.save()
            orginal_coupon_quantity = coupon_obj.no_of_uses
            coupon_obj.no_of_uses = orginal_coupon_quantity - 1
            coupon_obj.save()

    return order_obj.id


@login_required(login_url='store:login-view')
def CheckoutView(request, coupon_name):
    try:
        form = BillAddressForm()
        # checking if user had already existing payments to be done!
        try:
            existing_payment = Order.objects.get(
                user=request.user.id, payment_gateway__name='Paypal', status='P')
            if existing_payment:
                existing_payment_order_id = existing_payment.id
        except Order.DoesNotExist:
            existing_payment_order_id = None

        cart_detail = Cart.objects.select_related('user').prefetch_related(
            'items__product').get(user=request.user.id)
        if CartItem.objects.filter(cart=cart_detail.id).count() == 0:
            return redirect('store:cart-list-view')
        address = Address.objects.select_related('user').filter(
            user=request.user.id).filter(active=True)
        payment_methods = Payment_gateway.objects.filter(active=True)
        cart_total = cart_detail.total_price()
        if cart_total <= 0:
            cart_total
        elif cart_total < 500:
            cart_total += 50
        if coupon_name != 'None':
            coupon = Coupon.objects.get(code=coupon_name)
            cart_total -= ((cart_total)*(coupon.percent_off/100))
            cart_total = round(cart_total, 2)

        else:
            coupon = None

        if request.method == "POST":
            if 'Fill_Address' in request.POST:
                form = BillAddressForm(form_active=True, data=request.POST)
            else:
                form = BillAddressForm(request.POST)

            if 'Address' in request.POST:
                if 'PaymentType' not in request.POST:
                    messages.info(request, "Please Select the Payment Type!")
                elif request.POST['PaymentType'] == 'Paypal':
                    order_id = Transaction(data=request.POST,
                                           request=request.user.id,
                                           cart_total=cart_total,
                                           cart_detail=cart_detail,
                                           coupon=coupon)
                    return HttpResponseRedirect('/store/payment/{}/'.format(order_id))
                else:
                    order_id = Transaction(data=request.POST,
                                           request=request.user.id,
                                           cart_total=cart_total,
                                           cart_detail=cart_detail,
                                           coupon=coupon)

                    if order_id:
                        order = Order.objects.get(id=order_id)
                        html_content = render_to_string(
                            'order_placed_template.html', {'order': order})
                        text_content = strip_tags(html_content)
                        try:
                            send_mail(
                                'Here are your Order Details',
                                text_content,
                                settings.EMAIL_HOST_USER,
                                [request.user.email],
                                html_message=html_content,
                                fail_silently=False)
                        except Exception as e:
                            logger.error(e)

                        try:
                            admin_users = Group.objects.get(
                                name='admin').user_set.all()
                            send_mail(
                                'Details of the Users Placed Order',
                                text_content,
                                settings.EMAIL_HOST_USER,
                                [users.email for users in admin_users],
                                html_message=html_content,
                                fail_silently=False)
                        except Exception as e:
                            logger.error(e)

                    messages.success(
                        request, "Your Order was placed Successfully!")
                    return redirect('store:order-view')

            elif 'Fill_Address' in request.POST:
                if form.is_valid():
                    if 'PaymentType' not in request.POST:
                        messages.info(
                            request, "Please Select the Payment Type!")
                    elif request.POST['PaymentType'] == 'Paypal':
                        order_id = Transaction(data=request.POST,
                                               request=request.user.id,
                                               cart_total=cart_total,
                                               cart_detail=cart_detail,
                                               coupon=coupon)

                        return HttpResponseRedirect('/store/payment/{}/'.format(order_id))
                    else:
                        order_id = Transaction(data=request.POST,
                                               request=request.user.id,
                                               cart_total=cart_total,
                                               cart_detail=cart_detail,
                                               coupon=coupon)
                        if order_id:
                            order = Order.objects.get(id=order_id)
                            html_content = render_to_string(
                                'order_placed_template.html', {'order': order})
                            text_content = strip_tags(html_content)
                            send_mail(
                                'Here are your Order Details',
                                text_content,
                                settings.EMAIL_HOST_USER,
                                [request.user.email],
                                html_message=html_content,
                                fail_silently=False)
                            admin_users = Group.objects.get(
                                name='admin').user_set.all()
                            send_mail(
                                'Details of the Users Placed Order',
                                text_content,
                                settings.EMAIL_HOST_USER,
                                [users.email for users in admin_users],
                                html_message=html_content,
                                fail_silently=False)

                        messages.success(
                            request, "Your Order was placed Successfully!")

                        return redirect('store:order-view')

            else:
                messages.info(request, "Please Fill in the Address!")
                return HttpResponseRedirect('/store/checkout/{}/'.format(coupon_name))

        return render(request, 'store/checkout.html', {'existing_payment_order_id': existing_payment_order_id, 'address': address, 'cart_detail': cart_detail, 'total': cart_total, 'coupon': coupon, 'payment_methods': payment_methods, 'form': form})
    except Exception as e:
        logger.error(e)
        messages.error(request, 'Something Went Wrong!')
        return render(request, 'store/checkout.html')


@login_required(login_url='store:login-view')
def OrderDeleteView(request, order_id):
    try:
        if request.method == "POST":
            with transaction.atomic():
                orderitem = OrderItem.objects.filter(order=order_id)
                for item in orderitem:
                    item.delete()
                obj = get_object_or_404(Order, id=order_id)
                obj.delete()
            return HttpResponseRedirect('/store/checkout/None/')

    except Exception as e:
        logger.error(e)
        messages.error(request, 'Something Went Wrong!')
        return HttpResponseRedirect('/store/checkout/None/')


@login_required(login_url='store:login-view')
def PaymentView(request, order_id):
    try:
        if request.method == "GET":
            order_detail = Order.objects.get(id=order_id)
            return render(request, 'store/payment.html', {'order_detail': order_detail})

        if request.method == "POST":
            if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                try:
                    transaction_id = request.POST.get('transaction')
                    Order.objects.filter(id=order_id).update(
                        transaction_id=transaction_id, status='O')
                    if order_id:
                        order = Order.objects.get(id=order_id)
                        html_content = render_to_string(
                            'order_placed_template.html', {'order': order})
                        text_content = strip_tags(html_content)
                        send_mail(
                            'Here are your Order Details',
                            text_content,
                            settings.EMAIL_HOST_USER,
                            [request.user.email],
                            html_message=html_content,
                            fail_silently=False)
                        admin_users = Group.objects.get(
                            name='admin').user_set.all()
                        send_mail(
                            'Details of the Users Placed Order',
                            text_content,
                            settings.EMAIL_HOST_USER,
                            [users.email for users in admin_users],
                            html_message=html_content,
                            fail_silently=False)
                    response = {'url': '/store/myorder/', 'status': 1}
                    return HttpResponse(json.dumps(response), content_type='application/json')
                except Exception as e:
                    response = {'url': '/store/myorder/', 'status': 0}
                    return HttpResponse(json.dumps(response), content_type='application/json')
    except Exception as e:
        logger.error(e)
        messages.error(request, 'Something went wrong Cannot place your order')
        return redirect('store:order-view')


@login_required(login_url='store:login-view')
def OrderView(request):
    try:
        orders = Order.objects.filter(
            user=request.user.id).order_by('-created_at')
        return render(request, 'store/myorder.html', {'orders': orders})

    except Exception as e:
        logger.error(e)
        messages.error(request, 'Something Went Wrong')
        return render(request, 'store/myorder.html')


@login_required(login_url='store:login-view')
def TrackOrderView(request, **kwargs):
    try:
        form = TrackOrdersForm()
        if request.method == 'GET':
            if 'order_id' in request.GET:
                order_details = Order.objects.get(id=request.GET['order_id'])
            else:
                order_details = None
            return render(request, 'store/trackorder.html', {'order_details': order_details, 'form': form})

        if request.method == 'POST':
            form = TrackOrdersForm(request.POST)
            if form.is_valid():
                order_id = form.cleaned_data.get('orderid')
                try:
                    order_details = Order.objects.filter(
                        user=request.user.id).get(id=order_id)
                    if order_details:
                        return HttpResponseRedirect('/store/track-my-order/?order_id={}'.format(order_details.id))
                except Exception as e:
                    messages.info(request, 'No Such Order Exits!')
                    return redirect('store:track-order-view')

            return render(request, 'store/trackorder.html', {'form': form})
    except Exception as e:
        logger.error(e)
        messages.error(request, 'Something Went Wrong!')
        return render(request, 'store/trackorder.html')


def subscribe(email):
    mailchimp = Client()
    mailchimp.set_config({
        "api_key": api_key,
        "server": server,
    })

    member_info = {
        "email_address": email,
        "status": "subscribed",
    }

    try:
        response = mailchimp.lists.add_list_member(list_id, member_info)
        logger.info(response)

    except ApiClientError as error:
        logger.error(error.text)


def SubscribeNewsletterView(request):
    try:
        if request.method == "POST":
            email = request.POST['subscribenewsletter']
            subscribe(email)
            messages.success(
                request, "Thank You! For Subscribing to our NewsLetter ")

        return redirect('store:home-view')
    except Exception as e:
        logger.error(e)
        messages.success(request, "Something went Wrong!")
        return redirect('store:home-view')
