from django.forms import ModelForm
from User.models import User
from .models import Address, contact_us
from django import forms
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm,AuthenticationForm
import re
from django_countries.data import COUNTRIES


class TrackOrdersForm(forms.Form):
    
    orderid = forms.UUIDField(label='OrderID',required=True,widget=forms.TextInput(attrs={'placeholder': 'Order ID','class':'form-control'}))
    email = forms.EmailField(label='Email',required=True,widget=forms.EmailInput(attrs={'placeholder': 'Email','class':'form-control'}))


    def clean_email(self,*args,**kwargs):
        eml = self.cleaned_data.get('email')
        pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        if re.fullmatch(pattern,eml):
            return eml
        else:
            raise forms.ValidationError("Invalid Email!")

class BillAddressForm(forms.Form):
    def __init__(self,form_active=False,*args, **kwargs):
        super(BillAddressForm,self).__init__(*args, **kwargs)
        self.make_form_active = form_active
    
    address = forms.CharField(label='Address',required=False,widget=forms.Textarea(attrs={'placeholder': 'Address','class':'form-control','rows':'8'}))
    city = forms.CharField(label='City',required=False,widget=forms.TextInput(attrs={'placeholder': 'City','class':'form-control'}))
    state = forms.CharField(label='State',required=False,widget=forms.TextInput(attrs={'placeholder': 'State','class':'form-control'}))
    country = forms.CharField(widget = forms.Select(choices=COUNTRIES.items(),attrs={'class':'form-control'}))
    postcode = forms.CharField(label='PostCode',required=False,widget=forms.TextInput(attrs={'placeholder': 'PostCode','class':'form-control'}))
    
    def clean_address(self,*args,**kwargs):
        address = self.cleaned_data.get('address')
        if self.make_form_active:
            if not address:
                raise forms.ValidationError("This field is required")
            return address
        return address
    
    def clean_city(self,*args,**kwargs):
        city_name = self.cleaned_data.get('city')
        if self.make_form_active:
            if not city_name:
                raise forms.ValidationError("This field is required")
            else:
                pattern = re.compile(r"^([a-zA-Z\u0080-\u024F]+(?:. |-| |'))*[a-zA-Z\u0080-\u024F]*$")
                if re.fullmatch(pattern,city_name):
                    return city_name
                else:
                    raise forms.ValidationError("Invalid City!")
        return city_name

    def clean_postcode(self,*args,**kwargs):
        data = self.cleaned_data.get('postcode')
        if self.make_form_active:
            if not data:
                raise forms.ValidationError("This field is required")
            else:
                if data.isdigit():
                    return data
                else:
                    raise forms.ValidationError("Invalid Postcode!")
        return data
            
        
    
    def clean_state(self,*args,**kwargs):
        data = self.cleaned_data.get('state')
        if self.make_form_active:
            if not data:
                raise forms.ValidationError("This field is required")
            else:
                pattern = re.compile(r"^([a-zA-Z\u0080-\u024F]+(?:. |-| |'))*[a-zA-Z\u0080-\u024F]*$")
                if re.fullmatch(pattern,data):
                    return data
                else:
                    raise forms.ValidationError("Invalid State!")
        return data

class AddressForm(ModelForm):
    required_css_class = 'required'
    
    class Meta:
        model = Address
        fields = ['address','city','state','country','postcode','active']

        widgets = {
            'address': forms.Textarea(attrs={'placeholder':'Address','class':'form-control','rows':'8'}),
            'city': forms.TextInput(attrs={'placeholder':'City','class':'form-control'}),
            'state': forms.TextInput(attrs={'placeholder':'State','class':'form-control'}),
            'country': forms.Select(attrs={'class':'form-control'}),
            'postcode': forms.TextInput(attrs={'placeholder':'PostCode','class':'form-control'}),
            
        }
    def clean_city(self,*args,**kwargs):
        city_name = self.cleaned_data.get('city')
        pattern = re.compile(r"^([a-zA-Z\u0080-\u024F]+(?:. |-| |'))*[a-zA-Z\u0080-\u024F]*$")
        if re.fullmatch(pattern,city_name):
            return city_name
        else:
            raise forms.ValidationError("Invalid City!")

    def clean_postcode(self,*args,**kwargs):
        data = self.cleaned_data.get('postcode')
        if data.isdigit():
            return data
        else:
            raise forms.ValidationError("Invalid Postcode!")
            
        
    
    def clean_state(self,*args,**kwargs):
        data = self.cleaned_data.get('state')
        pattern = re.compile(r"^([a-zA-Z\u0080-\u024F]+(?:. |-| |'))*[a-zA-Z\u0080-\u024F]*$")
        if re.fullmatch(pattern,data):
            return data
        else:
            raise forms.ValidationError("Invalid State!")

        
class ProfileUpdateForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name','last_name','username','email']

        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder':'First Name','class':'form-control'}),
            'last_name': forms.TextInput(attrs={'placeholder':'Last Name','class':'form-control'}),
            'username': forms.TextInput(attrs={'placeholder':'Username','class':'form-control'}),
            'email': forms.TextInput(attrs={'placeholder':'Email Address','class':'form-control'}),
            
        }

    def clean_username(self,*args,**kwargs):
        uname = self.cleaned_data.get('username')
        if uname.isalnum():
            raise forms.ValidationError("Username must be Alphanumeric!")
        return uname
    
    def clean_first_name(self,*args,**kwargs):
        data = self.cleaned_data.get('first_name')
        if data.isdigit():
            raise forms.ValidationError("First Name must contain only Letters!")
        return data

    def clean_last_name(self,*args,**kwargs):
        data = self.cleaned_data.get('last_name')
        if data.isdigit():
            raise forms.ValidationError("Last Name must contain only Letters!")
        return data

    


class SignUpForm(UserCreationForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password','placeholder':'Password'}),
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password','placeholder':'Confirm Password'}),
        
    )
    class Meta:
        model = User
        fields = ['username','email','password1','password2']

        widgets = {
            'username': forms.TextInput(attrs={'placeholder':'Name'}),
            'email': forms.TextInput(attrs={'placeholder':'Email Address'}),
            
        }

    def clean_username(self,*args,**kwargs):
        uname = self.cleaned_data.get('username')
        if uname.isalnum():
            raise forms.ValidationError("Username must be Alphanumeric!")
        return uname



class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm,self).__init__(*args, **kwargs)
        self.fields['username'].widget = forms.TextInput(attrs={'placeholder':'Username'})
        self.fields['password'].widget = forms.PasswordInput(attrs={'placeholder':'Password'})

class ContactUsForm(ModelForm):
    class Meta:
        model = contact_us
        fields = '__all__'
        exclude = ['created_by','modify_by']

        widgets = {
            'name': forms.TextInput(attrs={'placeholder':'Name','class':'form-control'}),
            'email': forms.EmailInput(attrs={'placeholder':'Email','class':'form-control'}),
            'contact_no': forms.TextInput(attrs={'placeholder':'Contact No','class':'form-control'}),
            'message': forms.Textarea(attrs={'placeholder':'Your Message Here','class':'form-control','rows':'8'}),
            'note_admin': forms.TextInput(attrs={'placeholder':'Note','class':'form-control'}),
            
        }


    def clean_contact_no(self,*args,**kwargs):
        contact = self.cleaned_data.get('contact_no')
        if len(contact) < 10:
            raise forms.ValidationError("Invalid Contact Number")
        elif not contact.isdigit():
            raise forms.ValidationError("Only digits are allowed")
        return contact


    def clean_email(self,*args,**kwargs):
        eml = self.cleaned_data.get('email')
        pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        if re.fullmatch(pattern,eml):
            return eml
        else:
            raise forms.ValidationError("Invalid Email!")

class MyPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password','placeholder':'Old Password','class':'form-control','type':'password'}),
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password1','placeholder':'New Password','class':'form-control','type':'password'}),
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password2','placeholder':'Confirm New Password','class':'form-control','type':'password'}),
        
    )
    class Meta:
        model = User
        fields = ['old_password', 'new_password1', 'new_password2']





