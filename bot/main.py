import argparse
import concurrent.futures
from datetime import datetime, timezone, timedelta
import json
import os
import re
import sys
import time

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from . import config
from .scraper import FlipkartScraper
from .telegram import TelegramNotifier

# Indian Standard Time (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))

# 30-day cooldown for unchanging prices (items with unchanging price alert at most once a month, never twice in same day)
COOLDOWN_SECONDS = 30 * 24 * 3600

def get_deal_key(deal):
    """
    Derives a stable unique product identifier.
    Extracts 'pid' (Product ID) from product URL if present; otherwise falls back to normalized title.
    """
    lnk = deal.get("link", "")
    m = re.search(r"[?&]pid=([a-zA-Z0-9]+)", lnk)
    if m:
        return m.group(1).upper()
    title = deal.get("title", "")
    norm = re.sub(r"[^a-zA-Z0-9]", "", title.lower())
    return norm or deal.get("id", "")

def load_cache(cache_path):
    """Loads previously posted deals from cache."""
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_cache(cache, cache_path):
    """Saves posted deals to cache, pruning records older than 60 days."""
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    now = time.time()
    retention_period = 60 * 24 * 3600  # 60 days retention to preserve 30-day cooldown history

    pruned = {}
    for key, record in cache.items():
        ts = record.get("timestamp", 0)
        if now - ts < retention_period:
            pruned[key] = record

    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(pruned, f, indent=2, ensure_ascii=False)

def should_post_deal(deal, cache):
    """
    30-Day Deduplication & Alert Frequency Rules:
    1. If never posted before -> Post it.
    2. If posted before:
       - If selling price dropped further (fsp < cached_fsp) -> Post immediately (price drop alert).
       - If price is the same or higher:
         * Check if 30 days have passed since last post.
         * If >= 30 days -> Post once for the new month.
         * Otherwise -> Suppress (prevents repeat alerts on the same day and for the next 30 days).
    """
    key = get_deal_key(deal)
    # Check by stable key or legacy deal id
    cached = cache.get(key) or cache.get(deal.get("id"))
    if not cached:
        return True

    cached_fsp = cached.get("fsp", float("inf"))

    # 1. Price dropped further -> alert immediately
    if deal["fsp"] < cached_fsp:
        return True

    # 2. Same or higher price -> check if 30 days have passed
    now = time.time()
    last_posted = cached.get("timestamp", 0)
    if (now - last_posted) >= COOLDOWN_SECONDS:
        return True

    # Suppress repeat alert within the 30-day window (and same day)
    return False

def is_deal_blacklisted(deal):
    """
    Checks if a deal should be filtered out based on:
    - Excluded negative keywords (mobile covers, rakhi, pooja items, pet food)
    - Excluded brands (rakhi, puja, phone case, and pet food brands)
    - Religious brand pattern ('reli...' brands, e.g. 'Religious Ganesha Rakhi', except genuine words like 'relish')
    """
    title = deal.get("title", "").strip().lower()

    # 1. Excluded negative keywords
    for kw in config.EXCLUDED_KEYWORDS:
        if kw in title:
            return True

    # 2. Religious brand / keyword pattern (starts with reli... except relish)
    for word in re.findall(r"\b[a-z]+", title):
        if word.startswith("reli") and not word.startswith("relish"):
            return True

    # 3. Excluded brands
    for eb in config.EXCLUDED_BRANDS:
        eb_lower = eb.lower()
        if title.startswith(eb_lower + " ") or f" by {eb_lower}" in title or title == eb_lower or f" {eb_lower} " in title:
            return True

    return False

def get_effective_min_discount(deal, category_name=None, default_min=None):
    """
    Computes the minimum discount percentage required for a deal to qualify.
    Evaluates rules in hierarchical priority:
    1. Title keyword override (config.KEYWORD_THRESHOLDS)
    2. Brand override (config.BRAND_THRESHOLDS)
    3. Category override (config.CATEGORY_THRESHOLDS)
    4. Global default (config.DEFAULT_MIN_DISCOUNT, default: 65%)
    """
    title = deal.get("title", "").strip().lower()
    cat = (category_name or deal.get("category", "")).strip()

    # Priority 1: Keyword thresholds in title
    for kw, thresh in config.KEYWORD_THRESHOLDS:
        if kw.lower() in title:
            return thresh

    # Priority 2: Brand thresholds
    for b_name, thresh in config.BRAND_THRESHOLDS.items():
        b_lower = b_name.lower()
        if title.startswith(b_lower + " ") or f" by {b_lower}" in title or title == b_lower or f" {b_lower} " in title:
            return thresh

    # Priority 3: Category thresholds
    if cat:
        if cat in config.CATEGORY_THRESHOLDS:
            return config.CATEGORY_THRESHOLDS[cat]
        cat_lower = cat.lower()
        for c_key, thresh in config.CATEGORY_THRESHOLDS.items():
            if c_key.lower() == cat_lower or c_key.lower() in cat_lower:
                return thresh

    # Priority 4: Fallback to CLI argument or config default
    return default_min if default_min is not None else config.DEFAULT_MIN_DISCOUNT

