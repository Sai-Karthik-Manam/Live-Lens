from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import LoginForm, CustomPasswordResetForm, CustomSetPasswordForm

app_name = 'users'

urlpatterns = [
    # Auth URLs
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html', authentication_form=LoginForm), name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Password Reset URLs
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='users/password_reset.html', form_class=CustomPasswordResetForm), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html', form_class=CustomSetPasswordForm), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), name='password_reset_complete'),

    # Profile URLs
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('u/<str:username>/', views.seller_profile, name='seller_profile'),

    # NEW: Review URL
    path('u/<str:username>/review/', views.leave_review, name='leave_review'),
]