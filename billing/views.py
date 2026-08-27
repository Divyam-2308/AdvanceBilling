from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def index(request):
    return redirect('billing:login')


def login_view(request):
    if request.user.is_authenticated:
        return _redirect_by_role(request.user)

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return _redirect_by_role(user)
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'registration/login.html')


def logout_view(request):
    logout(request)
    return redirect('billing:login')


@login_required
def admin_dashboard(request):
    if not request.user.is_admin_user:
        messages.warning(request, 'You do not have admin access.')
        return redirect('billing:distributor_dashboard')
    return render(request, 'billing/admin_dashboard.html')


@login_required
def distributor_dashboard(request):
    if not request.user.is_distributor_user and not request.user.is_admin_user:
        messages.warning(request, 'Access denied.')
        return redirect('billing:login')
    return render(request, 'billing/distributor_dashboard.html')


def _redirect_by_role(user):
    if user.is_admin_user:
        return redirect('billing:admin_dashboard')
    return redirect('billing:distributor_dashboard')
