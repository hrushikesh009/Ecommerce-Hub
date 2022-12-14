from django.conf.urls import handler404
from django.urls import path
from . import views
from .views import ContactUsView,MyPasswordChangeView,ProfileUpdateView,AddressAddView,AddressEditView,MyPasswordResetView,MyPasswordResetDoneView,MyPasswordResetConfirmView
app_name = 'store'

urlpatterns = [
    path('',views.HomeView,name = 'home-view'),
    path('product_detail/<int:pk>/', views.ProductDetailView, name='product-detail-view'),
    path('category/<str:category_title>/', views.CategoryView, name='category-view'),
    path('MyAccount/', ProfileUpdateView.as_view(), name='myaccount-view'),
    path('login/', views.LoginView, name='login-view'),
    path('reset-password/',MyPasswordResetView.as_view(),name='reset-password'),
    path('password-reset-done/',MyPasswordResetDoneView.as_view(),name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',MyPasswordResetConfirmView.as_view(),name='password_reset_confirm'),
    path('logout/',views.LogoutView, name='logout-view'),
    path('contact_us/',ContactUsView.as_view(),name = "contact-us-view"),
    path('password_change/',MyPasswordChangeView.as_view(),name = "password-change-view"),
    path('wishlist/', views.WishListView, name='wish-list-view'),
    path('wishlist/<int:pk>/add/', views.WishListAddView, name='wish-list-add-view'),
    path('wishlist/<int:pk>/delete/', views.WishListDeleteView, name='wish-list-delete-view'),
    path('address/', views.AddressListView, name='address-view'),
    path('address/add/', AddressAddView.as_view(), name='address-add-view'),
    path('address/<int:pk>/edit/', AddressEditView.as_view(), name='address-edit-view'),
    path('address/<int:pk>/delete/', views.AddressDeleteView, name='address-delete-view'),
    path('mycart/', views.CartListView, name='cart-list-view'),
    path('cart/<int:pk>/add', views.CartAddView, name='cart-add-view'),
    path('cart/<int:pk>/delete', views.CartDeleteView, name='cart-delete-view'),
    path('checkout/<str:coupon_name>/', views.CheckoutView, name='checkout-view'),
    path('payment/<uuid:order_id>/', views.PaymentView, name='payment-view'),
    path('Order/<uuid:order_id>/delete/', views.OrderDeleteView, name='order-delete-view'),
    path('myorder/', views.OrderView, name='order-view'),
    path('track-my-order/', views.TrackOrderView, name='track-order-view'),
    path('subscribe-newsletter/', views.SubscribeNewsletterView, name='subscribe-newsletter-view'),




]




