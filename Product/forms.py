from datetime import date

from django import forms
from django.forms import ModelForm
from django.forms.models import BaseInlineFormSet
from store.helper import check_categorys_children

from Product.models import (Attribute_values, Attributes, Attributes_assoc,
                            Category, Coupon, Order, Product,
                            Product_categories)


class ChangeOrderStatus(ModelForm):
    required_css_class = 'required'
    notify_customer = forms.BooleanField(required=False)
    comment = forms.CharField(label='Comment',required= False,widget=forms.Textarea(attrs={'placeholder': 'Comment','class':'form-control','rows':'8'}))
    
    class Meta:
        model = Order
        fields = ['status','notify_customer','comment']

        widgets = {
            'status': forms.Select(attrs={'class':'form-control'}),
            
        }


class CouponForm(ModelForm):
    required_css_class = 'required'
    def __init__(self, *args, **kwargs):
        super(CouponForm,self).__init__(*args, **kwargs)
        self.fields['code'].required = True

    class Meta:
        model = Coupon
        fields = ['code','percent_off','no_of_uses','active']

        widgets = {
            'code': forms.TextInput(attrs={'class':'form-control required'}),
            'percent_off': forms.NumberInput(attrs={'class':'form-control required'}),
            'no_of_uses': forms.NumberInput(attrs={'class':'form-control required'}),
        }


class AttributeForm(ModelForm):
    required_css_class = 'required'
    def __init__(self, *args, **kwargs):
        super(AttributeForm,self).__init__(*args, **kwargs)
        self.fields['name'].required = True

    class Meta:
        model = Attributes
        fields = ['name','active']

        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control required'}),
        }
    def clean_active(self):
        active = self.cleaned_data.get('active')
        attribute = self.cleaned_data.get('name')
        if Attributes.objects.filter(name = attribute).count() > 0:
            if active == True:
                return active
            else:
                query = Attributes_assoc.objects.filter(product_attribute__name = attribute).count()
                if query > 0:
                    raise forms.ValidationError("The attribute is already in use please delete it first")
                else:
                    return active
        else:
            return active


class CategoryForm(ModelForm):
    required_css_class = 'required'
    def __init__(self, *args, **kwargs):
        super(CategoryForm,self).__init__(*args, **kwargs)
        self.fields['title'].required = True
        # self.fields['parent'].queryset = Category.objects.exclude(title = self.fields['title'])

    class Meta:
        model = Category
        fields = ['title','active','parent']

        widgets = {
            'title': forms.TextInput(attrs={'class':'form-control required'}),
            'parent': forms.Select(attrs={'class':'form-control required'}),

        }
    def clean_active(self,*args,**kwargs):
        active = self.cleaned_data.get('active')
        category = self.cleaned_data.get('title')
        if Category.objects.filter(title = category).count() > 0:
            if active == True:
                return active
            else:
                query = Product_categories.objects.filter(category__title=category)
                if query.count() > 0:
                    raise forms.ValidationError("The category is already in use please delete it first")
                else:
                    query = Category.objects.get(title=category)
                    if query.children.exists():
                        sub_cat = Product_categories.objects.filter(category_id__in = check_categorys_children(query)).filter(active=True)
                        if sub_cat.count() > 0:
                            raise forms.ValidationError("The category is parent of child which is already in use please delete it first")
                        else:
                            return active
                    else:
                        return active
        else:
            return active
           

            

class ProductForm(ModelForm):
    required_css_class = 'required'
    def __init__(self, *args, **kwargs):
        super(ProductForm,self).__init__(*args, **kwargs)
        self.fields['title'].required = True
        self.fields['short_description'].required = True

    class Meta:
        model = Product
        fields = "__all__"
        exclude = ['created_by','modify_by']

        widgets = {
            'title': forms.TextInput(attrs={'class':'form-control required'}),
            'sku': forms.TextInput(attrs={'class':'form-control required'}),
            'short_description': forms.TextInput(attrs={'class':'form-control required'}),
            'long_description': forms.Textarea(attrs={'class':'form-control','id':'summernote'}),
            'price': forms.NumberInput(attrs={'class':'form-control'}),
            'special_price': forms.NumberInput(attrs={'class':'form-control'}),
            'special_price_from': forms.DateInput(attrs={'type':'date','style':'width:20%; margin:10px; padding:10px;'}),
            'special_price_to': forms.DateInput(attrs={'type':'date','style':'width:20%; margin-left:30px; padding:10px;'}),
            'quantity': forms.NumberInput(attrs={'class':'form-control'}),
            'meta_title': forms.TextInput(attrs={'class':'form-control '}),
            'meta_description': forms.Textarea(attrs={'class':'form-control','id':'summernote2'}),
            'meta_keywords': forms.TextInput(attrs={'class':'form-control'}),
            
        }

    def clean_specila_price_to(self,*args,**kwargs):
        special_price_from = self.cleaned_data.get('special_price_from')
        special_price_to = self.cleaned_data.get('special_from_to')

        if special_price_to < special_price_from:
            raise forms.ValidationError("The date must me greater than the above field")
        else:
            return special_price_to

    def clean_specila_price_from(self,*args,**kwargs):
        special_price_from = self.cleaned_data.get('special_price_from')

        if special_price_from < date.today():
            raise forms.ValidationError("The date must me greater than the todays date")
        else:
            return special_price_from

class ProductCategoryForm(ModelForm):
    def __init__(self,*args, **kwargs):
        super(ProductCategoryForm,self).__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(active= True)
    
    class Meta:
        model = Product_categories
        fields=['category','active']

        widgets={
                'category': forms.Select(attrs={'style':'padding: 5px 30px; margin: 0px 10px;'})
                }

    
class ProductAttributeForm(ModelForm):
    def __init__(self,*args, **kwargs):
        super(ProductAttributeForm,self).__init__(*args, **kwargs)
        self.fields['product_attribute'].queryset = Attributes.objects.filter(active= True)
        self.fields['product_attribute_value'].queryset = Attribute_values.objects.filter(active = True)
    
    class Meta:
        model = Attributes_assoc
        fields=['product_attribute','product_attribute_value','active']

        widgets={
                'product_attribute': forms.Select(attrs={'style':'padding: 5px 30px; margin: 0px 10px;'}),
                'product_attribute_value': forms.Select(attrs={'style':'padding: 5px 30px; margin: 0px 10px;'})
                }

def UniqueValidateFormset(field_name): 
    class UniqueFieldFormSet(BaseInlineFormSet): 
        def clean(self): 
            if any(self.errors): 
                return 
            values = set()
            for form in self.forms: 
                if form.cleaned_data: 
                    value = form.cleaned_data[field_name]
                    print(value)
                    if value in values:
                        raise forms.ValidationError('Duplicate values for %s are not allowed.' % field_name) 
                    values.add(value) 
    return UniqueFieldFormSet

def ProductAttributeFormset(**kwargs): 
    class UniqueFieldFormSet(BaseInlineFormSet): 
        def clean(self): 
            if any(self.errors): 
                return 
            values = {}
            for form in self.forms:
                print(values)
                if form.cleaned_data: 
                    attribute = form.cleaned_data[kwargs['attribute']]
                    attribute_value = form.cleaned_data[kwargs['attribute_value']]
                    if attribute in values.keys():
                        if attribute_value in values[attribute]: 
                            raise forms.ValidationError('Duplicate values for %s are not allowed.' % attribute)
                        values[attribute].append(attribute_value)
                    else:
                        values[attribute] = [attribute_value]
    return UniqueFieldFormSet




        