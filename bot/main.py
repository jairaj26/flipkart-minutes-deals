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

# 7-day cooldown for unchanging prices (items with same price alert at most once a week)
SEVEN_DAYS_SECONDS = 7 * 24 * 3600

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
    """Saves posted deals to cache, pruning records older than 30 days."""
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    now = time.time()
    retention_period = 30 * 24 * 3600  # 30 days retention

    pruned = {}
    for key, record in cache.items():
        ts = record.get("timestamp", 0)
        if now - ts < retention_period:
            pruned[key] = record

    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(pruned, f, indent=2, ensure_ascii=False)

def should_post_deal(deal, cache):
    """
    Weekly Deduplication Rules:
    1. If never posted before -> Post it.
    2. If posted before:
       - If selling price dropped further (fsp < cached_fsp) -> Post immediately (price drop).
       - If price is the same or higher:
         * Check if 7 days (1 week) have passed since last post.
         * If >= 7 days -> Post once for the new week.
         * Otherwise -> Suppress (shows only once a week for items with unchanging prices).
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

    # 2. Same or higher price -> check if 7 days (1 week) have passed
    now = time.time()
    last_posted = cached.get("timestamp", 0)
    if (now - last_posted) >= SEVEN_DAYS_SECONDS:
        return True

    # Suppress repeat alert within the 7-day window
    return False

def scan_worker(category_info, pincode):
    """Worker function to scrape Page 1 of a single category."""
    scraper = FlipkartScraper(pincode=pincode)
    return scraper.fetch_category_deals(category_info)

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
    print(f"[*] Starting concurrent scan across {len(categories)} categories & subcategories (Page 1 sorted by discount)...")

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
        future_to_cat = {executor.submit(scan_worker, cat, args.pincode): cat for cat in categories}
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
                            future_to_cat[executor.submit(scan_worker, sub_copy, args.pincode)] = sub_copy
                            print(f"    ↳ Discovered subcategory: [{sub_copy['name']}]")
                except Exception as e:
                    print(f"  ✗ [{cat['name']}] Failed: {e}")

    elapsed_scan = time.time() - start_time
    print(f"[*] Scan complete in {elapsed_scan:.1f}s. Total unique items scraped: {len(all_products)}")

    # Filter deals
    qualifying_deals = [
        p for p in all_products
        if p["discount"] >= args.min_discount and not p["oos"]
    ]
    # Sort highest discount first
    qualifying_deals.sort(key=lambda x: x["discount"], reverse=True)

    print(f"[*] Found {len(qualifying_deals)} deals matching criteria (>= {args.min_discount}% OFF & In Stock)")

    # Load cache for deduplication
    cache = load_cache(args.cache)
    notifier = TelegramNotifier()

    new_alerts_sent = 0
    suppressed_count = 0
    now = time.time()

    for deal in qualifying_deals:
        key = get_deal_key(deal)
        if should_post_deal(deal, cache):
            print(f"  🔥 NEW DEAL: [{deal['discount']}% OFF] {deal['title']} - ₹{deal['fsp']} (MRP: ₹{deal['mrp']}) [Key: {key}]")
            if not args.dry_run:
                success = notifier.send_deal(deal)
                if success:
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
            else:
                new_alerts_sent += 1
        else:
            suppressed_count += 1

    if suppressed_count > 0:
        print(f"[*] Suppressed {suppressed_count} deals already alerted within the past 7 days at same price.")

    if not args.dry_run:
        save_cache(cache, args.cache)
        print(f"[*] Updated deduplication cache ({len(cache)} total active records).")

    total_time = time.time() - start_time
    print("-" * 60)
    print(f"✅ Completed run in {total_time:.1f}s. Sent {new_alerts_sent} new deal alerts.")
    print("=" * 60)

if __name__ == "__main__":
    main()
