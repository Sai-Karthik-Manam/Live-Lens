from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, Count, Avg
from django.core.paginator import Paginator
from django.http import JsonResponse

from .models import Item, Category, Wishlist
from .forms import NewItemForm

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ItemSerializer


# ---------------------------------------------------------------------------
# INDEX
# ---------------------------------------------------------------------------

def index(request):
    items_qs = Item.objects.filter(is_sold=False).order_by('-created_at')[:6]
    items = list(items_qs)
    categories = Category.objects.all()

    # Attach seller ratings to each item for the homepage cards
    from users.models import Review
    seller_ids = {it.seller_id for it in items}
    seller_stats = {}
    if seller_ids:
        stats = (
            Review.objects
            .filter(seller_id__in=seller_ids)
            .values('seller_id')
            .annotate(avg=Avg('rating'), count=Count('id'))
        )
        for s in stats:
            seller_stats[s['seller_id']] = {'avg': s['avg'] or 0, 'count': s['count'] or 0}

    for it in items:
        st = seller_stats.get(it.seller_id, {'avg': 0, 'count': 0})
        setattr(it, 'seller_avg_rating', round(st['avg'] or 0, 2))
        setattr(it, 'seller_review_count', st['count'] or 0)
        avg = st['avg'] or 0
        full = int(avg)
        half = 1 if (avg - full) >= 0.5 else 0
        empty = 5 - full - half
        setattr(it, 'seller_star_str', '★' * full + ('½' if half else '') + '☆' * empty)
        recent = Review.objects.filter(seller_id=it.seller_id).order_by('-created_at')[:3]
        setattr(it, 'seller_recent_reviews', list(recent))

    return render(request, 'market/index.html', {'items': items, 'categories': categories})


# ---------------------------------------------------------------------------
# DETAIL
# ---------------------------------------------------------------------------

def detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    related_items = Item.objects.filter(category=item.category, is_sold=False).exclude(pk=pk)[:3]

    is_wishlisted = False
    if request.user.is_authenticated:
        is_wishlisted = Wishlist.objects.filter(user=request.user, item=item).exists()

    return render(request, 'market/detail.html', {
        'item': item,
        'related_items': related_items,
        'is_wishlisted': is_wishlisted,
    })


# ---------------------------------------------------------------------------
# NEW / EDIT / DELETE
# ---------------------------------------------------------------------------

@login_required
def new(request):
    if request.method == 'POST':
        form = NewItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.seller = request.user
            item.save()

            # Auto background-removal for clothing items
            if item.product_type == 'clothing' and item.image:
                try:
                    from rembg import remove
                    import os
                    from django.conf import settings as django_settings

                    input_path = item.image.path
                    with open(input_path, 'rb') as f:
                        input_data = f.read()
                    output_data = remove(input_data)
                    output_path = input_path.rsplit('.', 1)[0] + '.png'
                    with open(output_path, 'wb') as f:
                        f.write(output_data)
                    relative_path = os.path.relpath(output_path, django_settings.MEDIA_ROOT)
                    item.image.name = relative_path.replace('\\', '/')
                    item.save()
                except Exception:
                    pass  # rembg not installed or failed — keep original image

            return redirect('market:detail', pk=item.id)
    else:
        form = NewItemForm()
    categories = Category.objects.all()
    return render(request, 'market/form.html', {'form': form, 'title': 'New Listing', 'categories': categories})


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
    return render(request, 'market/form.html', {'form': form, 'title': 'Edit Listing', 'categories': categories})


@login_required
def delete(request, pk):
    item = get_object_or_404(Item, pk=pk, seller=request.user)
    item.delete()
    return redirect('market:dashboard')


# ---------------------------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------------------------

@login_required
def dashboard(request):
    items = Item.objects.filter(seller=request.user)
    metrics = items.aggregate(
        total_items=Count('id'),
        sold_items=Count('id', filter=Q(is_sold=True)),
        total_revenue=Sum('price', filter=Q(is_sold=True)),
        active_revenue=Sum('price', filter=Q(is_sold=False)),
    )
    revenue = metrics['total_revenue'] or 0
    potential_revenue = metrics['active_revenue'] or 0
    return render(request, 'market/dashboard.html', {
        'items': items,
        'metrics': metrics,
        'revenue': revenue,
        'potential_revenue': potential_revenue,
    })


@login_required
def mark_sold(request, pk):
    item = get_object_or_404(Item, pk=pk, seller=request.user)
    item.is_sold = not item.is_sold
    item.save()
    return redirect('market:dashboard')


# ---------------------------------------------------------------------------
# BROWSE (with search, category filter, sort, pagination, wishlisted_ids)
# ---------------------------------------------------------------------------

def browse(request):
    query = request.GET.get('query', '')
    category_id = request.GET.get('category', 0)
    sort = request.GET.get('sort', 'newest')
    categories = Category.objects.all()
    items = Item.objects.filter(is_sold=False)

    if query:
        category_match = Category.objects.filter(name__iexact=query).first()
        if category_match:
            items = items.filter(category=category_match)
            try:
                category_id = int(category_match.id)
            except Exception:
                category_id = category_match.id
        else:
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

    paginator = Paginator(items, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

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
        'category_id': int(category_id) if category_id else 0,
        'sort': sort,
        'wishlisted_ids': wishlisted_ids,
    })


# ---------------------------------------------------------------------------
# WISHLIST
# ---------------------------------------------------------------------------

@login_required
def toggle_wishlist(request, pk):
    item = get_object_or_404(Item, pk=pk)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, item=item)
    if not created:
        wishlist_item.delete()
        action = 'removed'
    else:
        action = 'added'

    is_ajax = (
        request.headers.get('x-requested-with') == 'XMLHttpRequest'
        or 'application/json' in request.META.get('HTTP_ACCEPT', '')
    )
    if is_ajax:
        return JsonResponse({'status': action})
    return redirect(request.META.get('HTTP_REFERER', 'market:browse'))


@login_required
def wishlist(request):
    wishlist_items = (
        Wishlist.objects.filter(user=request.user)
        .select_related('item')
        .order_by('-created_at')
    )
    return render(request, 'market/wishlist.html', {'wishlist_items': wishlist_items})


# ---------------------------------------------------------------------------
# AR TRY-ON
# ---------------------------------------------------------------------------

def try_on(request, pk):
    item = get_object_or_404(Item, pk=pk)
    return render(request, 'market/try_on.html', {'item': item})


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------

@api_view(['GET'])
def api_item_list(request):
    """Returns JSON list of all available items (for mobile apps)."""
    items = Item.objects.filter(is_sold=False)
    serializer = ItemSerializer(items, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def api_lookup_by_barcode(request):
    """Lookup an item by barcode or text query."""
    barcode = request.GET.get('barcode') or request.GET.get('q')
    if not barcode:
        return Response({'error': 'Provide barcode or q parameter'}, status=400)

    item = Item.objects.filter(barcode__iexact=barcode, is_sold=False).first()
    if not item:
        item = Item.objects.filter(
            Q(title__icontains=barcode) | Q(category__name__icontains=barcode),
            is_sold=False,
        ).first()

    if not item:
        return Response({}, status=404)

    serializer = ItemSerializer(item)
    return Response(serializer.data)

def live_ar(request):
    return render(request, 'market/live_ar.html')
