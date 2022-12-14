from django.urls import path
from . import views
from .views import ProductView,ProductUpdateView,CategoryView,CategoryUpdateView,AttributeUpdateView,AttributeView,CouponView,CouponUpdateView

app_name = 'product'

urlpatterns = [
    path('product/add/',ProductView.as_view(),name = 'product-add-view'),
    path('product/<str:pk>/update/',ProductUpdateView.as_view(),name = 'product-update-view'),
    path('products/',views.ProductListView,name= 'product-list-view'),
    path('category/add/',CategoryView.as_view(),name = 'category-add-view'),
    path('category/<str:pk>/update/',CategoryUpdateView.as_view(),name = 'category-update-view'),
    path('categories/',views.CategoryListView,name= 'category-list-view'),
    path('attribute/add/',AttributeView.as_view(),name = 'attribute-add-view'),
    path('attribute/<str:pk>/update/',AttributeUpdateView.as_view(),name = 'attribute-update-view'),
    path('attributes/',views.AttributeListView,name= 'attribute-list-view'),
    path('coupons/',views.CouponListView,name= 'coupon-list-view'),
    path('coupon/add/',CouponView.as_view(),name = 'coupon-add-view'),
    path('coupon/<str:pk>/update/',CouponUpdateView.as_view(),name = 'coupon-update-view'),
    path('orders/',views.OrderListView,name = "order-list-view"),
    path('order-detail/<str:pk>/',views.OrderDetailView,name = "order-detail-view")
    
]