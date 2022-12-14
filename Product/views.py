import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import inlineformset_factory
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls.base import reverse
from django.utils.html import strip_tags
from django.views.generic import CreateView, UpdateView
from store.helper import mail
from django.contrib.auth.mixins import PermissionRequiredMixin

from Product.decorators import allowed_users
from Product.forms import (AttributeForm, CategoryForm, ChangeOrderStatus,
                           CouponForm, ProductAttributeForm,
                           ProductAttributeFormset, ProductCategoryForm,
                           ProductForm, UniqueValidateFormset)
from Product.models import (Attribute_values, Attributes, Attributes_assoc,
                            Category, Coupon, Images, Order, Product,
                            Product_categories)

logger = logging.getLogger('django')

@login_required(login_url='custom_admin:login-view')
@allowed_users(allowed_roles=['admin'])
def ProductListView(request):
    try:
        if request.method == "GET":
            products = Product.objects.all()
            for p in products:
                print(p.check_if_special_price())
            return render(request,'product/product-list.html',{'products':list(products)})       
        if request.method == "POST":
            ids = request.POST.getlist('id[]')
            for id in ids:
                Product.objects.get(pk=id).delete()
            messages.info(request,'Successfully Deleted Selected Items!')
            return HttpResponseRedirect('/admin/products/')
    except Exception as e:
        logger.error(e)
        messages.error(request,'Something Went Wrong!')
        return render(request,'product/product-list.html')


class ProductView(LoginRequiredMixin,PermissionRequiredMixin,SuccessMessageMixin,CreateView):
    login_url = '/admin/login/'
    model = Product
    form_class = ProductForm
    permission_required = 'Product.add_product'
    template_name = "product/product-add.html"
    success_url = '/admin/products/'
    success_message = 'Your Product was saved Successfully!'
    error_message = "Error saving the Product, check fields below."
    
    def form_valid(self, form):
        try:
            form.instance.created_by = self.request.user
            form.instance.modify_by = self.request.user
            return super().form_valid(form)
        except Exception as e:
            logger.error(e)

    def form_submit(self, request):
        try:
            if request.method == 'POST':
                form = ProductForm(request.POST)
                if form.is_valid():
                    form.save()
                else:
                    messages.error(self.request, self.error_message)
                    return HttpResponseRedirect('/admin/product/add/')
            return redirect('/admin/products/')
        except Exception as e:
            logger.error(e)
    

