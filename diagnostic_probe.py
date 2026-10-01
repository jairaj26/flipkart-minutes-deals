import os
import sys
import json
import re
import urllib.parse
import urllib.request
import ssl

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from bot.scraper import FlipkartScraper, build_product_link, sanitize_page_uri
from bot import config

def run_diagnostic():
    pincode = os.getenv("PINCODE", config.DEFAULT_PINCODE)
    scraper = FlipkartScraper(pincode=pincode)

    print("=" * 70)
    print("🔬 FLIPKART MINUTES CATEGORY SORT & RESPONSE DIAGNOSTIC PROBE")
    print(f"📍 Pincode: {scraper.pincode}")
    cookie_str = config.FLIPKART_COOKIE or ""
    print(f"🍪 Cookie: {'CONFIGURED (' + str(len(cookie_str)) + ' chars)' if cookie_str else 'NONE (Anonymous)'}")
    print("=" * 70)

    categories_to_probe = [
        ("Namkeens", "/hyperlocal/hloc/1002/pr?sid=hloc%2F0010%2F1002&marketplace=HYPERLOCAL"),
        ("Indian Snacks", "/hyperlocal/hloc/qeby/pr?sid=hloc%2F0010%2Fqeby&marketplace=HYPERLOCAL"),
        ("Chips", "/hyperlocal/hloc/1001/pr?sid=hloc%2F0010%2F1001&marketplace=HYPERLOCAL"),
        ("Popcorn", "/hyperlocal/hloc/1005/pr?sid=hloc%2F0010%2F1005&marketplace=HYPERLOCAL"),
        ("Chips, Crisps & Namkeen Hub", "/hyperlocal/Chips-Namkeen/pr?sid=hloc%2F0010&marketplace=HYPERLOCAL")
    ]

    target_keywords = ["delish", "shakkar", "namak para", "4700", "popcorn"]
    target_pids = ["SNSHJGQB4U7NRZJ7", "SNSHJGQBBE3FVPSP"]

    for cat_name, base_uri in categories_to_probe:
        print("\n" + "#" * 70)
        print(f"📁 PROBING CATEGORY: [{cat_name}]")
        print(f"   Base URI: {base_uri}")
        print("#" * 70)

        # -------------------------------------------------------------
        # 1. Fetch WITH sort=discount
        # -------------------------------------------------------------
        uri_sorted = base_uri + ("&" if "?" in base_uri else "?") + "sort=discount"
        json_sorted = scraper.fetch_rome_page(uri_sorted)
        prods_sorted = scraper.parse_products_from_json(json_sorted) if json_sorted else []

        print(f"\n[A] WITH sort=discount:")
        print(f"    Raw slots count: {len(json_sorted.get('RESPONSE', {}).get('slots', [])) if json_sorted else 0}")
        print(f"    Total parsed items: {len(prods_sorted)}")

        if prods_sorted:
            discs = [p['discount'] for p in prods_sorted]
            is_descending = all(discs[i] >= discs[i+1] for i in range(len(discs)-1))
            print(f"    Discount sequence: {discs}")
            print(f"    👉 IS SORTED BY DISCOUNT? {'✅ YES (Descending)' if is_descending else '❌ NO (Unsorted / Curated)'}")

            print("\n    Delivered items order (Page 1):")
            for idx, p in enumerate(prods_sorted):
                is_hit = any(k in p['title'].lower() for k in target_keywords) or any(pid in p['link'] for pid in target_pids)
                flag = "🎯 TARGET --> " if is_hit else "   "
                oos_str = " [OUT OF STOCK]" if p['oos'] else " [IN STOCK]"
                print(f"    {flag}[{idx+1:02d}] [{p['discount']}% OFF] {p['title']} - ₹{p['fsp']} (MRP: ₹{p['mrp']}){oos_str}")
        else:
            print("    ⚠️ 0 items parsed.")

        # -------------------------------------------------------------
        # 2. Fetch WITHOUT sort=discount (Default Sort)
        # -------------------------------------------------------------
        json_default = scraper.fetch_rome_page(base_uri)
        prods_default = scraper.parse_products_from_json(json_default) if json_default else []

        print(f"\n[B] WITHOUT sort=discount (Default Ranking):")
        print(f"    Total parsed items: {len(prods_default)}")
        if prods_default:
            discs_def = [p['discount'] for p in prods_default]
            print(f"    Default discount sequence: {discs_def[:10]}")
            # Compare if sorted vs default order are identical
            if prods_sorted and len(prods_sorted) == len(prods_default):
                same_order = [p['id'] for p in prods_sorted] == [p['id'] for p in prods_default]
                if same_order:
                    print("    ⚠️ ALERT: The item order with sort=discount is IDENTICAL to default sort!")
                    print("    👉 This proves Flipkart Minutes IGNORES the 'sort=discount' parameter for this endpoint!")
                else:
                    print("    ✅ sort=discount produced a DIFFERENT item ordering than default.")

        # -------------------------------------------------------------
        # 3. Test Page 2 with sort=discount
        # -------------------------------------------------------------
        uri_page2 = uri_sorted + "&page=2"
        json_p2 = scraper.fetch_rome_page(uri_page2)
        prods_p2 = scraper.parse_products_from_json(json_p2) if json_p2 else []
        print(f"\n[C] Page 2 (sort=discount&page=2):")
        print(f"    Items returned: {len(prods_p2)}")
        if prods_p2:
            p2_discs = [p['discount'] for p in prods_p2]
            print(f"    Page 2 discount sequence: {p2_discs[:10]}")
            for idx, p in enumerate(prods_p2[:10]):
                is_hit = any(k in p['title'].lower() for k in target_keywords) or any(pid in p['link'] for pid in target_pids)
                flag = "🎯 TARGET --> " if is_hit else "   "
                print(f"    {flag}[P2 #{idx+1:02d}] [{p['discount']}% OFF] {p['title']} - ₹{p['fsp']} (MRP: ₹{p['mrp']})")

    # -------------------------------------------------------------
    # 4. Direct Search Probe for Delish items
    # -------------------------------------------------------------
    print("\n" + "=" * 70)
    print("🔎 DIRECT SEARCH PROBE FOR TARGET ITEMS")
    print("=" * 70)

    search_queries = ["Delish", "Shakkar Para", "Namak Para"]
    for q in search_queries:
        s_uri = f"/hyperlocal/pr?q={urllib.parse.quote(q)}&marketplace=HYPERLOCAL&sort=discount"
        s_json = scraper.fetch_rome_page(s_uri)
        s_prods = scraper.parse_products_from_json(s_json) if s_json else []
        print(f"\n🔍 Search Query: '{q}' (sort=discount)")
        print(f"   Items found: {len(s_prods)}")
        for idx, p in enumerate(s_prods[:10]):
            is_hit = any(k in p['title'].lower() for k in target_keywords) or any(pid in p['link'] for pid in target_pids)
            flag = "🎯 TARGET --> " if is_hit else "   "
            print(f"   {flag}[{idx+1:02d}] [{p['discount']}% OFF] {p['title']} - ₹{p['fsp']} (MRP: ₹{p['mrp']}) | link: {p['link']}")

if __name__ == "__main__":
    run_diagnostic()
