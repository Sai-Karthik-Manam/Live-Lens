from django.urls import path
from . import views

app_name = 'market'

urlpatterns = [
    path('', views.index, name='index'),
    path('item/<int:pk>/', views.detail, name='detail'),
    path('item/<int:pk>/delete/', views.delete, name='delete'),
    path('item/<int:pk>/edit/', views.edit, name='edit'),
    path('item/<int:pk>/mark-sold/', views.mark_sold, name='mark_sold'),
    path('new/', views.new, name='new'),
    path('browse/', views.browse, name='browse'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Wishlist URLs
    path('item/<int:pk>/wishlist/', views.toggle_wishlist, name='toggle_wishlist'),
    path('wishlist/', views.wishlist, name='wishlist'),

    # API URL
    path('api/items/', views.api_item_list, name='api_item_list'),
]