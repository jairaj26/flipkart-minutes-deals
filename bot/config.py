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

# Verified Leaf Subcategories & Aisle Targets (Where products actually live)
CATEGORIES = [
    # Bakery & Biscuits
    { "name": "Biscuits & Cookies", "uri": "/hyperlocal/hloc/0613/pr?sid=hloc%2F0006%2F0613&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Breads & Buns", "uri": "/hyperlocal/hloc/0601/pr?sid=hloc%2F0006%2F0601&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Cakes & Muffins", "uri": "/hyperlocal/hloc/0604/pr?sid=hloc%2F0006%2F0604&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Rusk & Khari", "uri": "/hyperlocal/hloc/0603/pr?sid=hloc%2F0006%2F0603&marketplace=HYPERLOCAL&sort=discount" },

    # Chips & Snacks
    { "name": "Chips", "uri": "/hyperlocal/hloc/1001/pr?sid=hloc%2F0010%2F1001&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Namkeens & Mixture", "uri": "/hyperlocal/hloc/1002/pr?sid=hloc%2F0010%2F1002&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Nachos & Healthy Snacks", "uri": "/hyperlocal/hloc/1003/pr?sid=hloc%2F0010%2F1003&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Roasted Nuts & Popcorn", "uri": "/hyperlocal/hloc/1004/pr?sid=hloc%2F0010%2F1004&marketplace=HYPERLOCAL&sort=discount" },

    # Chocolates & Sweets
    { "name": "Chocolates", "uri": "/hyperlocal/hloc/6501/pr?sid=hloc%2F0065%2F6501&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Chocolate Packs & Candies", "uri": "/hyperlocal/hloc/gwcg/pr?sid=hloc%2F0065%2Fgwcg&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Dark Chocolate & Protein Bars", "uri": "/hyperlocal/hloc/tczo/pr?sid=hloc%2F0065%2Ftczo&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Sweets & Mithai", "uri": "/hyperlocal/hloc/0806/pr?sid=hloc%2F0081%2F0806&marketplace=HYPERLOCAL&sort=discount" },

    # Beverages & Dairy
    { "name": "Soft Drinks & Soda", "uri": "/hyperlocal/hloc/0701/pr?sid=hloc%2F0007%2F0701&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Fruit Juices", "uri": "/hyperlocal/hloc/0702/pr?sid=hloc%2F0007%2F0702&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Dairy, Bread & Eggs", "uri": "/hyperlocal/hloc/3002/pr?sid=hloc%2F0030%2F3002&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Tea, Coffee & Health Drinks", "uri": "/hyperlocal/Tea-Coffee-Milk-Drinks/pr?sid=hloc%2F0011&marketplace=HYPERLOCAL&sort=discount" },

    # Staples & Grocery
    { "name": "Atta & Flours", "uri": "/hyperlocal/hloc/0301/pr?sid=hloc%2F0003%2F0301&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Rice & Rice Products", "uri": "/hyperlocal/hloc/0302/pr?sid=hloc%2F0003%2F0302&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Dals & Pulses", "uri": "/hyperlocal/hloc/0303/pr?sid=hloc%2F0003%2F0303&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Edible Oils & Ghee", "uri": "/hyperlocal/hloc/0901/pr?sid=hloc%2F0009%2F0901&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Spices & Masalas", "uri": "/hyperlocal/hloc/0903/pr?sid=hloc%2F0009%2F0903&marketplace=HYPERLOCAL&sort=discount" },

    # Fresh Produce & Meat
    { "name": "Fresh Fruits", "uri": "/hyperlocal/Fruits/pr?sid=hloc%2F0071&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Fresh Vegetables", "uri": "/hyperlocal/Vegetables/pr?sid=hloc%2F0072&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Chicken, Meat & Fish", "uri": "/hyperlocal/Chicken-Meat-Fish/pr?sid=hloc%2F0031&marketplace=HYPERLOCAL&sort=discount" },

    # Personal Care, Household & Hygiene
    { "name": "Bath & Grooming / Soaps", "uri": "/hyperlocal/Bath-Grooming/pr?sid=hloc%2F0013&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Hair Care & Shampoos", "uri": "/hyperlocal/Hair-Care/pr?sid=hloc%2F0044&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Beauty & Fragrances", "uri": "/hyperlocal/Beauty-Fragrances/pr?sid=hloc%2F0041&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Baby Care & Diapers", "uri": "/hyperlocal/Baby-Care/pr?sid=hloc%2F0001%2F0110&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Cleaning Essentials", "uri": "/hyperlocal/Cleaning-Essentials/pr?sid=hloc%2F0025&marketplace=HYPERLOCAL&sort=discount" },

    # High-Discount Electronics & Lifestyle Aisles
    { "name": "Mobiles & Accessories", "uri": "/hyperlocal/Mobiles/pr?sid=hloc%2F0002&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Earphones & Speakers", "uri": "/hyperlocal/Speakers-Earphone/pr?sid=hloc%2F0039&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Electronics & Gadgets", "uri": "/hyperlocal/Electronics%20and%20Gadgets/pr?sid=hloc%2F0038&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Kitchen & Dining", "uri": "/hyperlocal/Kitchen/pr?sid=hloc%2F0048&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Home Appliances", "uri": "/hyperlocal/hloc/4002/pr?sid=hloc%2F0040%2F4002&marketplace=HYPERLOCAL&sort=discount" }
]
