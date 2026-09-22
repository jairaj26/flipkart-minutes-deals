import os

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

# Deal Filters & Settings
DEFAULT_PINCODE = os.getenv("PINCODE", "560032").strip()
FLIPKART_COOKIE = os.getenv("FLIPKART_COOKIE", "").strip()
MIN_DISCOUNT = int(os.getenv("MIN_DISCOUNT", "50"))
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
    "x-user-agent": X_USER_AGENT
}

# 38 Master Verified Flipkart Minutes Departments
CATEGORIES = [
    { "name": "Fresh Fruits", "uri": "/hyperlocal/Fruits/pr?sid=hloc%2F0071&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Fresh Vegetables", "uri": "/hyperlocal/Vegetables/pr?sid=hloc%2F0072&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Atta, Rice & Dal", "uri": "/hyperlocal/Atta-Rice-Dal/pr?sid=hloc%2F0003&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Oil, Ghee & Masalas", "uri": "/hyperlocal/Oil-Ghee-Masala/pr?sid=hloc%2F0009&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Dairy, Bread & Eggs", "uri": "/hyperlocal/hloc/3002/pr?sid=hloc%2F0030%2F3002&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Chicken, Meat & Fish", "uri": "/hyperlocal/Chicken-Meat-Fish/pr?sid=hloc%2F0031&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Chips, Crisps & Namkeen", "uri": "/hyperlocal/Chips-Namkeen/pr?sid=hloc%2F0010&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Cold Drinks & Juices", "uri": "/hyperlocal/ColdDrinks-Juices/pr?sid=hloc%2F0007&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Bakery & Biscuits", "uri": "/hyperlocal/Bakery-Biscuits/pr?sid=hloc%2F0006&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Tea, Coffee & Milk Drinks", "uri": "/hyperlocal/Tea-Coffee-Milk-Drinks/pr?sid=hloc%2F0011&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Cereals & Dry Fruits", "uri": "/hyperlocal/Cereals-DryFruits/pr?sid=hloc%2F0019&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Instant & Frozen Food", "uri": "/hyperlocal/Instant-FrozenFood/pr?sid=hloc%2F0020&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Sauces & Spreads", "uri": "/hyperlocal/Sauces-Spreads/pr?sid=hloc%2F0021&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Chocolates & Candies", "uri": "/hyperlocal/Fruits/pr?sid=hloc%2F0065&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Ice Cream & Desserts", "uri": "/hyperlocal/IceCream-Desserts/pr?sid=hloc%2F0034&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Sweets & Mithai", "uri": "/hyperlocal/hloc/0806/pr?sid=hloc%2F0081%2F0806&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Paan Corner & Refreshments", "uri": "/hyperlocal/hloc/4904/pr?sid=hloc%2F0049%2F4904&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Bath & Grooming / Soaps", "uri": "/hyperlocal/Bath-Grooming/pr?sid=hloc%2F0013&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Hair Care & Shampoos", "uri": "/hyperlocal/Hair-Care/pr?sid=hloc%2F0044&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Beauty & Fragrances", "uri": "/hyperlocal/Beauty-Fragrances/pr?sid=hloc%2F0041&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Baby Care & Diapers", "uri": "/hyperlocal/Baby-Care/pr?sid=hloc%2F0001%2F0110&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Health & Pharma", "uri": "/hyperlocal/Health-Pharma/pr?sid=hloc%2F0015&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Feminine Hygiene", "uri": "/hyperlocal/Fruits/pr?sid=hloc%2Fqbq2&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Sexual Wellness", "uri": "/hyperlocal/Fruits/pr?sid=hloc%2Fzgt0&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Cleaning Essentials & Detergents", "uri": "/hyperlocal/Cleaning-Essentials/pr?sid=hloc%2F0025&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Kitchen & Dining Essentials", "uri": "/hyperlocal/Kitchen/pr?sid=hloc%2F0048&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Home Furnishing & Bedding", "uri": "/hyperlocal/Toys-Games/pr?sid=hloc%2F0047&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "School Supplies & Stationery", "uri": "/hyperlocal/School-Supplies/pr?sid=hloc%2F0016&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Electricals & Tools", "uri": "/hyperlocal/Electircals-Tools/pr?sid=hloc%2F0043&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Pooja Needs & Agarbatti", "uri": "/hyperlocal/Toys-Games/pr?sid=hloc%2F0082&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Pet Care & Pet Food", "uri": "/hyperlocal/PetCare/pr?sid=hloc%2F0029&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Toys & Games", "uri": "/hyperlocal/Toys-Games/pr?sid=hloc%2F0028&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Sports & Fitness", "uri": "/hyperlocal/Sports-Fitness/pr?sid=hloc%2F0036&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Fashion Accessories", "uri": "/hyperlocal/Fashion-Accessories/pr?sid=hloc%2F0026&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Mobiles & Accessories", "uri": "/hyperlocal/Mobiles/pr?sid=hloc%2F0002&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Speakers & Earphones", "uri": "/hyperlocal/Speakers-Earphone/pr?sid=hloc%2F0039&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Electronics & Gadgets", "uri": "/hyperlocal/Electronics%20and%20Gadgets/pr?sid=hloc%2F0038&marketplace=HYPERLOCAL&sort=discount" },
    { "name": "Home Appliances", "uri": "/hyperlocal/hloc/4002/pr?sid=hloc%2F0040%2F4002&marketplace=HYPERLOCAL&sort=discount" }
]
