import os

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

# Deal Filters & Settings
DEFAULT_PINCODE = os.getenv("PINCODE", "560045").strip()
FLIPKART_COOKIE = os.getenv("FLIPKART_COOKIE", "").strip()
MIN_DISCOUNT = int(os.getenv("MIN_DISCOUNT", "70"))
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "5"))
CACHE_FILE = os.getenv("CACHE_FILE", os.path.join("data", "posted_deals.json"))
DRY_RUN = os.getenv("DRY_RUN", "false").lower() in ("true", "1", "yes")

# HTTP & API Headers
ROME_API_URL = "https://1.rome.api.flipkart.com/api/4/page/fetch?cacheFirst=false"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
X_USER_AGENT = "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Edg/153.0.0.0 Mobile Safari/537.36 FKUA/msite/0.0.4/msite/Mobile"

DEFAULT_HEADERS = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "flipkart_secure": "true",
    "user-agent": USER_AGENT,
    "x-user-agent": X_USER_AGENT,
    "origin": "https://www.flipkart.com",
    "referer": "https://www.flipkart.com/"
}

# Verified Leaf & Department Subcategories (Groceries, snacks, staples, beverages & essentials only; zero clutter)
CATEGORIES = [
    # ---------------------------------------------------------
    # 1. Bakery, Breads & Biscuits
    # ---------------------------------------------------------
    { "name": "Biscuits & Cookies", "uri": "/hyperlocal/hloc/0613/pr?sid=hloc%2F0006%2F0613&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Breads & Buns", "uri": "/hyperlocal/hloc/0601/pr?sid=hloc%2F0006%2F0601&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Rusk & Khari", "uri": "/hyperlocal/hloc/0603/pr?sid=hloc%2F0006%2F0603&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Cakes & Muffins", "uri": "/hyperlocal/hloc/0604/pr?sid=hloc%2F0006%2F0604&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Bakery Snacks", "uri": "/hyperlocal/hloc/0602/pr?sid=hloc%2F0006%2F0602&marketplace=HYPERLOCAL&sort=discount" },

    # ---------------------------------------------------------
    # 2. Chips, Crisps & Namkeen
    # ---------------------------------------------------------
    { "name": "Chips", "uri": "/hyperlocal/hloc/1001/pr?sid=hloc%2F0010%2F1001&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Bhujia & Mixture", "uri": "/hyperlocal/hloc/bbvr/pr?sid=hloc%2F0010%2Fbbvr&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Wafers", "uri": "/hyperlocal/hloc/sotw/pr?sid=hloc%2F0010%2Fsotw&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Namkeens", "uri": "/hyperlocal/hloc/1002/pr?sid=hloc%2F0010%2F1002&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Indian Snacks", "uri": "/hyperlocal/hloc/qeby/pr?sid=hloc%2F0010%2Fqeby&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Roasted Nuts", "uri": "/hyperlocal/hloc/1004/pr?sid=hloc%2F0010%2F1004&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Nachos", "uri": "/hyperlocal/hloc/1003/pr?sid=hloc%2F0010%2F1003&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Healthy Snacks", "uri": "/hyperlocal/hloc/rzhh/pr?sid=hloc%2F0010%2Frzhh&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Popcorn", "uri": "/hyperlocal/hloc/1005/pr?sid=hloc%2F0010%2F1005&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Papads & Fryums", "uri": "/hyperlocal/hloc/1006/pr?sid=hloc%2F0010%2F1006&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Premium & Gourmet Snacks", "uri": "/hyperlocal/hloc/nokv/pr?sid=hloc%2F0010%2Fnokv&marketplace=HYPERLOCAL&sort=discount" },

    # ---------------------------------------------------------
    # 3. Chocolates & Candies
    # ---------------------------------------------------------
    { "name": "Chocolates", "uri": "/hyperlocal/hloc/6501/pr?sid=hloc%2F0065%2F6501&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Chocolate Packs", "uri": "/hyperlocal/hloc/gwcg/pr?sid=hloc%2F0065%2Fgwcg&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Protein & Energy Bars", "uri": "/hyperlocal/hloc/6505/pr?sid=hloc%2F0065%2F6505&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Wafers & Waffle", "uri": "/hyperlocal/hloc/6504/pr?sid=hloc%2F0065%2F6504&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Candies & Lollipops", "uri": "/hyperlocal/hloc/6502/pr?sid=hloc%2F0065%2F6502&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Mouth Freshener & Gum", "uri": "/hyperlocal/hloc/6503/pr?sid=hloc%2F0065%2F6503&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Dark Chocolate", "uri": "/hyperlocal/hloc/tczo/pr?sid=hloc%2F0065%2Ftczo&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Milk Chocolate", "uri": "/hyperlocal/hloc/rzod/pr?sid=hloc%2F0065%2Frzod&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Syrups & Spreads", "uri": "/hyperlocal/hloc/ayvh/pr?sid=hloc%2F0065%2Fayvh&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Shared Packs", "uri": "/hyperlocal/hloc/evew/pr?sid=hloc%2F0065%2Fevew&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Fruit & Nut Chocolates", "uri": "/hyperlocal/hloc/skjg/pr?sid=hloc%2F0065%2Fskjg&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Brownies & Muffins", "uri": "/hyperlocal/hloc/flxv/pr?sid=hloc%2F0065%2Fflxv&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Premium & Imported Chocolates", "uri": "/hyperlocal/hloc/ztyr/pr?sid=hloc%2F0065%2Fztyr&marketplace=HYPERLOCAL&sort=discount" },

    # ---------------------------------------------------------
    # 4. Tea, Coffee & Health Drinks
    # ---------------------------------------------------------
    { "name": "Tea", "uri": "/hyperlocal/hloc/1101/pr?sid=hloc%2F0011%2F1101&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Coffee", "uri": "/hyperlocal/hloc/1102/pr?sid=hloc%2F0011%2F1102&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Health & Nutrition Drinks", "uri": "/hyperlocal/hloc/1103/pr?sid=hloc%2F0011%2F1103&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Green & Herbal Tea", "uri": "/hyperlocal/hloc/1104/pr?sid=hloc%2F0011%2F1104&marketplace=HYPERLOCAL&sort=discount" },

    # ---------------------------------------------------------
    # 5. Cold Drinks & Juices
    # ---------------------------------------------------------
    { "name": "Soft Drinks & Soda", "uri": "/hyperlocal/hloc/0701/pr?sid=hloc%2F0007%2F0701&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Fruit Juices", "uri": "/hyperlocal/hloc/0702/pr?sid=hloc%2F0007%2F0702&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Energy & Sports Drinks", "uri": "/hyperlocal/hloc/0703/pr?sid=hloc%2F0007%2F0703&marketplace=HYPERLOCAL&sort=discount" },

    # ---------------------------------------------------------
    # 6. Atta, Rice, Dal & Staples
    # ---------------------------------------------------------
    { "name": "Atta & Flours", "uri": "/hyperlocal/hloc/0301/pr?sid=hloc%2F0003%2F0301&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Rice & Rice Products", "uri": "/hyperlocal/hloc/0302/pr?sid=hloc%2F0003%2F0302&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Dals & Pulses", "uri": "/hyperlocal/hloc/0303/pr?sid=hloc%2F0003%2F0303&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Atta, Rice & Dal Hub", "uri": "/hyperlocal/Atta-Rice-Dal/pr?sid=hloc%2F0003&marketplace=HYPERLOCAL&sort=discount" },

    # ---------------------------------------------------------
    # 7. Oil, Ghee & Masalas
    # ---------------------------------------------------------
    { "name": "Edible Oils", "uri": "/hyperlocal/hloc/0901/pr?sid=hloc%2F0009%2F0901&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Ghee & Vanaspati", "uri": "/hyperlocal/hloc/0902/pr?sid=hloc%2F0009%2F0902&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Spices & Masalas", "uri": "/hyperlocal/hloc/0903/pr?sid=hloc%2F0009%2F0903&marketplace=HYPERLOCAL&sort=discount" },

    # ---------------------------------------------------------
    # 8. Dairy, Bread & Eggs
    # ---------------------------------------------------------
    { "name": "Dairy, Milk & Butter", "uri": "/hyperlocal/hloc/3002/pr?sid=hloc%2F0030%2F3002&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Dairy, Bread & Eggs Hub", "uri": "/hyperlocal/Dairy-Bread-Eggs/pr?sid=hloc%2F0030&marketplace=HYPERLOCAL&sort=discount" },

    # ---------------------------------------------------------
    # 9. Sweets, Mithai & Paan Corner
    # ---------------------------------------------------------
    { "name": "Sweets & Mithai", "uri": "/hyperlocal/hloc/0806/pr?sid=hloc%2F0081%2F0806&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Paan Corner & Refreshments", "uri": "/hyperlocal/hloc/4904/pr?sid=hloc%2F0049%2F4904&marketplace=HYPERLOCAL&sort=discount" },

    # ---------------------------------------------------------
    # 10. Instant & Frozen Food
    # ---------------------------------------------------------
    { "name": "Instant & Frozen Food Hub", "uri": "/hyperlocal/Instant-FrozenFood/pr?sid=hloc%2F0020&marketplace=HYPERLOCAL&sort=discount" },

    # ---------------------------------------------------------
    # 11. Sauces & Spreads
    # ---------------------------------------------------------
    { "name": "Sauces & Spreads Hub", "uri": "/hyperlocal/Sauces-Spreads/pr?sid=hloc%2F0021&marketplace=HYPERLOCAL&sort=discount" },

    # ---------------------------------------------------------
    # 12. Cereals & Dry Fruits
    # ---------------------------------------------------------
    { "name": "Cereals & Dry Fruits Hub", "uri": "/hyperlocal/Cereals-DryFruits/pr?sid=hloc%2F0019&marketplace=HYPERLOCAL&sort=discount" },

    # ---------------------------------------------------------
    # 13. Ice Cream & Desserts
    # ---------------------------------------------------------
    { "name": "Ice Cream & Desserts Hub", "uri": "/hyperlocal/IceCream-Desserts/pr?sid=hloc%2F0034&marketplace=HYPERLOCAL&sort=discount" },

    # ---------------------------------------------------------
    # 14. Fresh Produce & Meat
    # ---------------------------------------------------------
    { "name": "Fresh Fruits", "uri": "/hyperlocal/Fruits/pr?sid=hloc%2F0071&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Fresh Vegetables", "uri": "/hyperlocal/Vegetables/pr?sid=hloc%2F0072&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Chicken, Meat & Fish", "uri": "/hyperlocal/Chicken-Meat-Fish/pr?sid=hloc%2F0031&marketplace=HYPERLOCAL&sort=discount" },

    # ---------------------------------------------------------
    # 15. Personal Care, Bath & Hygiene
    # ---------------------------------------------------------
    { "name": "Bath & Grooming / Soaps", "uri": "/hyperlocal/Bath-Grooming/pr?sid=hloc%2F0013&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Hair Care & Shampoos", "uri": "/hyperlocal/Hair-Care/pr?sid=hloc%2F0044&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Beauty & Fragrances", "uri": "/hyperlocal/Beauty-Fragrances/pr?sid=hloc%2F0041&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Cleaning Essentials", "uri": "/hyperlocal/Cleaning-Essentials/pr?sid=hloc%2F0025&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Feminine Hygiene", "uri": "/hyperlocal/hloc/qbq2/pr?sid=hloc%2Fqbq2&marketplace=HYPERLOCAL&sort=discount" }
]
