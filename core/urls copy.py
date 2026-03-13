from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('market.urls')),
    path('admin/', admin.site.urls),
    path('auth/', include('users.urls')),
    path('inbox/', include('conversation.urls')),   # ← ADDED
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
