from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, Count
from django.core.paginator import Paginator
from .models import Item, Category, Wishlist
from .forms import NewItemForm

# DRF Imports (For the API)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ItemSerializer

def index(request):
    items = Item.objects.filter(is_sold=False)[0:6]
    categories = Category.objects.all()
    return render(request, 'market/index.html', {
        'items': items,
        'categories': categories,
    })

def detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    related_items = Item.objects.filter(category=item.category, is_sold=False).exclude(pk=pk)[0:3]
    
    # Check if the current user has wishlisted this item
    is_wishlisted = False
    if request.user.is_authenticated:
        is_wishlisted = Wishlist.objects.filter(user=request.user, item=item).exists()

    return render(request, 'market/detail.html', {
        'item': item,
        'related_items': related_items,
        'is_wishlisted': is_wishlisted,
    })

@login_required
def new(request):
    if request.method == 'POST':
        form = NewItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.seller = request.user
            item.save()
            return redirect('market:detail', pk=item.id)
    else:
        form = NewItemForm()
    return render(request, 'market/form.html', {
        'form': form,
        'title': 'New Item',
    })

@login_required
def edit(request, pk):
    item = get_object_or_404(Item, pk=pk, seller=request.user)
    if request.method == 'POST':
        form = NewItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect('market:detail', pk=item.id)
    else:
        form = NewItemForm(instance=item)
    return render(request, 'market/form.html', {
        'form': form,
        'title': 'Edit Item',
    })

@login_required
def delete(request, pk):
    item = get_object_or_404(Item, pk=pk, seller=request.user)
    item.delete()
    return redirect('market:dashboard')

@login_required
def dashboard(request):
    items = Item.objects.filter(seller=request.user)
    
    metrics = items.aggregate(
        total_items=Count('id'),
        sold_items=Count('id', filter=Q(is_sold=True)),
        total_revenue=Sum('price', filter=Q(is_sold=True)),
        active_revenue=Sum('price', filter=Q(is_sold=False))
    )
    
    revenue = metrics['total_revenue'] if metrics['total_revenue'] else 0
    potential_revenue = metrics['active_revenue'] if metrics['active_revenue'] else 0

    return render(request, 'market/dashboard.html', {
        'items': items,
        'metrics': metrics,
        'revenue': revenue,
        'potential_revenue': potential_revenue
    })

@login_required
def mark_sold(request, pk):
    item = get_object_or_404(Item, pk=pk, seller=request.user)
    item.is_sold = not item.is_sold
    item.save()
    return redirect('market:dashboard')

def browse(request):
    query = request.GET.get('query', '')
    category_id = request.GET.get('category', 0)
    sort = request.GET.get('sort', 'newest')
    categories = Category.objects.all()
    items = Item.objects.filter(is_sold=False)

    if query:
        items = items.filter(Q(title__icontains=query) | Q(description__icontains=query))

    if category_id:
        items = items.filter(category_id=category_id)

    if sort == 'price_asc':
        items = items.order_by('price')
    elif sort == 'price_desc':
        items = items.order_by('-price')
    else:
        items = items.order_by('-created_at')

    paginator = Paginator(items, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Pass the user's wishlisted item IDs so cards can show filled/empty hearts
    wishlisted_ids = set()
    if request.user.is_authenticated:
        wishlisted_ids = set(
            Wishlist.objects.filter(user=request.user).values_list('item_id', flat=True)
        )

    return render(request, 'market/browse.html', {
        'items': page_obj,
        'page_obj': page_obj,
        'query': query,
        'categories': categories,
        'category_id': int(category_id),
        'sort': sort,
        'wishlisted_ids': wishlisted_ids,
    })


# --- NEW WISHLIST VIEWS ---

@login_required
def toggle_wishlist(request, pk):
    """Adds item to wishlist if not saved, removes it if already saved."""
    item = get_object_or_404(Item, pk=pk)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, item=item)
    
    if not created:
        # Already wishlisted — remove it
        wishlist_item.delete()

    # Redirect back to wherever the user came from
    next_url = request.GET.get('next', 'market:browse')
    return redirect(request.META.get('HTTP_REFERER', 'market:browse'))


@login_required
def wishlist(request):
    """Shows the user's saved items."""
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('item').order_by('-created_at')
    return render(request, 'market/wishlist.html', {
        'wishlist_items': wishlist_items,
    })


# --- API VIEW ---
@api_view(['GET'])
def api_item_list(request):
    """Returns JSON data for Mobile Apps"""
    items = Item.objects.filter(is_sold=False)
    serializer = ItemSerializer(items, many=True)
    return Response(serializer.data)