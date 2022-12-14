import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import inlineformset_factory
from django.http.response import (HttpResponse, HttpResponseRedirect,
                                  JsonResponse)
from django.shortcuts import redirect, render
from django.urls.base import reverse
from django.utils.html import strip_tags
from django.views.generic import CreateView, UpdateView
from Product.models import Coupon, Coupons_used, Order, Product
from store.helper import mail
from store.models import Profile, contact_us
from User.models import User

from custom_admin.decorators import allowed_users, unauthenticated_user
from custom_admin.forms import (BannerForm, CMSForm, ConfigForm,
                                EmailTemplateForm)

from .models import CMS, Banner, Banner_images, EmailTemplate, configuration

logger = logging.getLogger('django')


@login_required(login_url='custom_admin:login-view')
@allowed_users(allowed_roles=['admin'])
def admin_home_view(request):
    try:
        order_count = Order.objects.all().count()
        user_count = User.objects.all().count()
        coupon_count = Coupon.objects.all().count()
        product_count = Product.objects.all().count()
        context = {'order_count': order_count,
                   'user_count': user_count,
                   'coupon_count': coupon_count,
                   'product_count': product_count

                   }
        return render(request, 'custom_admin/dashboard.html', context=context)
    except Exception as e:
        logger.error(e)
        messages.error(request, 'Something Went Wrong!')
        return render(request, 'custom_admin/dashboard.html')


@login_required(login_url='custom_admin:login-view')
@allowed_users(allowed_roles=['admin'])
def user_list_view(request):
    try:
        if request.method == "GET":
            users = User.objects.all()
            return render(request, 'custom_admin/user-list.html', {'users': list(users)})
    except Exception as e:
        logger.error(e)
        messages.error(request, 'Something Went Wrong!')
        return render(request, 'custom_admin/user-list.html')


@unauthenticated_user
def LoginView(request):
    try:
        if request.method == "POST":
            user = request.POST.get("username")
            pwd = request.POST.get("password")
            user = authenticate(request, username=user, password=pwd)
            if user is not None:
                if user.is_staff:
                    login(request, user)
                    return redirect('custom_admin:admin-home-view')
                else:
                    messages.info(request, 'Only Staff can access the site!!')
            else:
                messages.info(request, 'User or password is incorrect!')
        return render(request, 'registration/login.html')
    except Exception as e:
        logger.error(e)
        messages.error(request, 'Something Went Wrong!')
        return render(request, 'registration/login.html')


def LogoutView(request):
    try:
        logout(request)
        return redirect('custom_admin:login-view')
    except Exception as e:
        logger.error(e)


@login_required(login_url='custom_admin:login-view')
@allowed_users(allowed_roles=['admin'])
def EmailTemplateListView(request):
    try:
        if request.method == "GET":
            email_templates = EmailTemplate.objects.all()
            return render(request, 'custom_admin/email-template-list.html', {'email_templates': list(email_templates)})

        if request.method == "POST":
            ids = request.POST.getlist('id[]')
            for id in ids:
                EmailTemplate.objects.get(pk=id).delete()
            messages.success(request, 'Successfully Deleted Selected Items!')
            return HttpResponseRedirect('/admin/email-templates/')
    except Exception as e:
        logger.error(e)
        messages.error(request, 'Something Went Wrong!')
        return render(request, 'custom_admin/email-template-list.html')


class EmailTemplateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    login_url = '/admin/login/'
    model = EmailTemplate
    form_class = EmailTemplateForm
    template_name = "custom_admin/email-template-add.html"
    success_message = 'Your Email Template was saved Successfully!'
    error_message = "Error saving the Email Template, check fields below."

    def form_valid(self, form):
        try:
            form.instance.created_by = self.request.user
            form.instance.modify_by = self.request.user
            return super(EmailTemplateView, self).form_valid(form)
        except Exception as e:
            logger.error(e)

    def get_success_url(self) -> str:
        try:
            return reverse('custom_admin:email-template-list-view')
        except Exception as e:
            logger.error(e)


class EmailTemplateUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    login_url = '/admin/login/'
    model = EmailTemplate
    form_class = EmailTemplateForm
    template_name = "custom_admin/email-template-edit.html"
    success_message = 'Your Email Template was Updated Successfully!'
    error_message = "Error Updating the Email Template, check fields below."

    def form_valid(self, form):
        try:
            form.instance.modify_by = self.request.user
            return super(EmailTemplateUpdateView, self).form_valid(form)
        except Exception as e:
            logger.error(e)

    def get_success_url(self):
        try:
            return reverse("custom_admin:email-template-list-view")
        except Exception as e:
            logger.error(e)


