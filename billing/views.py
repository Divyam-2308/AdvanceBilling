from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.cache import cache
from urllib.parse import urlparse

MAX_LOGIN_ATTEMPTS = 5
LOGIN_LOCKOUT_SECONDS = 300  # 5 minutes


def index(request):
    return redirect('billing:login')


def _is_safe_next_url(url):
    if not url:
        return False
    parsed = urlparse(url)
    return parsed.scheme == '' and parsed.netloc == '' and url.startswith('/')


def _get_lockout_key(ip):
    return f'login_lockout_{ip}'


def _get_attempt_key(ip):
    return f'login_attempts_{ip}'


def login_view(request):
    if request.user.is_authenticated:
        return _redirect_by_role(request.user)

    client_ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', '127.0.0.1'))
    if ',' in client_ip:
        client_ip = client_ip.split(',')[0].strip()

    lockout_key = _get_lockout_key(client_ip)
    if cache.get(lockout_key):
        messages.error(request, 'Too many failed attempts. Please try again in 5 minutes.')
        return render(request, 'registration/login.html', {'next': request.GET.get('next', '')})

    next_url = request.GET.get('next', '') or request.POST.get('next', '')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if not user.is_active:
                messages.error(request, 'Your account is inactive. Contact the administrator.')
                return render(request, 'registration/login.html', {'next': next_url})

            login(request, user)
            cache.delete(_get_attempt_key(client_ip))

            if _is_safe_next_url(next_url):
                return redirect(next_url)
            return _redirect_by_role(user)
        else:
            attempt_key = _get_attempt_key(client_ip)
            attempts = cache.get(attempt_key, 0) + 1
            cache.set(attempt_key, attempts, LOGIN_LOCKOUT_SECONDS)

            if attempts >= MAX_LOGIN_ATTEMPTS:
                cache.set(lockout_key, True, LOGIN_LOCKOUT_SECONDS)
                messages.error(request, 'Too many failed attempts. Account locked for 5 minutes.')
            else:
                remaining = MAX_LOGIN_ATTEMPTS - attempts
                messages.error(request, f'Invalid username or password. {remaining} attempt{"s" if remaining != 1 else ""} remaining.')

    return render(request, 'registration/login.html', {'next': next_url})


def logout_view(request):
    logout(request)
    return redirect('billing:login')


@login_required
def admin_dashboard(request):
    if not request.user.is_admin_user:
        messages.warning(request, 'You do not have admin access.')
        return redirect('distributor_dashboard')
    return render(request, 'billing/admin_dashboard.html')


@login_required
def distributor_dashboard(request):
    if not request.user.is_distributor_user and not request.user.is_admin_user:
        messages.warning(request, 'Access denied.')
        return redirect('billing:login')
    return render(request, 'billing/distributor_dashboard.html')


def _redirect_by_role(user):
    if user.is_admin_user:
        return redirect('admin_dashboard')
    return redirect('distributor_dashboard')
