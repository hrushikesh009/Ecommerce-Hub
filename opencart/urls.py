from django.contrib import admin
from django.urls import path,include
import debug_toolbar

from django.conf.urls.static import static
from django.conf import settings

admin.site.site_header = 'OpenCart'
admin.site.index_title = 'Admin'
urlpatterns = [
    path('admin/', include('custom_admin.urls',namespace="custom_admin")),
    path('admin/', include('Product.urls',namespace="product")),
    path('store/',include('store.urls')),
    path('custom_admin/', admin.site.urls),
    path('__debug__/', include(debug_toolbar.urls)),
    path('pages/',include('django.contrib.flatpages.urls')),
    path('social-auth/',include('social_django.urls',namespace="social"))
]


urlpatterns += static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)

handler500 = 'store.views.server_error_view'
handler404 = 'store.views.page_not_found_view'

