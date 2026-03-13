#!/usr/bin/env python3
"""
Live-Lens Patch Verification Script
====================================
Run this from your Live-Lens project root:
    python verify_patch.py

It checks that every file from the patch is present and contains
the expected code signatures.
"""

import os
import sys

# ANSI colours
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

passed = 0
failed = 0
warnings = 0


def ok(label):
    global passed
    passed += 1
    print(f"  {GREEN}✓{RESET}  {label}")


def fail(label, hint=""):
    global failed
    failed += 1
    msg = f"  {RED}✗{RESET}  {label}"
    if hint:
        msg += f"\n       {YELLOW}→ {hint}{RESET}"
    print(msg)


def warn(label, hint=""):
    global warnings
    warnings += 1
    msg = f"  {YELLOW}⚠{RESET}  {label}"
    if hint:
        msg += f"\n       {YELLOW}→ {hint}{RESET}"
    print(msg)


def section(title):
    print(f"\n{BOLD}{CYAN}{'─'*55}{RESET}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"{BOLD}{CYAN}{'─'*55}{RESET}")


def file_exists(path, hint=""):
    if os.path.isfile(path):
        ok(f"EXISTS  {path}")
        return True
    else:
        fail(f"MISSING {path}", hint or "Copy this file from the patch zip")
        return False


def contains(path, *needles, label=None):
    """Check that a file contains all the given strings."""
    if not os.path.isfile(path):
        fail(f"MISSING {path} (cannot check contents)")
        return False
    with open(path, encoding="utf-8", errors="ignore") as f:
        content = f.read()
    missing = [n for n in needles if n not in content]
    display = label or f"{path}"
    if not missing:
        ok(f"CONTENT {display}")
        return True
    else:
        fail(f"CONTENT {display}",
             f"Missing: {', '.join(repr(m) for m in missing)}")
        return False


def not_contains(path, needle, label=None):
    """Check that a file does NOT contain a string (detects old code)."""
    if not os.path.isfile(path):
        return  # already caught by file_exists
    with open(path, encoding="utf-8", errors="ignore") as f:
        content = f.read()
    display = label or path
    if needle not in content:
        ok(f"CLEAN   {display}")
    else:
        warn(f"OLD CODE {display}",
             f"Still contains: {repr(needle)} — patch may not have been applied")


# ─────────────────────────────────────────────────────────────────────────────
# 1. FILE EXISTENCE CHECKS
# ─────────────────────────────────────────────────────────────────────────────
section("1. Required Files Exist")

REQUIRED_FILES = [
    # market
    "market/models.py",
    "market/views.py",
    "market/forms.py",
    "market/urls.py",
    "market/serializers.py",
    "market/admin.py",
    # conversation app
    "conversation/__init__.py",
    "conversation/apps.py",
    "conversation/models.py",
    "conversation/views.py",
    "conversation/forms.py",
    "conversation/urls.py",
    "conversation/migrations/__init__.py",
    "conversation/migrations/0001_initial.py",
    # users
    "users/models.py",
    "users/views.py",
    "users/forms.py",
    "users/urls.py",
    # core
    "core/settings.py",
    "core/urls.py",
    # templates — conversation
    "templates/conversation/inbox.html",
    "templates/conversation/detail.html",
    "templates/conversation/new.html",
    # templates — market
    "templates/market/wishlist.html",
    "templates/market/try_on.html",
    "templates/market/partials/ar_overlay.html",
    # templates — users
    "templates/users/seller_profile.html",
    "templates/users/edit_profile.html",
]

for f in REQUIRED_FILES:
    file_exists(f)

# ─────────────────────────────────────────────────────────────────────────────
# 2. MARKET MODELS
# ─────────────────────────────────────────────────────────────────────────────
section("2. market/models.py — New Fields & Wishlist")

contains("market/models.py",
    "product_type",
    "PRODUCT_TYPE_CHOICES",
    label="Item.product_type field")

contains("market/models.py",
    "gender",
    "GENDER_CHOICES",
    label="Item.gender field")

contains("market/models.py",
    "size",
    "SIZE_CHOICES",
    label="Item.size field")

contains("market/models.py",
    "brand",
    label="Item.brand field")

contains("market/models.py",
    "color",
    label="Item.color field")

contains("market/models.py",
    "barcode",
    label="Item.barcode field")

contains("market/models.py",
    "class Wishlist",
    "unique_together",
    label="Wishlist model")

# ─────────────────────────────────────────────────────────────────────────────
# 3. MARKET VIEWS
# ─────────────────────────────────────────────────────────────────────────────
section("3. market/views.py — Feature Views")

contains("market/views.py",
    "toggle_wishlist",
    label="toggle_wishlist view")

contains("market/views.py",
    "def wishlist",
    label="wishlist list view")

contains("market/views.py",
    "def try_on",
    label="try_on view")

contains("market/views.py",
    "api_lookup_by_barcode",
    label="api_lookup_by_barcode view")

contains("market/views.py",
    "wishlisted_ids",
    label="browse() passes wishlisted_ids to template")

contains("market/views.py",
    "sort",
    "price_asc",
    label="browse() sorting logic")

contains("market/views.py",
    "Paginator",
    label="browse() pagination")

contains("market/views.py",
    "seller_star_str",
    label="index() attaches seller ratings")

contains("market/views.py",
    "rembg",
    label="new() rembg background removal (optional)")

# ─────────────────────────────────────────────────────────────────────────────
# 4. MARKET FORMS
# ─────────────────────────────────────────────────────────────────────────────
section("4. market/forms.py — New Fields")

contains("market/forms.py",
    "product_type",
    "gender",
    "size",
    "brand",
    "color",
    label="NewItemForm includes all new fields")

contains("market/forms.py",
    "barcode",
    label="NewItemForm includes barcode field")

# ─────────────────────────────────────────────────────────────────────────────
# 5. MARKET URLS
# ─────────────────────────────────────────────────────────────────────────────
section("5. market/urls.py — New Routes")

contains("market/urls.py",
    "toggle_wishlist",
    "name='toggle_wishlist'",
    label="wishlist toggle URL")

contains("market/urls.py",
    "wishlist",
    "name='wishlist'",
    label="wishlist page URL")

contains("market/urls.py",
    "try_on",
    "name='try_on'",
    label="try-on URL")

contains("market/urls.py",
    "api_lookup_by_barcode",
    label="barcode lookup API URL")

# ─────────────────────────────────────────────────────────────────────────────
# 6. MARKET SERIALIZERS
# ─────────────────────────────────────────────────────────────────────────────
section("6. market/serializers.py — Extended Fields")

contains("market/serializers.py",
    "product_type",
    "barcode",
    "brand",
    label="ItemSerializer includes new fields")

# ─────────────────────────────────────────────────────────────────────────────
# 7. CONVERSATION APP
# ─────────────────────────────────────────────────────────────────────────────
section("7. conversation/ — Full App")

contains("conversation/models.py",
    "class Conversation",
    "class Message",
    label="Conversation & Message models")

contains("conversation/views.py",
    "def inbox",
    "def conversation_detail",
    "def new_conversation",
    label="All conversation views present")

contains("conversation/urls.py",
    "app_name = 'conversation'",
    "inbox",
    "detail",
    label="conversation URL patterns")

contains("conversation/migrations/0001_initial.py",
    "Conversation",
    "Message",
    label="conversation initial migration")

# ─────────────────────────────────────────────────────────────────────────────
# 8. USERS — PROFILE & REVIEW
# ─────────────────────────────────────────────────────────────────────────────
section("8. users/ — Profile & Review System")

contains("users/models.py",
    "class Profile",
    label="Profile model")

contains("users/models.py",
    "class Review",
    "reviews_received",
    label="Review model")

contains("users/views.py",
    "def edit_profile",
    label="edit_profile view")

contains("users/views.py",
    "def seller_profile",
    label="seller_profile view")

contains("users/views.py",
    "def leave_review",
    label="leave_review view")

contains("users/forms.py",
    "class ProfileForm",
    label="ProfileForm")

contains("users/forms.py",
    "class ReviewForm",
    label="ReviewForm")

contains("users/urls.py",
    "seller_profile",
    "leave_review",
    "edit_profile",
    label="users URL patterns complete")

# ─────────────────────────────────────────────────────────────────────────────
# 9. CORE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
section("9. Core Config")

contains("core/settings.py",
    '"conversation"',
    label="'conversation' in INSTALLED_APPS")

contains("core/urls.py",
    "conversation.urls",
    "inbox/",
    label="conversation URLs included in core/urls.py")

not_contains("core/settings.py",
    '# "conversation"',
    label="conversation not commented out in INSTALLED_APPS")

# ─────────────────────────────────────────────────────────────────────────────
# 10. MIGRATIONS
# ─────────────────────────────────────────────────────────────────────────────
section("10. Migrations")

# Check market migration exists (any file with wishlist)
market_migs = []
mig_dir = "market/migrations"
if os.path.isdir(mig_dir):
    for fname in os.listdir(mig_dir):
        if fname.endswith(".py") and fname != "__init__.py":
            fpath = os.path.join(mig_dir, fname)
            with open(fpath, encoding="utf-8", errors="ignore") as f:
                content = f.read()
            if "Wishlist" in content:
                market_migs.append(fname)

if market_migs:
    ok(f"Market Wishlist migration found: {', '.join(market_migs)}")
else:
    fail("No market migration contains 'Wishlist'",
         "Run: python manage.py makemigrations market")

# Check users migration for Review
user_migs = []
user_mig_dir = "users/migrations"
if os.path.isdir(user_mig_dir):
    for fname in os.listdir(user_mig_dir):
        if fname.endswith(".py") and fname != "__init__.py":
            fpath = os.path.join(user_mig_dir, fname)
            with open(fpath, encoding="utf-8", errors="ignore") as f:
                content = f.read()
            if "Review" in content:
                user_migs.append(fname)

if user_migs:
    ok(f"Users Review migration found: {', '.join(user_migs)}")
else:
    fail("No users migration contains 'Review'",
         "Run: python manage.py makemigrations users")

# Check conversation migration
if file_exists("conversation/migrations/0001_initial.py"):
    contains("conversation/migrations/0001_initial.py",
        "Conversation", "Message",
        label="conversation migration has both models")

# ─────────────────────────────────────────────────────────────────────────────
# 11. TEMPLATE CONTENT SPOT-CHECKS
# ─────────────────────────────────────────────────────────────────────────────
section("11. Template Content Spot-checks")

contains("templates/conversation/inbox.html",
    "conversation:detail",
    label="inbox.html links to conversation detail")

contains("templates/conversation/detail.html",
    "conversation:inbox",
    label="detail.html has back-to-inbox link")

contains("templates/conversation/detail.html",
    "messages",
    label="detail.html renders message thread")

contains("templates/market/wishlist.html",
    "toggle_wishlist",
    label="wishlist.html has remove link")

contains("templates/market/try_on.html",
    "@mediapipe/pose",
    "poseLandmarks",
    label="try_on.html uses MediaPipe pose")

contains("templates/users/seller_profile.html",
    "leave_review",
    "avg_rating",
    label="seller_profile.html has review form + rating display")

contains("templates/market/partials/ar_overlay.html",
    "holo-pop",
    "try_on",
    label="ar_overlay partial has try-on link")

# ─────────────────────────────────────────────────────────────────────────────
# 12. DETAIL.HTML — OPTIONAL FEATURE CHECK
# ─────────────────────────────────────────────────────────────────────────────
section("12. templates/market/detail.html — Action Block (manual patch)")

detail_path = "templates/market/detail.html"
if os.path.isfile(detail_path):
    with open(detail_path, encoding="utf-8", errors="ignore") as f:
        detail = f.read()

    checks = {
        "toggle_wishlist URL": "toggle_wishlist",
        "conversation:new (Message Seller button)": "conversation:new",
        "market:try_on (AR Try-On button)": "market:try_on",
        "users:seller_profile (seller link)": "users:seller_profile",
    }
    for label, needle in checks.items():
        if needle in detail:
            ok(f"detail.html — {label}")
        else:
            warn(f"detail.html — {label} NOT found",
                 "Manually add from templates/market/detail_action_block.html")
else:
    warn("templates/market/detail.html not found",
         "Make sure this file exists in your project")

# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
total = passed + failed + warnings
print(f"\n{BOLD}{'═'*55}{RESET}")
print(f"{BOLD}  RESULTS{RESET}")
print(f"{'═'*55}")
print(f"  {GREEN}Passed  : {passed}{RESET}")
print(f"  {RED}Failed  : {failed}{RESET}")
print(f"  {YELLOW}Warnings: {warnings}{RESET}")
print(f"  Total   : {total}")
print(f"{'═'*55}\n")

if failed == 0 and warnings == 0:
    print(f"{GREEN}{BOLD}  🎉 All checks passed! Your patch is complete.{RESET}\n")
elif failed == 0:
    print(f"{YELLOW}{BOLD}  ⚠  Passed with warnings. Review items above.{RESET}\n")
else:
    print(f"{RED}{BOLD}  ✗  {failed} check(s) failed. See details above.{RESET}\n")
    print(f"  Tip: Run  {CYAN}python manage.py check{RESET}  after fixing to validate Django config.\n")

sys.exit(0 if failed == 0 else 1)
