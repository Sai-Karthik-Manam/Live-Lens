from django.contrib import admin
from .models import Category, Item

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):  # <--- CHANGED FROM admin.site.ModelAdmin
    list_display = ('title', 'price', 'category', 'is_sold')
    list_filter = ('category', 'is_sold')
    search_fields = ('title', 'description')

admin.site.register(Category)