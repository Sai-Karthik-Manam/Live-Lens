from django.urls import path
from . import views

app_name = 'market'

urlpatterns = [
    path('', views.index, name='index'),
    path('browse/', views.browse, name='browse'),
    path('new/', views.new, name='new'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Item detail / CRUD
    path('item/<int:pk>/', views.detail, name='detail'),
    path('item/<int:pk>/edit/', views.edit, name='edit'),
    path('item/<int:pk>/delete/', views.delete, name='delete'),
    path('item/<int:pk>/mark-sold/', views.mark_sold, name='mark_sold'),

    # AR Try-On
    path('item/<int:pk>/try-on/', views.try_on, name='try_on'),

    # Wishlist
    path('item/<int:pk>/wishlist/', views.toggle_wishlist, name='toggle_wishlist'),
    path('wishlist/', views.wishlist, name='wishlist'),

    # REST API
    path('api/items/', views.api_item_list, name='api_item_list'),
    path('api/items/lookup/', views.api_lookup_by_barcode, name='api_item_lookup'),
    path('live-ar/', views.live_ar, name='live_ar'),
]
