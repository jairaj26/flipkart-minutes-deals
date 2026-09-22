import argparse
import concurrent.futures
from datetime import datetime, timezone
import json
import os
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
    """Saves posted deals to cache, pruning records older than 7 days."""
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    now = time.time()
    seven_days = 7 * 24 * 3600

    pruned = {}
    for uid, record in cache.items():
        ts = record.get("timestamp", 0)
        if now - ts < seven_days:
            pruned[uid] = record

    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(pruned, f, indent=2, ensure_ascii=False)

def should_post_deal(deal, cache):
    """
    Deduplication rules:
    - If not in cache -> Post.
    - If in cache, only re-post if selling price dropped further (fsp < cached_fsp)
      OR if last posted more than 36 hours ago.
    """
    uid = deal["id"]
    if uid not in cache:
        return True

    cached = cache[uid]
    cached_fsp = cached.get("fsp", float("inf"))
    if deal["fsp"] < cached_fsp:
        return True

    now = time.time()
    last_posted = cached.get("timestamp", 0)
    if (now - last_posted) > (36 * 3600):
        return True

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
    print("=" * 60)
    print("⚡ Flipkart Minutes Deals Finder - Hourly Run")
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
    print(f"[*] Starting concurrent scan across {len(categories)} leaf categories (Page 1 sorted by discount)...")

    all_products = []
    seen_ids = set()

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        future_to_cat = {executor.submit(scan_worker, cat, args.pincode): cat for cat in categories}
        for future in concurrent.futures.as_completed(future_to_cat):
            cat = future_to_cat[future]
            try:
                prods = future.result()
                unique_added = 0
                for p in prods:
                    if p["id"] not in seen_ids:
                        seen_ids.add(p["id"])
                        all_products.append(p)
                        unique_added += 1
                print(f"  ✓ [{cat['name']}] Found {len(prods)} items ({unique_added} new)")
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
    now = time.time()

    for deal in qualifying_deals:
        if should_post_deal(deal, cache):
            print(f"  🔥 NEW DEAL: [{deal['discount']}% OFF] {deal['title']} - ₹{deal['fsp']} (MRP: ₹{deal['mrp']})")
            if not args.dry_run:
                success = notifier.send_deal(deal)
                if success:
                    cache[deal["id"]] = {
                        "fsp": deal["fsp"],
                        "mrp": deal["mrp"],
                        "discount": deal["discount"],
                        "timestamp": now,
                        "date": datetime.now(timezone.utc).isoformat()
                    }
                    new_alerts_sent += 1
            else:
                new_alerts_sent += 1

    if not args.dry_run:
        save_cache(cache, args.cache)
        print(f"[*] Updated deduplication cache ({len(cache)} total active records).")

    total_time = time.time() - start_time
    print("-" * 60)
    print(f"✅ Completed run in {total_time:.1f}s. Sent {new_alerts_sent} new deal alerts.")
    print("=" * 60)

if __name__ == "__main__":
    main()
