from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import UserProfile
import hashlib


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def register_view(request):
    if request.session.get('user_id'):
        return redirect('dashboard:home')

    if request.method == 'POST':
        full_name    = request.POST.get('full_name', '').strip()
        email        = request.POST.get('email', '').strip().lower()
        password     = request.POST.get('password', '')
        confirm_pw   = request.POST.get('confirm_password', '')
        organization = request.POST.get('organization', '').strip()

        if len(full_name) < 2:
            messages.error(request, 'Full name must be at least 2 characters.')
            return render(request, 'accounts/register.html')
        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
            return render(request, 'accounts/register.html')
        if password != confirm_pw:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/register.html')
        if UserProfile.objects.filter(email=email).exists():
            messages.error(request, 'This email is already registered.')
            return render(request, 'accounts/register.html')

        UserProfile.objects.create(
            full_name=full_name,
            email=email,
            password=hash_password(password),
            role='industry_user',
            organization=organization,
        )
        messages.success(request, 'Account created successfully! Please login.')
        return redirect('accounts:login')

    return render(request, 'accounts/register.html')


def login_view(request):
    if request.session.get('user_id'):
        if request.session.get('user_role') == 'admin':
            return redirect('adminpanel:dashboard')
        return redirect('dashboard:home')

    if request.method == 'POST':
        email    = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')

        try:
            user = UserProfile.objects.get(
                email=email,
                password=hash_password(password),
                is_active=True
            )
            request.session['user_id']    = user.id
            request.session['user_name']  = user.full_name
            request.session['user_role']  = user.role
            request.session['user_email'] = user.email
            request.session['user_org']   = user.organization or ''

            messages.success(request, f'Welcome back, {user.full_name}!')
            if user.role == 'admin':
                return redirect('adminpanel:dashboard')
            return redirect('dashboard:home')

        except UserProfile.DoesNotExist:
            messages.error(request,
                'Invalid email or password, or account is inactive.')

    return render(request, 'accounts/login.html')


def logout_view(request):
    name = request.session.get('user_name', 'User')
    request.session.flush()
    messages.success(request, f'Goodbye, {name}! You have been logged out.')
    return redirect('accounts:login')


def profile_view(request):
    if not request.session.get('user_id'):
        return redirect('accounts:login')

    user = get_object_or_404(UserProfile, pk=request.session['user_id'])

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_profile':
            full_name    = request.POST.get('full_name', '').strip()
            organization = request.POST.get('organization', '').strip()

            if len(full_name) < 2:
                messages.error(request, 'Full name must be at least 2 characters.')
                return redirect('accounts:profile')

            user.full_name    = full_name
            user.organization = organization
            user.save()
            request.session['user_name'] = user.full_name
            request.session['user_org']  = user.organization
            messages.success(request, 'Profile updated successfully.')

        elif action == 'change_password':
            current = request.POST.get('current_password', '')
            new_pw  = request.POST.get('new_password', '')
            confirm = request.POST.get('confirm_password', '')

            if user.password != hash_password(current):
                messages.error(request, 'Current password is incorrect.')
            elif len(new_pw) < 6:
                messages.error(request, 'New password must be at least 6 characters.')
            elif new_pw != confirm:
                messages.error(request, 'New passwords do not match.')
            else:
                user.password = hash_password(new_pw)
                user.save()
                messages.success(request, 'Password changed successfully.')

        return redirect('accounts:profile')

    return render(request, 'accounts/profile.html', {'user': user})