@login_required(login_url='custom_admin:login-view')
@allowed_users(allowed_roles=['admin'])
def ConfigListView(request):
    try:
        if request.method == "GET":
            config = configuration.objects.all()
            return render(request, 'custom_admin/config-list.html', {'config_list': list(config)})

        if request.method == "POST":
            ids = request.POST.getlist('id[]')
            for id in ids:
                configuration.objects.get(pk=id).delete()
            messages.success(request, 'Successfully Deleted Selected Items!')
            return HttpResponseRedirect('/admin/configurations/')
    except Exception as e:
        logger.error(e)
        messages.error(request, 'Something Went Wrong!')
        return render(request, 'custom_admin/config-list.html')


class ConfigView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    login_url = '/admin/login/'
    model = configuration
    form_class = ConfigForm
    template_name = "custom_admin/config-add.html"
    success_message = 'Your Configuration was saved Successfully!'
    error_message = "Error saving the Configuration, check fields below."

    def form_valid(self, form):
        try:
            form.instance.created_by = self.request.user
            form.instance.modify_by = self.request.user
            return super(ConfigView, self).form_valid(form)
        except Exception as e:
            logger.error(e)

    def get_success_url(self) -> str:
        try:
            return reverse('custom_admin:config-list-view')
        except Exception as e:
            logger.error(e)


class ConfigUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    login_url = '/admin/login/'
    model = configuration
    form_class = ConfigForm
    template_name = "custom_admin/config-update.html"
    success_message = 'Your Configuration was Updated Successfully!'
    error_message = "Error updating the Configuration, check fields below."

    def form_valid(self, form):
        try:
            form.instance.modify_by = self.request.user
            return super(ConfigUpdateView, self).form_valid(form)
        except Exception as e:
            logger.error(e)

    def get_success_url(self):
        try:
            return reverse("custom_admin:config-list-view")
        except Exception as e:
            logger.error(e)


@login_required(login_url='custom_admin:login-view')
@allowed_users(allowed_roles=['admin'])
def BannerListView(request):

    if request.method == "GET":
        try:
            banners = Banner.objects.prefetch_related(
                'banner_images_set__banner').all()
            return render(request, 'custom_admin/banner-list.html', {'banners': list(banners)})
        except Exception as e:
            logger.error(e)
            messages.error(request, 'Something Went Wrong!')
            return render(request, 'custom_admin/banner-list.html')

    if request.method == "POST":
        try:
            ids = request.POST.getlist('id[]')
            for id in ids:
                Banner.objects.get(pk=id).delete()
            messages.success(request, 'Successfully Deleted Selected Items!')
            return HttpResponseRedirect('/admin/banners/')
        except Exception as e:
            logger.error(e)
            messages.error(request, 'Something Went Wrong!')
            return render(request, 'custom_admin/banner-list.html')


class BannerView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    login_url = '/admin/login/'
    model = Banner
    form_class = BannerForm
    template_name = "custom_admin/banner-add.html"
    success_message = 'Your Banner Path was saved Successfully!'
    error_message = "Error saving the Banner Path, check fields below."

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
                form = BannerForm(request.POST)
                if form.is_valid():
                    form.save()
                else:
                    messages.error(self.request, self.error_message)
                    return HttpResponseRedirect('/banner/add')
            return redirect('/admin/banners/')
        except Exception as e:
            logger.error(e)

    def get_success_url(self) -> str:
        try:
            return reverse('custom_admin:banner-list-view')
        except Exception as e:
            logger.error(e)


class BannerUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    login_url = '/admin/login/'
    model = Banner
    form_class = BannerForm
    template_name = "custom_admin/banner-edit.html"
    success_message = 'Your Banner Path was saved Successfully!'
    error_message = "Error saving the Banner Path, check fields below."

    def dispatch(self, request, *args, **kwargs):
        try:
            BannerFormSet = inlineformset_factory(Banner,
                                                  Banner_images,
                                                  fields=['image_name',
                                                          'image', 'active'],
                                                  extra=1,
                                                  can_delete=False)
            self.banner = self.get_object()
            self.BannerFormSet = BannerFormSet
            self.formset = BannerFormSet(instance=self.banner)
            return super(BannerUpdateView, self).dispatch(request, *args, **kwargs)
        except Exception as e:
            logger.error(e)

    def form_valid(self, form):
        try:
            formset = self.BannerFormSet(
                self.request.POST, self.request.FILES, instance=self.banner)
            if formset.is_valid():
                self.formset_valid(formset)

                form.instance.modify_by = self.request.user
                return super(BannerUpdateView, self).form_valid(form)
            else:
                if formset.non_form_errors():
                    messages.warning(self.request, strip_tags(
                        formset.non_form_errors()))
                else:
                    messages.warning(self.request, self.error_message)

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
            context = super(BannerUpdateView, self).get_context_data(**kwargs)
            formset = self.formset
            context['formset'] = formset
            context['banner'] = self.banner
            return context
        except Exception as e:
            logger.error(e)

    def post(self, request, **kwargs):
        try:
            if request.POST.get('data') == 'Banner':
                v = request.POST.get('value')
                Banner_images.objects.filter(id=v).delete()
                return HttpResponseRedirect('/admin/banner/{}/update'.format(self.kwargs['pk']))
            return super(BannerUpdateView, self).post(request, **kwargs)
        except Exception as e:
            logger.error(e)
            return HttpResponseRedirect('/admin/banner/{}/update'.format(self.kwargs['pk']))

    def get_success_url(self):
        try:
            return reverse("custom_admin:banner-list-view")
        except Exception as e:
            logger.error(e)


@login_required(login_url='custom_admin:login-view')
@allowed_users(allowed_roles=['admin'])
def CMSListView(request):
    try:
        if request.method == "GET":
            cms = CMS.objects.all()
            return render(request, 'custom_admin/cms-list.html', {'cms': list(cms)})

        if request.method == "POST":
            ids = request.POST.getlist('id[]')
            for id in ids:
                try:
                    CMS.objects.get(pk=id).delete()
                except Exception as e:
                    messages.warning(
                        request, 'CMS Does not exist perhaps it was Deleted!')
            messages.success(request, 'Successfully Deleted Selected Items!')
            return HttpResponseRedirect('/admin/cms/')
    except Exception as e:
        logger.error(e)
        messages.error(request, 'Something Went Wrong!')
        return render(request, 'custom_admin/cms-list.html')


class CMSView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    login_url = '/admin/login/'
    model = CMS
    form_class = CMSForm
    template_name = "custom_admin/cms-add.html"
    success_message = 'Your CMS was saved Successfully!'
    error_message = "Error saving the CMS, check fields below."

    def form_valid(self, form):
        try:
            form.instance.created_by = self.request.user
            form.instance.modify_by = self.request.user
            form.instance.template_name = 'custom_admin/flatpages/default.html'
            return super(CMSView, self).form_valid(form)
        except Exception as e:
            logger.error(e)

    def get_success_url(self) -> str:
        try:
            return reverse('custom_admin:cms-list-view')
        except Exception as e:
            logger.error(e)


class CMSUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    login_url = '/admin/login/'
    model = CMS
    form_class = CMSForm
    template_name = "custom_admin/cms-update.html"
    success_message = 'Your CMS was Updated Successfully!'
    error_message = "Error updating the CMS, check fields below"

    def form_valid(self, form):
        try:
            form.instance.modify_by = self.request.user
            return super(CMSUpdateView, self).form_valid(form)
        except Exception as e:
            logger.error(e)

    def get_success_url(self):
        try:
            return reverse("custom_admin:cms-list-view")
        except Exception as e:
            logger.error(e)


@login_required(login_url='custom_admin:login-view')
@allowed_users(allowed_roles=['admin'])
def ContactUsListView(request):
    try:
        contact = contact_us.objects.all()
        return render(request, 'custom_admin/contact-us-list.html', {'contact': list(contact)})
    except Exception as e:
        logger.error(e)
        messages.error(request, 'Something Went Wrong!')
        return render(request, 'custom_admin/contact-us-list.html')


