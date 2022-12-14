from django.urls import path

from . import views
from .views import (BannerUpdateView, BannerView, CMSUpdateView, CMSView,
                    ConfigUpdateView, ConfigView, EmailTemplateUpdateView,
                    EmailTemplateView)

app_name = 'custom_admin'

urlpatterns = [
    path('', views.admin_home_view, name='admin-home-view'),

    path('email-template/add/', EmailTemplateView.as_view(),
         name='email-template-add-view'),
    path('email-template/<str:pk>/update/',
         EmailTemplateUpdateView.as_view(), name='email-template-update-view'),
    path('email-templates/', views.EmailTemplateListView,
         name='email-template-list-view'),

    path('contact-us/', views.ContactUsListView, name="contact-us-list-view"),
    path('contact-us-detail/<str:pk>/', views.ContactUsDetailView,
         name="contact-us-detail-view"),

    path('cms/add/', CMSView.as_view(), name="cms-add-view"),
    path('cms/<str:pk>/update/', CMSUpdateView.as_view(), name='cms-update-view'),
    path('cms/', views.CMSListView, name='cms-list-view'),

    path('login/', views.LoginView, name='login-view'),
    path('logout/', views.LogoutView, name='logout-view'),

    path('reports/', views.ReportView, name='report-view'),

    path('users/', views.user_list_view, name='user-list-view'),

    path('banner/add/', BannerView.as_view(), name='banner-add-view'),
    path('banner/<str:pk>/update/', BannerUpdateView.as_view(),
         name='banner-update-view'),
    path('banners/', views.BannerListView, name='banner-list-view'),

    path('sales_report/', views.SalesReportView, name='sales-report-view'),

    path('configuration/add/', ConfigView.as_view(), name='config-add-view'),
    path('configuration/<str:pk>/update/',
         ConfigUpdateView.as_view(), name='config-update-view'),
    path('configurations/', views.ConfigListView, name='config-list-view'),


]
