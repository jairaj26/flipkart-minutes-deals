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
# 10 Clean Solr Grocery Categories (Direct Solr Facets)
# -----------------------------------------------------------------------------
CATEGORIES = [
    {
        "name": "Staples \u203a Dal & Pulses",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/bpe&p[]=facets.category[]=73z/bpe/3uv/"
    },
    {
        "name": "Staples \u203a Ghee and Oils",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/bpe&p[]=facets.category[]=73z/bpe/4wu/"
    },
    {
        "name": "Staples \u203a Atta and Flours",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/bpe&p[]=facets.category[]=73z/bpe/9da/"
    },
    {
        "name": "Staples \u203a Masala and Spices",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/bpe&p[]=facets.category[]=73z/bpe/a6m/"
    },
    {
        "name": "Staples \u203a Rice and Rice Products",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/bpe&p[]=facets.category[]=73z/bpe/zwp/"
    },
    {
        "name": "Staples \u203a Dry Fruits, Nuts & Seeds",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/bpe&p[]=facets.category[]=73z/bpe/dtp/"
    },
    {
        "name": "Staples \u203a Sugar, Jaggery & Salt",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/bpe&p[]=facets.category[]=73z/bpe/fdl/"
    },
    {
        "name": "Tea & Coffee \u203a Tea",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/ujs&p[]=facets.category[]=73z/ujs/amr/"
    },
    {
        "name": "Tea & Coffee \u203a Coffee",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/ujs&p[]=facets.category[]=73z/ujs/t7k/"
    },
    {
        "name": "Tea & Coffee \u203a Nutritional & Health Drink Mix",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/ujs&p[]=facets.category[]=73z/ujs/vnq/"
    },
    {
        "name": "Cold Drinks & Juices \u203a Soft Drinks & Sodas",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/ujs&p[]=facets.category[]=73z/ujs/dfw/"
    },
    {
        "name": "Cold Drinks & Juices \u203a Fruit Juices",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/ujs&p[]=facets.category[]=73z/ujs/afd/"
    },
    {
        "name": "Cold Drinks & Juices \u203a Instant Drink Mixes, Squash & Syrups",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/ujs&p[]=facets.category[]=73z/ujs/iau/"
    },
    {
        "name": "Cold Drinks & Juices \u203a Water",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/ujs&p[]=facets.category[]=73z/ujs/wsx/"
    },
    {
        "name": "Snacks & Munchies \u203a Biscuits & Cookies",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/ujs&p[]=facets.category[]=73z/ujs/eb9/"
    },
    {
        "name": "Snacks & Munchies \u203a Chips, Namkeen and Snacks",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/ujs&p[]=facets.category[]=73z/ujs/dd9/"
    },
    {
        "name": "Dairy, Bakery and Eggs \u203a Dairy",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/esa&p[]=facets.category[]=73z/esa/dt6/"
    },
    {
        "name": "Dairy, Bakery and Eggs \u203a Eggs",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/esa&p[]=facets.category[]=73z/esa/hh7/"
    },
    {
        "name": "Dairy, Bakery and Eggs \u203a Bakery Sweets and Namkeen",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/esa&p[]=facets.category[]=73z/esa/93l/"
    },
    {
        "name": "Packaged Goods \u203a Noodles and Pasta",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/u0u&p[]=facets.category[]=73z/u0u/ltz/"
    },
    {
        "name": "Packaged Goods \u203a Chocolates and Sweets",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/u0u&p[]=facets.category[]=73z/u0u/7o6/"
    },
    {
        "name": "Packaged Goods \u203a Ketchups and Spreads",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/u0u&p[]=facets.category[]=73z/u0u/0tl/"
    },
    {
        "name": "Packaged Goods \u203a Breakfast Cereals",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/u0u&p[]=facets.category[]=73z/u0u/bx9/"
    },
    {
        "name": "Packaged Goods \u203a Jam and Honey",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/u0u&p[]=facets.category[]=73z/u0u/j4e/"
    },
    {
        "name": "Packaged Goods \u203a Cooking Sauces and Vinegar",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/u0u&p[]=facets.category[]=73z/u0u/wd7/"
    },
    {
        "name": "Packaged Goods \u203a Baking Essentials",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/u0u&p[]=facets.category[]=73z/u0u/td1/"
    },
    {
        "name": "Personal Care & Wellness \u203a Soaps and Body Wash",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/njl&p[]=facets.category[]=73z/njl/sn6/"
    },
    {
        "name": "Personal Care & Wellness \u203a Hair Care",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/njl&p[]=facets.category[]=73z/njl/vpw/"
    },
    {
        "name": "Personal Care & Wellness \u203a Oral Care",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/njl&p[]=facets.category[]=73z/njl/2s3/"
    },
    {
        "name": "Personal Care & Wellness \u203a Deos, Perfumes and Talcs",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/njl&p[]=facets.category[]=73z/njl/np3/"
    },
    {
        "name": "Personal Care & Wellness \u203a Creams, Lotions Skin Care",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/njl&p[]=facets.category[]=73z/njl/n3m/"
    },
    {
        "name": "Personal Care & Wellness \u203a Kajal and Makeup",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/njl&p[]=facets.category[]=73z/njl/lzq/"
    },
    {
        "name": "Personal Care & Wellness \u203a Sanitary Needs",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/njl&p[]=facets.category[]=73z/njl/tlj/"
    },
    {
        "name": "Personal Care & Wellness \u203a Wellness and Common Pharma",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/njl&p[]=facets.category[]=73z/njl/07d/"
    },
    {
        "name": "Personal Care & Wellness \u203a Shaving Needs",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/njl&p[]=facets.category[]=73z/njl/nw3/"
    },
    {
        "name": "Baby Care \u203a Diapers and Wipes",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/njl&p[]=facets.category[]=73z/njl/smb/"
    },
    {
        "name": "Baby Care \u203a Baby Food",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/njl&p[]=facets.category[]=73z/njl/2jj/"
    },
    {
        "name": "Baby Care \u203a Baby Bath and Skin Care",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/njl&p[]=facets.category[]=73z/njl/m1f/"
    },
    {
        "name": "Fruits and Vegetables \u203a Fruits",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/mk9&p[]=facets.category[]=73z/mk9/w9z/"
    },
    {
        "name": "Fruits and Vegetables \u203a Vegetables",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/mk9&p[]=facets.category[]=73z/mk9/aiw/"
    },
    {
        "name": "Household Care \u203a Detergents and Laundry",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/cwl&p[]=facets.category[]=73z/cwl/2z2/"
    },
    {
        "name": "Household Care \u203a Utensil Cleaners",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/cwl&p[]=facets.category[]=73z/cwl/bdc/"
    },
    {
        "name": "Household Care \u203a Floor and Other Cleaners",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/cwl&p[]=facets.category[]=73z/cwl/u3c/"
    },
    {
        "name": "Household Care \u203a Repellents and Fresheners",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/cwl&p[]=facets.category[]=73z/cwl/qz9/"
    },
    {
        "name": "Household Care \u203a Paper and Disposables",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/cwl&p[]=facets.category[]=73z/cwl/2wc/"
    },
    {
        "name": "Household Care \u203a Basic Electricals",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/cwl&p[]=facets.category[]=73z/cwl/0s4/"
    },
    {
        "name": "Home & Kitchen \u203a Kitchen Tools and Appliances",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/uyk&p[]=facets.category[]=73z/uyk/hho/"
    },
    {
        "name": "Home & Kitchen \u203a Cookware and Serveware",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/uyk&p[]=facets.category[]=73z/uyk/vdx/"
    },
    {
        "name": "Home & Kitchen \u203a Home Utilities",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/uyk/sgh&p[]=facets.category[]=73z/uyk/sgh/lbh/"
    },
    {
        "name": "Home & Kitchen \u203a Home Organisers",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/uyk/sgh&p[]=facets.category[]=73z/uyk/sgh/ib1/"
    },
    {
        "name": "Home & Kitchen \u203a Bath and Bed Essentials",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/uyk&p[]=facets.category[]=73z/uyk/6f4/"
    },
    {
        "name": "Home & Kitchen \u203a Hand Tools",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/uyk/sgh&p[]=facets.category[]=73z/uyk/sgh/nlf/"
    },
    {
        "name": "Electronics & Gadgets \u203a Speakers & Earphones",
        "uri": "/hyperlocal/Speakers%20nd%20Earphones/pr?sid=hloc%2F0039&marketplace=HYPERLOCAL&sort=discount"
    },
    {
        "name": "Electronics & Gadgets \u203a Smartwatches & Wearables",
        "uri": "/ajy/~cs-n07lff2ctz/pr?sid=ajy&marketplace=HYPERLOCAL&collection-tab-name=Smartwatches&sort=discount"
    },
    {
        "name": "Electronics & Gadgets \u203a Kitchen & Home Appliances",
        "uri": "/j9e/abm/~cs-sg12jxivk6/pr?sid=j9e%2Cabm&marketplace=HYPERLOCAL&collection-tab-name=Appliances&sort=discount"
    },
    {
        "name": "Ice Cream & Desserts \u203a Ice Creams & Desserts",
        "uri": "/hyperlocal/IceCream-Desserts/pr?sid=hloc%2F0034&marketplace=HYPERLOCAL&sort=discount"
    },
    {
        "name": "Ice Cream & Desserts \u203a Sweets & Mithai",
        "uri": "/hyperlocal/hloc/0806/pr?sid=hloc%2F0081%2F0806&marketplace=HYPERLOCAL&sort=discount"
    },
    {
        "name": "Toys, Games & Sports \u203a Toys & Games",
        "uri": "/hyperlocal/Toys-Games/pr?sid=hloc%2F0028&marketplace=HYPERLOCAL&sort=discount"
    },
    {
        "name": "Toys, Games & Sports \u203a Sports & Fitness",
        "uri": "/hyperlocal/Sports-Fitness/pr?sid=hloc%2F0036&marketplace=HYPERLOCAL&sort=discount"
    },
    {
        "name": "Office & School Supplies",
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
    },
]=facets.category[]=73z/bpe"
    },
    {
        "name": "Snacks & Beverages",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/ujs"
    },
    {
        "name": "Dairy, Bakery and Eggs",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/esa"
    },
    {
        "name": "Packaged Goods",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z&p[]=facets.category[]=73z/u0u/"
    },
    {
        "name": "Personal and Baby Care",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z&p[]=facets.category[]=73z/njl/"
    },
    {
        "name": "Fruits and Vegetables",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z&p[]=facets.category[]=73z/mk9/"
    },
    {
        "name": "Household Care",
        # Clean composite excluding Pooja Needs (73z/cwl/u64/) and Pet Food (73z/cwl/m92/)
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/cwl/2z2/&p[]=facets.category[]=73z/cwl/bdc/&p[]=facets.category[]=73z/cwl/u3c/&p[]=facets.category[]=73z/cwl/qz9/&p[]=facets.category[]=73z/cwl/2wc/&p[]=facets.category[]=73z/cwl/0s4/"
    },
    {
        "name": "Home & Kitchen",
        # Clean composite excluding Mobile Pouches (73z/uyk/sgh/jaa/) and Festive (73z/uyk/hnw/)
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/uyk/sgh/lbh/&p[]=facets.category[]=73z/uyk/sgh/ib1/&p[]=facets.category[]=73z/uyk/sgh/nlf/&p[]=facets.category[]=73z/uyk/hho/&p[]=facets.category[]=73z/uyk/vdx/&p[]=facets.category[]=73z/uyk/6f4/"
    },
    {
        "name": "Decor & Festive Needs",
        # Standalone route gated at >= 90%
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z&p[]=facets.category[]=73z/uyk/&p[]=facets.category[]=73z/uyk/hnw/"
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
        "name": "Electronics & Gadgets",
        "uri": "/hyperlocal/Electronics%20and%20Gadgets/pr?sid=hloc%2F0038&marketplace=HYPERLOCAL&sort=discount"
    },
    {
        "name": "Ice Cream & Desserts",
        "uri": "/hyperlocal/IceCream-Desserts/pr?sid=hloc%2F0034&marketplace=HYPERLOCAL&sort=discount"
    },
    {
        "name": "Toys, Games & Sports",
        "uri": "/hyperlocal/Toys-Games/pr?sid=hloc%2F0028&marketplace=HYPERLOCAL&sort=discount"
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
