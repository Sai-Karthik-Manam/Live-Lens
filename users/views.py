from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .models import User, Profile
from .forms import SignupForm, ProfileForm

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('market:index')
    else:
        form = SignupForm()

    return render(request, 'users/signup.html', {
        'form': form
    })

def logout_view(request):
    logout(request)
    return redirect('market:index')

@login_required
def edit_profile(request):
    # SAFETY CHECK: Get the profile, or create it if it's missing (Fixes the crash)
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('market:dashboard')
    else:
        form = ProfileForm(instance=profile)
    
    return render(request, 'users/edit_profile.html', {
        'form': form
    })

def seller_profile(request, username):
    # Get the specific user by their username
    seller = get_object_or_404(User, username=username)
    # Get their unsold items
    items = seller.items.filter(is_sold=False)

    return render(request, 'users/seller_profile.html', {
        'seller': seller,
        'items': items
    })