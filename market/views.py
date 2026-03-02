from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, Count, Avg
from django.core.paginator import Paginator
from .models import Item, Category, Wishlist
from .forms import NewItemForm

# DRF Imports (For the API)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ItemSerializer

from django.http import JsonResponse

def index(request):
    # Take a small set of newest available items for the homepage
    items_qs = Item.objects.filter(is_sold=False).order_by('-created_at')[:6]
    items = list(items_qs)
    categories = Category.objects.all()

    # Compute seller ratings (avg and count) and attach to items so templates can read them easily
    seller_ids = {it.seller_id for it in items}
    from users.models import Review

    seller_stats = {}
    if seller_ids:
        stats = Review.objects.filter(seller_id__in=seller_ids).values('seller_id').annotate(avg=Avg('rating'), count=Count('id'))
        for s in stats:
            seller_stats[s['seller_id']] = {
                'avg': s['avg'] or 0,
                'count': s['count'] or 0
            }

    # Attach attributes to item instances for template convenience
    for it in items:
        st = seller_stats.get(it.seller_id, {'avg': 0, 'count': 0})
        setattr(it, 'seller_avg_rating', round(st['avg'] or 0, 2))
        setattr(it, 'seller_review_count', st['count'] or 0)
        # Build a simple star string (e.g. ★★★★☆ or ★★★½☆) for easy template rendering
        avg = st['avg'] or 0
        full = int(avg)
        half = 1 if (avg - full) >= 0.5 else 0
        empty = 5 - full - half
        star_str = '★' * full + ('½' if half else '') + '☆' * empty
        setattr(it, 'seller_star_str', star_str)

        # Attach recent reviews (latest 3) for the seller to show in a tooltip
        recent = Review.objects.filter(seller_id=it.seller_id).order_by('-created_at')[:3]
        setattr(it, 'seller_recent_reviews', list(recent))

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
    categories = Category.objects.all()
    return render(request, 'market/form.html', {
        'form': form,
        'title': 'New Item',
        'categories': categories,
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
    categories = Category.objects.all()
    return render(request, 'market/form.html', {
        'form': form,
        'title': 'Edit Item',
        'categories': categories,
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
        # If the query exactly matches a category name, prefer that category
        category_match = Category.objects.filter(name__iexact=query).first()
        if category_match:
            items = items.filter(category=category_match, is_sold=False)
            # set category_id so the UI reflects the selected category
            try:
                category_id = int(category_match.id)
            except Exception:
                category_id = category_match.id
        else:
            # otherwise search title, description, or category name
            items = items.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(category__name__icontains=query)
            )

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
    # If it already existed, remove it and mark action as removed
    if not created:
        wishlist_item.delete()
        action = 'removed'
    else:
        action = 'added'

    # If the request is AJAX/fetch (X-Requested-With) or expects JSON, return a JSON response
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.META.get('HTTP_ACCEPT', '')
    if is_ajax:
        return JsonResponse({'status': action})

    # Fallback: redirect back to wherever the user came from
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


@api_view(['GET'])
def api_lookup_by_barcode(request):
    """Lookup item by barcode or query string. Returns first matching item."""
    barcode = request.GET.get('barcode') or request.GET.get('q')
    if not barcode:
        return Response({'error': 'Provide barcode or q parameter'}, status=400)

    # Try exact barcode match first
    item = Item.objects.filter(barcode__iexact=barcode, is_sold=False).first()
    if not item:
        # Fallback: search title or slug-like match
        item = Item.objects.filter(Q(title__icontains=barcode) | Q(category__name__icontains=barcode), is_sold=False).first()

    if not item:
        return Response({}, status=404)

    serializer = ItemSerializer(item)
    return Response(serializer.data)