class ProductUpdateView(LoginRequiredMixin,PermissionRequiredMixin,SuccessMessageMixin,UpdateView):
    permission_required = 'Product.change_product'
    login_url = '/admin/login/'
    model = Product
    form_class = ProductForm
    template_name = "product/product-edit.html"
    success_message = 'Your Product was Updated Successfully!'
    error_message = "Error updating the Product, check fields below."

    def dispatch(self, request, *args, **kwargs):
        super().dispatch(request, *args, **kwargs)
        try:
            SubCategoryFormSet = inlineformset_factory(Product,
                                                    Product_categories,
                                                    form = ProductCategoryForm,
                                                    formset= UniqueValidateFormset('category'),extra=1,can_delete=False)
            AttributeFormSet = inlineformset_factory(Product,
                                                    Attributes_assoc,
                                                    form = ProductAttributeForm,
                                                    formset = ProductAttributeFormset(
                                                        attribute ='product_attribute',
                                                        attribute_value='product_attribute_value'),
                                                    extra=1,
                                                    can_delete=False
                                                    )
            ImageFormSet = inlineformset_factory(Product,
                                                Images,
                                                fields=['image_name','image','active'],
                                                extra=1,
                                                can_delete=False)
            self.product =  self.get_object()
            self.SubCategoryFormSet = SubCategoryFormSet
            self.AttributeFormSet = AttributeFormSet
            self.ImageFormSet = ImageFormSet
            self.formset = SubCategoryFormSet(instance=self.product)
            self.attributeformset = AttributeFormSet(instance=self.product)
            self.imageformset = ImageFormSet(instance=self.product)
            return super(ProductUpdateView,self).dispatch(request, *args, **kwargs)
        except Exception as e:
            logger.error(e)
    
    def form_valid(self, form):
        try:
            formset = self.SubCategoryFormSet(self.request.POST,instance=self.product)
            attributeformset = self.AttributeFormSet(self.request.POST,instance=self.product)
            imageformset = self.ImageFormSet(self.request.POST,self.request.FILES,instance=self.product)
            if formset.is_valid() and attributeformset.is_valid() and imageformset.is_valid() :
                self.formset_valid(formset)
                self.formset_valid(imageformset)
                self.formset_valid(attributeformset)

                form.instance.modify_by = self.request.user
                return super(ProductUpdateView,self).form_valid(form)
            else:
                if formset.non_form_errors():
                    messages.warning(self.request,strip_tags(formset.non_form_errors()))
                elif attributeformset.non_form_errors():
                    messages.warning(self.request,strip_tags(attributeformset.non_form_errors()))
                else:
                    messages.warning(self.request,self.error_message)
                
                return HttpResponseRedirect(self.request.path_info)
        except Exception as e:
            logger.error(e)
        
    def formset_valid(self, formset):
        try:
            instances = formset.save(commit=False)
            for instance in instances:
                try:
                    if instance.created_by:
                        instance.modify_by = self.request.user
                except Exception as e:
                    instance.created_by = self.request.user
                    instance.modify_by = self.request.user
                instance.save()
            formset.save()
        except Exception as e:
            logger.error(e)


    def get_context_data(self, **kwargs):
        try:
            context = super(ProductUpdateView,self).get_context_data(**kwargs)
            context['formset'] = self.formset
            context['attributeformset'] = self.attributeformset
            context['imageformset'] = self.imageformset
            context['product'] = self.product
            return context
        except Exception as e:
            logger.error(e)

    def post(self,request,**kwargs):
        try:
            if request.POST.get('data') == 'Category':
                v = request.POST.get('value')
                Product_categories.objects.filter(id=v).delete()
                return HttpResponseRedirect('/admin/product/{}/update'.format(self.kwargs['pk']))
            if request.POST.get('data') == 'Attribute':
                v = request.POST.get('value')
                Attributes_assoc.objects.filter(id=v).delete()
                return HttpResponseRedirect('/admin/product/{}/update'.format(self.kwargs['pk']))
            if request.POST.get('data') == 'Image':
                v = request.POST.get('value')
                Images.objects.get(id=v).delete()
                return HttpResponseRedirect('/admin/product/{}/update'.format(self.kwargs['pk']))
            return super(ProductUpdateView,self).post(request,**kwargs)
        except Exception as e:
            logger.error(e)
            return HttpResponseRedirect('/admin/product/{}/update'.format(self.kwargs['pk']))
    
    def get_success_url(self) -> str:
        return reverse('product:product-list-view')

@login_required(login_url='custom_admin:login-view')
@allowed_users(allowed_roles=['admin'])
def CategoryListView(request):
    try:

        if request.method == "GET":
            category = Category.objects.all()
            return render(request,'product/category-list.html',{'category':list(category)})
        
        if request.method == "POST":
            ids = request.POST.getlist('id[]')
            for id in ids:
                query = Product_categories.objects.filter(category = id).count()
                if query > 0:
                    messages.warning(request,'The category is already in use please delete it first')
                    return HttpResponseRedirect('/admin/categories/')
                else:
                    Category.objects.get(pk=id).delete()
            messages.success(request,'Successfully Deleted Selected Items!')
            return HttpResponseRedirect('/admin/categories/')
    except Exception as e:
        logger.error(e)
        messages.error(request,'Something Went Wrong!')
        return render(request,'product/category-list.html')

class CategoryView(LoginRequiredMixin,SuccessMessageMixin,CreateView):
    login_url = '/admin/login/'
    model = Category
    form_class = CategoryForm
    template_name = "product/category-add.html"
    success_message = 'Your Category was saved Successfully!'
    error_message = "Error saving the Category, check fields below."
    
    def form_valid(self, form):
        try:
            form.instance.created_by = self.request.user
            form.instance.modify_by = self.request.user
            return super().form_valid(form)
        except Exception as e:
            logger.error(e)

    def form_submit(self, request):
        try:
            if request.method == 'POST':
                form = CategoryForm(request.POST)
                if form.is_valid():
                    form.save()
                else:
                    messages.error(self.request, self.error_message)
                    return HttpResponseRedirect('admin/category/add/')
            return redirect('/admin/categories/')
        except Exception as e:
            logger.error(e)

    
    def get_success_url(self) -> str:
        try:
            return reverse('product:category-list-view')
        except Exception as e:
            logger.error(e)
    


class CategoryUpdateView(LoginRequiredMixin,SuccessMessageMixin,UpdateView,):
    login_url = '/admin/login/'
    model = Category
    form_class = CategoryForm
    template_name = "product/category-edit.html"
    success_message = 'Your Category was Updated Successfully!'
    error_message = "Error updating the Category, check fields below."

    def form_valid(self, form):
        try:
            form.instance.modify_by = self.request.user
            return super().form_valid(form)
        except Exception as e:
            logger.error(e)

    def get_success_url(self):
        try:
            return reverse("product:category-list-view")
        except Exception as e:
            logger.error(e)


