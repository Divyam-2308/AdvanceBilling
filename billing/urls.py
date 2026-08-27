from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('distributor/dashboard/', views.distributor_dashboard, name='distributor_dashboard'),
]
