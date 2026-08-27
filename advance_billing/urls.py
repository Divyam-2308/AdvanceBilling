from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from billing import views as billing_views

urlpatterns = [
    path('dashboard/admin/', billing_views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/distributor/', billing_views.distributor_dashboard, name='distributor_dashboard'),
    path('django-admin/', admin.site.urls),
    path('', include('billing.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
