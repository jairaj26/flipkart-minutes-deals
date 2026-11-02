import os

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

# Deal Filters & Settings
DEFAULT_PINCODE = os.getenv("PINCODE", "560045").strip()
FLIPKART_COOKIE = os.getenv("FLIPKART_COOKIE", "").strip()
DEFAULT_MIN_DISCOUNT = int(os.getenv("MIN_DISCOUNT", "65"))
MIN_DISCOUNT = DEFAULT_MIN_DISCOUNT
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

# -----------------------------------------------------------------------------
# Dynamic Discount Threshold Configuration (Hierarchical Rule Engine)
# -----------------------------------------------------------------------------
# 1. Category-specific threshold overrides (percentage)
CATEGORY_THRESHOLDS = {
    "Fruits and Vegetables": 90,
    "Fresh Vegetables": 90,
    "Fresh Fruits": 90,
    "Decor & Festive Needs": 90,
}

# 2. Brand-specific threshold overrides (percentage)
# Lowercase keys for case-insensitive matching
BRAND_THRESHOLDS = {
    # 13 Home & Kitchen brands gated at >= 90% (allowed, not blacklisted)
    "clothology": 90,
    "decent home": 90,
    "qxore": 90,
    "sarvoch": 90,
    "elegant weavers": 90,
    "perpetual": 90,
    "xbey": 90,
    "fezora": 90,
    "flipkart smartbuy": 90,
    "crea4": 90,
    "omortex": 90,
    "bombay kookware": 90,
    "deodap": 90,
}

# 3. Keyword / Substring threshold overrides: list of (keyword_phrase, threshold_pct)
# Ready for user to easily customize specific items (e.g. Cadbury 50%, Cooking Oil 40%, Olive/Pomace Oil 85%)
KEYWORD_THRESHOLDS = [
    # ("cadbury", 50),
    # ("cooking oil", 40),
    # ("olive oil", 85),
    # ("pomace oil", 85),
]

# -----------------------------------------------------------------------------
# Blacklist & Negative Filtering (Strict exclusions)
# -----------------------------------------------------------------------------
# Keywords in title that cause deal to be completely dropped
EXCLUDED_KEYWORDS = [
    # Mobile accessories & covers
    "back cover", "case cover", "phone cover", "mobile cover", "phone case",
    "mobile case", "mobile pouch", "phone pouch", "tempered glass", "screen protector",
    "screen guard", "camera protector", "camera lens protector",
    # Rakhi & Festive items
    "rakhi", "rakshabandhan", "lumba", "chuda rakhi", "roli chawal", "rakhee",
    # Pooja / Puja rituals & Pooja needs
    "puja thali", "pooja thali", "pooja needs", "puja needs", "hawan samagri",
    "sambrani cup", "camphor tablet", "dhoop cone", "agarbatti stand", "diya brass",
    # Pet food & supplies
    "dog food", "cat food", "pet food", "puppy food", "kitten food", "bird food",
]

# Excluded brands (case-insensitive check against title start/by brand)
EXCLUDED_BRANDS = [
    # Rakhi & Puja brands
    "designer rakhi", "rudraksh", "religious ganesha rakhi", "d1769",
    "tied ribbons", "craftvatika",
    # Pet food brands
    "pedigree", "whiskas", "drools", "purepet", "royal canin", "me-o",
    # Phone case / junk brands
    "100percent", "abt", "adofys", "aircase", "amazer", "amzer", "annprash",
    "casotec", "cease", "cover alive", "doubleshot",
    "golden tree collection", "hritika", "hyper mob", "kartik crafts",
    "kavish", "maru", "mixtron", "mudrika", "mumbai creations",
    "paper plane design", "parasnath", "shine craft", "sunshine sale",
    "vanya"
]

