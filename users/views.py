from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from .models import User, Profile, Review
from .forms import SignupForm, ProfileForm, ReviewForm


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('market:index')
    else:
        form = SignupForm()
    return render(request, 'users/signup.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('market:index')


@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('market:dashboard')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'users/edit_profile.html', {'form': form})


def seller_profile(request, username):
    seller = get_object_or_404(User, username=username)
    items = seller.items.filter(is_sold=False)
    reviews = seller.reviews_received.all()

    # Calculate average rating
    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg']
    avg_rating = round(avg_rating, 1) if avg_rating else None

    # Check if the current user has already left a review
    user_review = None
    can_review = False
    review_form = None

    if request.user.is_authenticated and request.user != seller:
        user_review = Review.objects.filter(seller=seller, reviewer=request.user).first()
        can_review = user_review is None  # Can only review if hasn't reviewed yet
        if can_review:
            review_form = ReviewForm()

    return render(request, 'users/seller_profile.html', {
        'seller': seller,
        'items': items,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_form': review_form,
        'can_review': can_review,
        'user_review': user_review,
    })


@login_required
def leave_review(request, username):
    seller = get_object_or_404(User, username=username)

    # Can't review yourself
    if request.user == seller:
        return redirect('users:seller_profile', username=username)

    # Can't review twice
    if Review.objects.filter(seller=seller, reviewer=request.user).exists():
        return redirect('users:seller_profile', username=username)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.seller = seller
            review.reviewer = request.user
            review.save()

    return redirect('users:seller_profile', username=username)