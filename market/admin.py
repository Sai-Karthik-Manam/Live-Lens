from django.contrib import admin
from .models import Category, Item, Wishlist


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'product_type', 'size', 'price', 'is_sold', 'seller')
    list_filter = ('category', 'product_type', 'is_sold', 'condition')
    search_fields = ('title', 'description', 'barcode', 'brand')


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'item', 'created_at')


admin.site.register(Category)