@login_required(login_url='custom_admin:login-view')
@allowed_users(allowed_roles=['admin'])
def AttributeListView(request):
    try:
        if request.method == "GET":
            attributes = Attributes.objects.all()
            return render(request,'product/attribute-list.html',{'attributes':list(attributes)})
        
        if request.method == "POST":
            ids = request.POST.getlist('id[]')
            for id in ids:
                Attributes.objects.get(pk=id).delete()
            messages.success(request,'Successfully Deleted Selected Items!')
            return HttpResponseRedirect('/admin/attributes/')
    except Exception as e:
        logger.error(e)
        messages.error(request,'Something Went Wrong!')
        return render(request,'product/attribute-list.html')

class AttributeView(LoginRequiredMixin,SuccessMessageMixin,CreateView):
    login_url = '/admin/login/'
    model = Attributes
    form_class = AttributeForm
    template_name = "product/attribute-add.html"
    success_message = 'Your Attribute was saved Successfully!'
    error_message = "Error saving the Attribute, check fields below."
    
    def form_valid(self, form):
        try:
            form.instance.created_by = self.request.user
            form.instance.modify_by = self.request.user
            return super().form_valid(form)
        except Exception as e:
            logger.error(e)

    def form_submit(self, request):
        try:
            if request.method == 'POST':
                form = CategoryForm(request.POST)
                if form.is_valid():
                    form.save()
                else:
                    messages.error(self.request, self.error_message)
                    return HttpResponseRedirect('/attribute/add')
            return redirect('/admin/attributes/')
        except Exception as e:
            logger.error(e)

    def get_success_url(self) -> str:
        try:
            return reverse('product:attribute-list-view')
        except Exception as e:
            logger.error(e)
    


class AttributeUpdateView(LoginRequiredMixin,SuccessMessageMixin,UpdateView):
    login_url = '/admin/login/'
    model = Attributes
    form_class = AttributeForm
    template_name = "product/attribute-edit.html"
    success_message = 'Your Attribute was Updated Successfully!'
    error_message = "Error updating the Attribute, check fields below."


    def dispatch(self, request, *args, **kwargs):
        try:
            AttributeFormSet = inlineformset_factory(Attributes,
                                            Attribute_values,
                                            fields=['attribute_value','active'],
                                            formset= UniqueValidateFormset('attribute_value'),
                                            extra=1,
                                            can_delete=False)
            self.attribute = self.get_object()
            self.AttributeFormSet = AttributeFormSet
            self.formset = AttributeFormSet(instance=self.attribute)
            return super(AttributeUpdateView,self).dispatch(request, *args, **kwargs)
        except Exception as e:
            logger.error(e)

    def form_valid(self, form):
        try:
            attributeformset = self.AttributeFormSet(self.request.POST,instance=self.attribute)
            if attributeformset.is_valid():
                self.formset_valid(attributeformset)
            
                form.instance.modify_by = self.request.user
                return super(AttributeUpdateView,self).form_valid(form)
            else:
                if attributeformset.non_form_errors():
                    messages.warning(self.request,strip_tags(attributeformset.non_form_errors()))
                else:
                    messages.warning(self.request,self.error_message)
                
                return HttpResponseRedirect(self.request.path_info)
        except Exception as e:
            logger.error(e)

    def formset_valid(self, formset):
        try:
            instances = formset.save(commit=False)
            for instance in instances:
                try:
                    if instance.created_by:
                        instance.modify_by = self.request.user
                except Exception as e:
                    instance.created_by = self.request.user
                    instance.modify_by = self.request.user
                instance.save()
            formset.save()
        except Exception as e:
            logger.error(e)
    
    def get_context_data(self, **kwargs):
        try:
            context = super(AttributeUpdateView,self).get_context_data(**kwargs)
            formset = self.formset
            context['formset'] = formset
            context['attribute'] = self.attribute
            return context 
        except Exception as e:
            logger.error(e)
    
    def post(self,request,**kwargs):
        try:
            if request.POST.get('data') == 'Attribute':
                v = request.POST.get('value')
                Attribute_values.objects.filter(id=v).delete()
                return HttpResponseRedirect('/admin/attribute/{}/update'.format(self.kwargs['pk']))
            return super(AttributeUpdateView,self).post(request,**kwargs)
        except Exception as e:
            logger.error(e)
            return HttpResponseRedirect('/admin/attribute/{}/update'.format(self.kwargs['pk']))

    def get_success_url(self):
        try:
            return reverse("product:attribute-list-view")
        except Exception as e:
            logger.error(e)