def scan_worker(category_info, pincode, min_discount=None):
    """Worker function to scrape deals for a single category with smart multi-page pagination."""
    scraper = FlipkartScraper(pincode=pincode)
    cat_name = category_info.get("name", "")
    cat_thresh = config.CATEGORY_THRESHOLDS.get(cat_name)
    scan_min = cat_thresh if cat_thresh is not None else (min_discount if min_discount is not None else config.DEFAULT_MIN_DISCOUNT)
    return scraper.fetch_category_deals(category_info, min_discount=scan_min, max_pages=3)

def main():
    parser = argparse.ArgumentParser(description="Flipkart Minutes Deals Scraper & Telegram Bot")
    parser.add_argument("--dry-run", action="store_true", default=config.DRY_RUN, help="Print deals without posting to Telegram")
    parser.add_argument("--pincode", default=config.DEFAULT_PINCODE, help="Target delivery pincode (default: 560045)")
    parser.add_argument("--min-discount", type=int, default=config.MIN_DISCOUNT, help="Minimum discount percentage threshold")
    parser.add_argument("--workers", type=int, default=config.MAX_WORKERS, help="Number of concurrent worker threads")
    parser.add_argument("--cache", default=config.CACHE_FILE, help="Path to cache JSON file")
    args = parser.parse_args()

    start_time = time.time()
    ist_now = datetime.now(IST)
    print("=" * 60)
    print("⚡ Flipkart Minutes Deals Finder - Hourly Run")
    print(f"⏰ Current IST Time: {ist_now.strftime('%Y-%m-%d %H:%M:%S')} IST")
    print(f"📍 Target Pincode: {args.pincode}")
    print(f"🔥 Min Discount: {args.min_discount}%")
    print(f"⚙️ Workers: {args.workers}")
    print(f"🛡️ Dry Run: {'YES (Alerts disabled)' if args.dry_run else 'NO (Live Telegram posting)'}")

    # Inspect Cookie configuration
    cookie_str = config.FLIPKART_COOKIE or ""
    has_sn = "SN=" in cookie_str or "; SN=" in cookie_str
    has_at = "at=" in cookie_str or "; at=" in cookie_str
    has_s = "S=" in cookie_str or "; S=" in cookie_str

    if cookie_str:
        print(f"🍪 Cookie: Configured ({len(cookie_str)} chars) [SN: {'✓' if has_sn else '✗'}, at: {'✓' if has_at else '✗'}, S: {'✓' if has_s else '✗'}]")
        if not (has_sn and has_at):
            print("  ⚠️ WARNING: 'SN' or 'at' tokens are missing from FLIPKART_COOKIE!")
            print("  ⚠️ If you copied from `document.cookie` in console, HttpOnly security tokens were excluded.")
            print("  ⚠️ Please copy the Cookie directly from DevTools -> Network tab -> Request Headers -> Cookie.")
    else:
        print("🍪 Cookie: None provided (Running anonymous guest session)")
    print("=" * 60)

    categories = config.CATEGORIES
    print(f"[*] Starting concurrent scan across {len(categories)} categories & subcategories (Smart Multi-Page sorted by discount)...")

    all_products = []
    seen_ids = set()

    def normalize_cat_uri(u):
        if not u:
            return ""
        # Remove sort parameter and protocol for dedup check
        u = re.sub(r"^https?://[^/]+", "", u)
        u = re.sub(r"[?&]sort=[^&]+", "", u)
        return u.strip().rstrip("?")

    visited_uris = {normalize_cat_uri(c["uri"]) for c in categories}

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        future_to_cat = {executor.submit(scan_worker, cat, args.pincode, args.min_discount): cat for cat in categories}
        while future_to_cat:
            done, _ = concurrent.futures.wait(future_to_cat, return_when=concurrent.futures.FIRST_COMPLETED)
            for future in done:
                cat = future_to_cat.pop(future)
                try:
                    prods, discovered_subcats = future.result()
                    unique_added = 0
                    for p in prods:
                        if p["id"] not in seen_ids:
                            seen_ids.add(p["id"])
                            all_products.append(p)
                            unique_added += 1
                    print(f"  ✓ [{cat['name']}] Found {len(prods)} items ({unique_added} new)")

                    # Dynamically queue any unvisited subcategories discovered from side-rail navigation
                    for sub in discovered_subcats:
                        norm_sub = normalize_cat_uri(sub.get("uri", ""))
                        if norm_sub and norm_sub not in visited_uris:
                            visited_uris.add(norm_sub)
                            sub_uri = sub["uri"]
                            if "sort=discount" not in sub_uri:
                                sub_uri += ("&" if "?" in sub_uri else "?") + "sort=discount"
                            sub_copy = {"name": sub["name"], "uri": sub_uri}
                            future_to_cat[executor.submit(scan_worker, sub_copy, args.pincode, args.min_discount)] = sub_copy
                            print(f"    ↳ Discovered subcategory: [{sub_copy['name']}]")
                except Exception as e:
                    print(f"  ✗ [{cat['name']}] Failed: {e}")

    elapsed_scan = time.time() - start_time
    print(f"[*] Scan complete in {elapsed_scan:.1f}s. Total unique items scraped: {len(all_products)}")

    # Filter deals with negative filters and hierarchical threshold engine
    qualifying_deals = []
    dropped_blacklisted = 0
    dropped_threshold = 0
    dropped_oos = 0

    for p in all_products:
        if is_deal_blacklisted(p):
            dropped_blacklisted += 1
            continue
        if p.get("oos"):
            dropped_oos += 1
            continue
        effective_threshold = get_effective_min_discount(p, p.get("category"), default_min=args.min_discount)
        if p.get("discount", 0) >= effective_threshold:
            p["effective_threshold"] = effective_threshold
            qualifying_deals.append(p)
        else:
            dropped_threshold += 1

    # Sort highest discount first
    qualifying_deals.sort(key=lambda x: x["discount"], reverse=True)

    print(f"[*] Filtering summary: {len(qualifying_deals)} qualified deals (Excluded: {dropped_blacklisted} blacklisted/junk, {dropped_oos} OOS, {dropped_threshold} below threshold)")

    # Load cache for deduplication
    cache = load_cache(args.cache)
    notifier = TelegramNotifier()

    new_alerts_sent = 0
    suppressed_count = 0
    now = time.time()

    deals_to_post = []
    for deal in qualifying_deals:
        key = get_deal_key(deal)
        thresh = deal.get("effective_threshold", args.min_discount)
        if should_post_deal(deal, cache):
            print(f"  🔥 QUALIFIED DEAL: [{deal['discount']}% OFF] {deal['title']} - ₹{deal['fsp']} (MRP: ₹{deal['mrp']}) [Req: >={thresh}%] [Key: {key}]")
            deals_to_post.append(deal)
        else:
            suppressed_count += 1

    if deals_to_post:
        if not args.dry_run:
            posted_deals = notifier.send_combined_deals(deals_to_post)
            for deal in posted_deals:
                key = get_deal_key(deal)
                cache[key] = {
                    "key": key,
                    "title": deal["title"],
                    "fsp": deal["fsp"],
                    "mrp": deal["mrp"],
                    "discount": deal["discount"],
                    "link": deal["link"],
                    "timestamp": now,
                    "date": datetime.now(timezone.utc).isoformat()
                }
                new_alerts_sent += 1
            print(f"[*] Posted {len(posted_deals)} deals in combined message(s) to Telegram.")
        else:
            new_alerts_sent = len(deals_to_post)
            print(f"[*] Dry run: {len(deals_to_post)} deals ready to post in combined message.")
    else:
        print("[*] No new qualifying deals to post this run.")

    if suppressed_count > 0:
        print(f"[*] Suppressed {suppressed_count} deals already alerted within the past 30 days (or earlier today) with unchanging price.")

    if not args.dry_run:
        save_cache(cache, args.cache)
        print(f"[*] Updated deduplication cache ({len(cache)} total active records).")

    total_time = time.time() - start_time
    print("-" * 60)
    print(f"✅ Completed run in {total_time:.1f}s. Sent {new_alerts_sent} new deal alerts.")
    print("=" * 60)

if __name__ == "__main__":
    main()