# -----------------------------------------------------------------------------
# 63 Clean Solr Grocery & Minutes Categories (Direct Solr Facets)
# -----------------------------------------------------------------------------
CATEGORIES = [
    {
        "name": "Staples › Dal & Pulses",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/bpe&p[]=facets.category[]=73z/bpe/3uv/"
    },
    {
        "name": "Staples › Ghee and Oils",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/bpe&p[]=facets.category[]=73z/bpe/4wu/"
    },
    {
        "name": "Staples › Atta and Flours",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/bpe&p[]=facets.category[]=73z/bpe/9da/"
    },
    {
        "name": "Staples › Masala and Spices",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/bpe&p[]=facets.category[]=73z/bpe/a6m/"
    },
    {
        "name": "Staples › Rice and Rice Products",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/bpe&p[]=facets.category[]=73z/bpe/zwp/"
    },
    {
        "name": "Staples › Dry Fruits, Nuts & Seeds",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/bpe&p[]=facets.category[]=73z/bpe/dtp/"
    },
    {
        "name": "Staples › Sugar, Jaggery & Salt",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/bpe&p[]=facets.category[]=73z/bpe/fdl/"
    },
    {
        "name": "Tea & Coffee › Tea",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/ujs&p[]=facets.category[]=73z/ujs/amr/"
    },
    {
        "name": "Tea & Coffee › Coffee",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/ujs&p[]=facets.category[]=73z/ujs/t7k/"
    },
    {
        "name": "Tea & Coffee › Nutritional & Health Drink Mix",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/ujs&p[]=facets.category[]=73z/ujs/vnq/"
    },
    {
        "name": "Cold Drinks & Juices › Soft Drinks & Sodas",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/ujs&p[]=facets.category[]=73z/ujs/dfw/"
    },
    {
        "name": "Cold Drinks & Juices › Fruit Juices",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/ujs&p[]=facets.category[]=73z/ujs/afd/"
    },
    {
        "name": "Cold Drinks & Juices › Instant Drink Mixes, Squash & Syrups",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/ujs&p[]=facets.category[]=73z/ujs/iau/"
    },
    {
        "name": "Cold Drinks & Juices › Water",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/ujs&p[]=facets.category[]=73z/ujs/wsx/"
    },
    {
        "name": "Snacks & Munchies › Biscuits & Cookies",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/ujs&p[]=facets.category[]=73z/ujs/eb9/"
    },
    {
        "name": "Snacks & Munchies › Chips, Namkeen and Snacks",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/ujs&p[]=facets.category[]=73z/ujs/dd9/"
    },
    {
        "name": "Dairy, Bakery and Eggs › Dairy",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/esa&p[]=facets.category[]=73z/esa/dt6/"
    },
    {
        "name": "Dairy, Bakery and Eggs › Eggs",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/esa&p[]=facets.category[]=73z/esa/hh7/"
    },
    {
        "name": "Dairy, Bakery and Eggs › Bakery Sweets and Namkeen",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/esa&p[]=facets.category[]=73z/esa/93l/"
    },
    {
        "name": "Packaged Goods › Noodles and Pasta",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/u0u&p[]=facets.category[]=73z/u0u/ltz/"
    },
    {
        "name": "Packaged Goods › Chocolates and Sweets",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/u0u&p[]=facets.category[]=73z/u0u/7o6/"
    },
    {
        "name": "Packaged Goods › Ketchups and Spreads",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/u0u&p[]=facets.category[]=73z/u0u/0tl/"
    },
    {
        "name": "Packaged Goods › Breakfast Cereals",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/u0u&p[]=facets.category[]=73z/u0u/bx9/"
    },
    {
        "name": "Packaged Goods › Jam and Honey",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/u0u&p[]=facets.category[]=73z/u0u/j4e/"
    },
    {
        "name": "Packaged Goods › Cooking Sauces and Vinegar",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/u0u&p[]=facets.category[]=73z/u0u/wd7/"
    },
    {
        "name": "Packaged Goods › Baking Essentials",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/u0u&p[]=facets.category[]=73z/u0u/td1/"
    },
    {
        "name": "Personal Care & Wellness › Soaps and Body Wash",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/njl&p[]=facets.category[]=73z/njl/sn6/"
    },
    {
        "name": "Personal Care & Wellness › Hair Care",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/njl&p[]=facets.category[]=73z/njl/vpw/"
    },
    {
        "name": "Personal Care & Wellness › Oral Care",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/njl&p[]=facets.category[]=73z/njl/2s3/"
    },
    {
        "name": "Personal Care & Wellness › Deos, Perfumes and Talcs",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/njl&p[]=facets.category[]=73z/njl/np3/"
    },
    {
        "name": "Personal Care & Wellness › Creams, Lotions Skin Care",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/njl&p[]=facets.category[]=73z/njl/n3m/"
    },
    {
        "name": "Personal Care & Wellness › Kajal and Makeup",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/njl&p[]=facets.category[]=73z/njl/lzq/"
    },
    {
        "name": "Personal Care & Wellness › Sanitary Needs",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/njl&p[]=facets.category[]=73z/njl/tlj/"
    },
    {
        "name": "Personal Care & Wellness › Wellness and Common Pharma",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/njl&p[]=facets.category[]=73z/njl/07d/"
    },
    {
        "name": "Personal Care & Wellness › Shaving Needs",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/njl&p[]=facets.category[]=73z/njl/nw3/"
    },
    {
        "name": "Baby Care › Diapers and Wipes",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/njl&p[]=facets.category[]=73z/njl/smb/"
    },
    {
        "name": "Baby Care › Baby Food",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/njl&p[]=facets.category[]=73z/njl/2jj/"
    },
    {
        "name": "Baby Care › Baby Bath and Skin Care",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/njl&p[]=facets.category[]=73z/njl/m1f/"
    },
    {
        "name": "Fruits and Vegetables › Fruits",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/mk9&p[]=facets.category[]=73z/mk9/w9z/"
    },
    {
        "name": "Fruits and Vegetables › Vegetables",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/mk9&p[]=facets.category[]=73z/mk9/aiw/"
    },
    {
        "name": "Household Care › Detergents and Laundry",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/cwl&p[]=facets.category[]=73z/cwl/2z2/"
    },
    {
        "name": "Household Care › Utensil Cleaners",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/cwl&p[]=facets.category[]=73z/cwl/bdc/"
    },
    {
        "name": "Household Care › Floor and Other Cleaners",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/cwl&p[]=facets.category[]=73z/cwl/u3c/"
    },
    {
        "name": "Household Care › Repellents and Fresheners",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/cwl&p[]=facets.category[]=73z/cwl/qz9/"
    },
    {
        "name": "Household Care › Paper and Disposables",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/cwl&p[]=facets.category[]=73z/cwl/2wc/"
    },
    {
        "name": "Household Care › Basic Electricals",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/cwl&p[]=facets.category[]=73z/cwl/0s4/"
    },
    {
        "name": "Home & Kitchen › Kitchen Tools and Appliances",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/uyk&p[]=facets.category[]=73z/uyk/hho/"
    },
    {
        "name": "Home & Kitchen › Cookware and Serveware",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/uyk&p[]=facets.category[]=73z/uyk/vdx/"
    },
    {
        "name": "Home & Kitchen › Home Utilities",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/uyk/sgh&p[]=facets.category[]=73z/uyk/sgh/lbh/"
    },
    {
        "name": "Home & Kitchen › Home Organisers",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/uyk/sgh&p[]=facets.category[]=73z/uyk/sgh/ib1/"
    },
    {
        "name": "Home & Kitchen › Bath and Bed Essentials",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/uyk&p[]=facets.category[]=73z/uyk/6f4/"
    },
    {
        "name": "Home & Kitchen › Hand Tools",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/uyk/sgh&p[]=facets.category[]=73z/uyk/sgh/nlf/"
    },
    {
        "name": "Electronics & Gadgets › Speakers & Earphones",
        "uri": "/hyperlocal/Speakers%20nd%20Earphones/pr?sid=hloc%2F0039&marketplace=HYPERLOCAL&sort=discount"
    },
    {
        "name": "Electronics & Gadgets › Smartwatches & Wearables",
        "uri": "/ajy/~cs-n07lff2ctz/pr?sid=ajy&marketplace=HYPERLOCAL&collection-tab-name=Smartwatches&sort=discount"
    },
    {
        "name": "Electronics & Gadgets › Kitchen & Home Appliances",
        "uri": "/j9e/abm/~cs-sg12jxivk6/pr?sid=j9e%2Cabm&marketplace=HYPERLOCAL&collection-tab-name=Appliances&sort=discount"
    },
    {
        "name": "Ice Cream & Desserts › Ice Creams & Desserts",
        "uri": "/hyperlocal/IceCream-Desserts/pr?sid=hloc%2F0034&marketplace=HYPERLOCAL&sort=discount"
    },
    {
        "name": "Ice Cream & Desserts › Sweets & Mithai",
        "uri": "/hyperlocal/hloc/0806/pr?sid=hloc%2F0081%2F0806&marketplace=HYPERLOCAL&sort=discount"
    },
    {
        "name": "Toys, Games & Sports › Toys & Games",
        "uri": "/hyperlocal/Toys-Games/pr?sid=hloc%2F0028&marketplace=HYPERLOCAL&sort=discount"
    },
    {
        "name": "Toys, Games & Sports › Sports & Fitness",
        "uri": "/hyperlocal/Sports-Fitness/pr?sid=hloc%2F0036&marketplace=HYPERLOCAL&sort=discount"
    },
    {
        "name": "Office and School Supplies",
        "uri": "/grocery/office-school-supplies/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z,pyy&p[]=facets.category[]=73z&p[]=facets.category[]=73z/pyy/"
    },
    {
        "name": "Fashion & Accessories",
        "uri": "/hyperlocal/Fashion-Accessories/pr?sid=hloc%2F0026&marketplace=HYPERLOCAL&sort=discount"
    },
    {
        "name": "Chicken, Meat & Fish",
        "uri": "/hyperlocal/hloc/3106/pr?sid=hloc%2F7n35&marketplace=HYPERLOCAL&sort=discount"
    },
    {
        "name": "Paan Corner & Refreshers",
        "uri": "/hyperlocal/hloc/4901/pr?sid=hloc%2F0049%2F4901&marketplace=HYPERLOCAL&sort=discount"
    }
]