@login_required(login_url='custom_admin:login-view')
@allowed_users(allowed_roles=['admin'])
def CouponListView(request):
    try:
        if request.method == "GET":
            coupons = Coupon.objects.all()
            return render(request,'product/coupon-list.html',{'coupons':list(coupons)})
        
        if request.method == "POST":
            ids = request.POST.getlist('id[]')
            for id in ids:
                Coupon.objects.get(pk=id).delete()
            messages.success(request,'Successfully Deleted Selected Items!')
            return HttpResponseRedirect('/admin/coupons/')
    except Exception as e:
        logger.error(e)
        messages.error(request,'Something Went Wrong!')
        return render(request,'product/coupon-list.html')

class CouponView(LoginRequiredMixin,SuccessMessageMixin,CreateView):
    login_url = '/admin/login/'
    model = Coupon
    form_class = CouponForm
    template_name = "product/coupon-add.html"
    success_message = 'Your Coupon was saved Successfully!'
    error_message = "Error saving the Coupon, check fields below."
    
    def form_valid(self, form):
        try:
            form.instance.created_by = self.request.user
            form.instance.modify_by = self.request.user
            return super().form_valid(form)
        except Exception as e:
            logger.error(e)

    def form_submit(self, request):
        try:
            if request.method == 'POST':
                form = CouponForm(request.POST)
                if form.is_valid():
                    form.save()
                else:
                    messages.error(self.request, self.error_message)
                    return HttpResponseRedirect('/coupon/add')
            return redirect('/admin/coupons/')
        except Exception as e:
            logger.error(e)

    def get_success_url(self) -> str:
        try:
            return reverse('product:coupon-list-view')
        except Exception as e:
            logger.error(e)
    


class CouponUpdateView(LoginRequiredMixin,SuccessMessageMixin,UpdateView):
    login_url = '/admin/login/' 
    model = Coupon
    form_class = CouponForm
    template_name = "product/coupon-edit.html"
    success_message = 'Your Coupon was Updated Successfully!'
    error_message = "Error updating the Coupon, check fields below."

    def form_valid(self, form):
        try:
            form.instance.modify_by = self.request.user
            return super().form_valid(form)
        except Exception as e:
            logger.error(e)

    def get_success_url(self):
        try:
            return reverse("product:coupon-list-view")
        except Exception as e:
            logger.error(e)

@login_required(login_url='custom_admin:login-view')
@allowed_users(allowed_roles=['admin'])
def OrderListView(request):
    try:
        orders = Order.objects.select_related('user','payment_gateway').prefetch_related('orderitem_set__product').all().order_by('-created_at')
        return render(request,'product/order-list.html',{'orders':list(orders)})
    except Exception as e:
        logger.error(e) 
        messages.error(request,'Something Went Wrong!')
        return render(request,'product/order-list.html')



@login_required(login_url='custom_admin:login-view')
@allowed_users(allowed_roles=['admin'])
def OrderDetailView(request,pk):
    try:
        try:
            order_detail = Order.objects.select_related('user','payment_gateway').prefetch_related('orderitem_set__product').get(id=pk)
            form = ChangeOrderStatus(initial={'status':order_detail.status})
        except Order.DoesNotExist:
            return HttpResponse("The Order Does not Exits!<br><a href='/admin/'>Home</a>")

        if request.method == 'POST':
            level = {'P':0,'O':1,'S':2,'D':3}
            form = ChangeOrderStatus(request.POST)
            if form.is_valid():
                try:
                    order_detail = Order.objects.get(id=pk)
                    if level[form.cleaned_data['status']] > level[order_detail.status]:
                        order_detail.status = form.cleaned_data['status']
                        order_detail.save()
                        comment = form.cleaned_data['comment']
                        mail(
                                id = 8,
                                context = {'order_detail':order_detail,'Comment':comment},
                                user_email = [order_detail.user.email]
                            )
                    messages.success(request,'Your Order Status was changed Successfully!')
                    return HttpResponseRedirect('/admin/order-detail/{}/'.format(pk))
                except Exception as e:
                    print(e)
                

        return render(request,'product/order-detail.html',{'order_detail':order_detail,'form':form})
    except Exception as e:
        logger.error(e)
        messages.warning(request,'Something Went Wrong!')
        return render(request,'product/order-detail.html')










