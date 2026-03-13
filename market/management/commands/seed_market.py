from decimal import Decimal
import os
import random
import urllib.request

from decimal import Decimal
import os
import random
import urllib.request
import json

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils.text import slugify

from market.models import Category, Item


class Command(BaseCommand):
    help = 'Seed the database with categories and sample items for the market app. Use --use-api dummyjson to fetch real product data.'

    def add_arguments(self, parser):
        parser.add_argument('--use-api', choices=['dummyjson', 'fakestore'], help='Fetch products from a public API and seed them as-is')
        parser.add_argument('--api-url', help='Custom API URL that returns a JSON array of products')
        parser.add_argument('--remove-local', action='store_true', help='Remove the first 20 locally seeded placeholder items per category')
        parser.add_argument('--per-category', action='store_true', help='Fetch products from the API separately for each existing Category')

    def handle(self, *args, **options):
        User = get_user_model()

        # Ensure a seller exists
        user = User.objects.first()
        if not user:
            user = User.objects.create_user(
                username='seeduser', email='seed@example.com', password='password123'
            )
            self.stdout.write(self.style.SUCCESS(f'Created seed user: {user.username}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Using existing user: {user.username}'))

        # If remove-local flag passed, delete the placeholder items
        if options.get('remove_local'):
            self._remove_local_seed(user)
            return

        # If API option passed, fetch products from API and seed directly
        api_choice = options.get('use_api')
        api_url = options.get('api_url')
        per_category = options.get('per_category')
        if api_choice or api_url:
            self._seed_from_api(api_choice, api_url, user, per_category=per_category)
            return

        # Fallback: create categories and local sample items (existing behavior)
        category_names = ['Electronics', 'Books', 'Clothing', 'Home', 'Toys']
        for name in category_names:
            slug = name.lower()
            cat, created = Category.objects.get_or_create(name=name, slug=slug)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Category already exists: {name}'))

        # Create 20 items per category with relevant images
        for cat in Category.objects.all():
            for i in range(1, 21):
                title = f"{cat.name} Item {i}"
                desc = f"{cat.name} - A quality {cat.name.lower()} product, sample #{i}."
                # Price ranges by category (simple heuristic)
                if cat.name.lower() == 'electronics':
                    price = Decimal(str(round(random.uniform(20, 300), 2)))
                elif cat.name.lower() == 'books':
                    price = Decimal(str(round(random.uniform(5, 60), 2)))
                elif cat.name.lower() == 'clothing':
                    price = Decimal(str(round(random.uniform(10, 120), 2)))
                elif cat.name.lower() == 'home':
                    price = Decimal(str(round(random.uniform(8, 150), 2)))
                else:
                    price = Decimal(str(round(random.uniform(5, 80), 2)))

                item, created = Item.objects.get_or_create(
                    title=title,
                    seller=user,
                    defaults={
                        'description': desc,
                        'price': price,
                        'category': cat,
                    }
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created item: {title}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Item already exists: {title}'))

                # Download and attach a placeholder image if none exists
                try:
                    image_dir = os.path.join(settings.MEDIA_ROOT, 'item_images')
                    os.makedirs(image_dir, exist_ok=True)
                    filename = f"{slugify(cat.name)}-{i}.jpg"
                    filepath = os.path.join(image_dir, filename)

                    if not os.path.exists(filepath):
                        # Use picsum.photos seeded by category+index so images are relevant/deterministic
                        url = f'https://picsum.photos/seed/{slugify(cat.name)}-{i}/800/600'
                        try:
                            urllib.request.urlretrieve(url, filepath)
                            self.stdout.write(self.style.SUCCESS(f'Downloaded image for: {title}'))
                        except Exception as e:
                            self.stdout.write(self.style.WARNING(f'Failed to download image for {title}: {e}'))

                    # Save relative path into ImageField if not set
                    rel_path = os.path.join('item_images', filename)
                    if not item.image:
                        item.image = rel_path
                        item.save()
                        self.stdout.write(self.style.SUCCESS(f'Attached image to item: {title}'))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Error attaching image for {title}: {e}'))

        self.stdout.write(self.style.SUCCESS('Seeding complete.'))

    def _remove_local_seed(self, user):
        """Removes the placeholder items seeded locally (titles like "<Category> Item N").

        Only removes up to the first 20 items per category and only items belonging to the seed user.
        """
        self.stdout.write(self.style.WARNING('Removing local seeded items (up to 20 per category)...'))
        deleted_count = 0
        for cat in Category.objects.all():
            prefix = f"{cat.name} Item "
            qs = Item.objects.filter(title__startswith=prefix, seller=user)
            # Collect candidates and remove those ending with a number (1..20)
            to_delete = []
            for item in qs:
                suffix = item.title[len(prefix):]
                if suffix.isdigit():
                    num = int(suffix)
                    if 1 <= num <= 20:
                        to_delete.append(item)

            for item in to_delete:
                item_title = item.title
                item.delete()
                deleted_count += 1
                self.stdout.write(self.style.SUCCESS(f'Deleted: {item_title}'))

        self.stdout.write(self.style.SUCCESS(f'Removal complete. Total items deleted: {deleted_count}'))

    def _seed_from_api(self, api_choice, api_url, user, per_category=False):
        """Fetch products from a public API and seed them as-is.

        Supports:
        - dummyjson: https://dummyjson.com/products (images, category, price, description, title)
        - fakestore: https://fakestoreapi.com/products
        - custom api_url: expects JSON array of products with keys (title, description, price, category, images or image)
        """
        # If per_category is requested, iterate repository Categories and fetch products per category
        image_dir = os.path.join(settings.MEDIA_ROOT, 'item_images')
        os.makedirs(image_dir, exist_ok=True)

        if per_category:
            self.stdout.write(self.style.SUCCESS('Seeding products per category from API...'))
            for cat in Category.objects.all():
                # Try to construct API category endpoint; fall back to fetching all products and filtering
                cat_slug = slugify(cat.name)
                attempted_urls = []

                if api_url:
                    # If a custom API base is supplied, try appending /category/{slug}
                    attempted_urls.append(api_url.rstrip('/') + f'/category/{cat_slug}')
                elif api_choice == 'dummyjson':
                    attempted_urls.append(f'https://dummyjson.com/products/category/{cat_slug}')
                elif api_choice == 'fakestore':
                    attempted_urls.append(f'https://fakestoreapi.com/products/category/{cat_slug}')

                products = None
                for url in attempted_urls:
                    self.stdout.write(self.style.SUCCESS(f'Trying category URL: {url}'))
                    try:
                        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (seed-script)'})
                        with urllib.request.urlopen(req, timeout=30) as resp:
                            raw = resp.read()
                            data = json.loads(raw)
                            # dummyjson may return dict with products, fakestore returns list
                            if isinstance(data, dict) and 'products' in data:
                                products = data['products']
                            elif isinstance(data, list):
                                products = data
                            else:
                                products = None
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'Category URL failed: {e}'))
                        products = None

                # If category-specific fetch failed or not available, fetch full list and filter
                if products is None:
                    # Fetch full product set depending on API
                    if api_url:
                        fetch_url = api_url
                    elif api_choice == 'dummyjson':
                        fetch_url = 'https://dummyjson.com/products?limit=0'
                    elif api_choice == 'fakestore':
                        fetch_url = 'https://fakestoreapi.com/products'
                    else:
                        self.stdout.write(self.style.ERROR('Unknown API choice'))
                        return

                    self.stdout.write(self.style.SUCCESS(f'Fetching full product list to filter for category: {cat.name}'))
                    try:
                        req = urllib.request.Request(fetch_url, headers={'User-Agent': 'Mozilla/5.0 (seed-script)'})
                        with urllib.request.urlopen(req, timeout=30) as resp:
                            raw = resp.read()
                            data = json.loads(raw)
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Failed to fetch products: {e}'))
                        continue

                    if isinstance(data, dict) and 'products' in data:
                        all_products = data['products']
                    elif isinstance(data, list):
                        all_products = data
                    else:
                        self.stdout.write(self.style.ERROR('Unexpected API response format'))
                        continue

                    # Filter heuristically by matching category string (case-insensitive substring)
                    all_lower = cat.name.lower()
                    products = [p for p in all_products if p.get('category') and all_lower in p.get('category', '').lower()]

                if not products:
                    self.stdout.write(self.style.WARNING(f'No products found for category: {cat.name}'))
                    continue

                # Seed the products for this category
                for p in products:
                    title = p.get('title') or p.get('name')
                    description = p.get('description', '')
                    price_val = p.get('price', 0)
                    try:
                        price = Decimal(str(price_val))
                    except Exception:
                        price = Decimal('0')

                    # Use current cat (we're seeding per-category)
                    category_name = cat.name
                    cat_slug = slugify(category_name)[:50]
                    cat_obj, _ = Category.objects.get_or_create(name=category_name.title(), slug=cat_slug)

                    item, created = Item.objects.get_or_create(
                        title=title,
                        seller=user,
                        defaults={
                            'description': description,
                            'price': price,
                            'category': cat_obj,
                        }
                    )

                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Created item: {title}'))
                    else:
                        self.stdout.write(self.style.WARNING(f'Item already exists: {title}'))

                    # Attach first available image
                    images = []
                    if 'images' in p and isinstance(p['images'], list):
                        images = p['images']
                    elif 'image' in p:
                        images = [p['image']]

                    if images:
                        first = images[0]
                        # Save image to media and attach
                        try:
                            filename = f"{slugify(title)[:50]}.jpg"
                            filepath = os.path.join(image_dir, filename)
                            if not os.path.exists(filepath):
                                try:
                                    req_img = urllib.request.Request(first, headers={'User-Agent': 'Mozilla/5.0 (seed-script)'} )
                                    with urllib.request.urlopen(req_img, timeout=30) as rimg:
                                        with open(filepath, 'wb') as out_f:
                                            out_f.write(rimg.read())
                                    self.stdout.write(self.style.SUCCESS(f'Downloaded image for: {title}'))
                                except Exception as e:
                                    self.stdout.write(self.style.WARNING(f'Failed to download image for {title}: {e}'))
                            rel_path = os.path.join('item_images', filename)
                            if not item.image:
                                item.image = rel_path
                                item.save()
                                self.stdout.write(self.style.SUCCESS(f'Attached image to item: {title}'))
                        except Exception as e:
                            self.stdout.write(self.style.WARNING(f'Failed to attach image for {title}: {e}'))

                # done per-category loop
            # continue to next category
            return

        self.stdout.write(self.style.SUCCESS('API seeding complete.'))