@login_required(login_url='custom_admin:login-view')
@allowed_users(allowed_roles=['admin'])
def ContactUsDetailView(request, pk):
    if request.method == 'GET':
        try:
            contact_us_detail = contact_us.objects.get(id=pk)
        except contact_us.DoesNotExist:
            return HttpResponse("The Message Does not Exits!<br><a href='/admin/'>Home</a>")
        return render(request, 'custom_admin/contact-us-detail.html', {'contact_us_detail': contact_us_detail})

    if request.method == 'POST' and 'note' in request.POST:
        try:
            contact_us_detail = contact_us.objects.get(id=pk)
            mail(
                id=7,
                context={'Name': contact_us_detail.name, 'Email': contact_us_detail.email,
                         'Contact': contact_us_detail.contact_no, 'Message': contact_us_detail.message, 'Note': request.POST['note']},
                user_email=[contact_us_detail.email]
            )
            messages.success(request, 'Email was Sent Successfully')
            return HttpResponseRedirect('/admin/contact-us-detail/{}/'.format(pk))
        except Exception as e:
            logger.error(e)
            messages.error(request, 'Something Went Wrong')
            return HttpResponseRedirect('/admin/contact-us-detail/{}/'.format(pk))


@login_required(login_url='custom_admin:login-view')
@allowed_users(allowed_roles=['admin'])
def ReportView(request):
    try:
        if request.method == "GET":
            if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                obj = Profile.objects.filter(user__groups__name='Customer').values(
                    'id', 'user__username', 'user__email', 'registration_method', 'user__date_joined', 'user__is_active',)
                context = {
                    "data": [data for data in obj],
                }
                return JsonResponse(context)

        if request.method == "POST":
            filter_val = request.POST.get('filter_val')
            if filter_val == 'Coupons Used':
                if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                    obj = Coupons_used.objects.values(
                        'id', 'order', 'user__email', 'coupon__code', 'created_by_id', 'modify_by_id', 'active', 'created_at', 'modify_at')
                    context = {
                        "data": [data for data in obj],
                        "columns": [
                            {'title': 'ID', 'data': 'id'},
                            {'title': 'Order', 'data': "order"},
                            {'title': 'Created by', 'data': "created_by_id"},
                            {'title': 'Modify by', 'data': "modify_by_id"},
                            {'title': 'Created Date', 'data': "created_at"},
                            {'title': 'Modify Date', 'data': "modify_at"},
                            {'title': 'User', 'data': "user__email"},
                            {'title': 'Coupon', 'data': "coupon__code"},
                            {'title': 'Active', 'data': 'active'},

                        ]
                    }
                    return JsonResponse(context)

            elif filter_val == 'Customer Registered':
                if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                    obj = Profile.objects.filter(user__groups__name='Customer').values(
                        'id', 'user__username', 'user__email', 'registration_method', 'user__date_joined', 'user__is_active',)
                    context = {
                        "data": [data for data in obj],
                        "columns": [
                            {'title': 'ID', 'data': 'id'},
                            {'title': 'Date Joined', 'data': "user__date_joined"},
                            {'title': 'Active', 'data': "user__is_active"},
                            {'title': 'User', 'data': "user__username"},
                            {'title': 'Email', 'data': "user__email"},
                            {'title': 'Registration Method',
                                'data': 'registration_method'},

                        ]
                    }

                    return JsonResponse(context)

        return render(request, 'custom_admin/report.html')
    except Exception as e:
        logger.error(e)
        messages.error(request, 'Something Went Wrong!')
        return render(request, 'custom_admin/report.html')


@login_required(login_url='custom_admin:login-view')
@allowed_users(allowed_roles=['admin'])
def SalesReportView(request):
    try:
        if request.method == 'GET':
            if 'Sales-Report' in request.GET:
                start_date = request.GET['SalesReportStartDate']
                end_date = request.GET['SalesReportEndDate']
                order_list = Order.objects.select_related('user', 'payment_gateway', 'coupon').prefetch_related(
                    'orderitem_set__product').filter(created_at__gte=start_date, created_at__lte=end_date)
                order_total = sum([order.grand_total for order in order_list])
                discount = round(sum([((order.grand_total)*(order.coupon.percent_off/100))
                                 for order in order_list if order.coupon]), 2)

            else:
                order_list = Order.objects.select_related(
                    'user', 'payment_gateway', 'coupon').prefetch_related('orderitem_set__product').all()
                order_total = sum([order.grand_total for order in order_list])
                discount = round(sum([((order.grand_total)*(order.coupon.percent_off/100))
                                 for order in order_list if order.coupon]), 2)

        return render(request, 'custom_admin/sales-report.html', {'order_list': order_list, 'order_total': order_total, 'discount': discount})

    except Exception as e:
        logger.error(e)
        messages.warning(request, 'Something Went Wrong!')
        return render(request, 'custom_admin/sales-report.html')
