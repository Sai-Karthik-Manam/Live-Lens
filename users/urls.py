from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import LoginForm

app_name = 'users'

urlpatterns = [
    # Auth URLs
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html', authentication_form=LoginForm), name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Profile URLs
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('u/<str:username>/', views.seller_profile, name='seller_profile'),

    # NEW: Review URL
    path('u/<str:username>/review/', views.leave_review, name='leave_review'),
]