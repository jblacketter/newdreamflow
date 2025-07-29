from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from .forms import CustomUserCreationForm, UserProfileForm


def register(request):
    """User registration view."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome to Dream Journal!')
            return redirect('dreams:list')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile(request):
    """User profile view."""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('users:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'users/profile.html', {'form': form})


@login_required
def delete_account(request):
    """Handle account deletion."""
    if request.method == 'POST':
        # Verify password for security
        password = request.POST.get('password')
        if request.user.check_password(password):
            user = request.user
            logout(request)
            user.delete()
            messages.success(request, 'Your account has been successfully deleted.')
            return redirect('home')
        else:
            messages.error(request, 'Incorrect password. Account deletion cancelled.')
            return redirect('users:delete_account')
    
    return render(request, 'users/delete_account.html')


@login_required
@require_http_methods(["POST"])
def confirm_delete_account(request):
    """Confirm account deletion via AJAX."""
    password = request.POST.get('password')
    if request.user.check_password(password):
        user = request.user
        logout(request)
        user.delete()
        return JsonResponse({'success': True, 'redirect_url': '/'})
    else:
        return JsonResponse({'success': False, 'error': 'Incorrect password'})
