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
        "name": "Staples",
        "uri": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/bpe"
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
    }
]
