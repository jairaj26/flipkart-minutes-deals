import html
import json
import os
import re
import urllib.parse

def build_bookmarklet():
    with open("data/categories_catalog.json", "r", encoding="utf-8") as f:
        cat_catalog = json.load(f)

    with open("data/brands_catalog.json", "r", encoding="utf-8") as f:
        brand_catalog = json.load(f)

    raw_excluded = brand_catalog.get("excluded_brands", []) + [
        "100percent", "abt", "adofys", "aircase", "amazer", "amzer", "annprash",
        "casotec", "cease", "cover alive", "doubleshot",
        "golden tree collection", "hritika", "hyper mob", "kartik crafts",
        "kavish", "maru", "mixtron", "mudrika", "mumbai creations",
        "paper plane design", "parasnath", "shine craft", "sunshine sale",
        "tied ribbons", "vanya", "pedigree", "whiskas", "drools", "purepet",
        "royal canin", "me-o", "designer rakhi", "rudraksh", "religious ganesha rakhi", "d1769"
    ]
    excluded_brands = sorted(list({b.strip().lower() for b in raw_excluded if b.strip()}))

    # Group icons for all quick-commerce categories
    icons = {
        "Staples": "🌾",
        "Tea & Coffee": "☕",
        "Cold Drinks & Juices": "🧃",
        "Snacks & Munchies": "🍟",
        "Dairy, Bakery and Eggs": "🥛",
        "Packaged Goods": "🥫",
        "Personal Care & Wellness": "🧼",
        "Baby Care": "👶",
        "Fruits and Vegetables": "🍎",
        "Household Care": "🧹",
        "Home & Kitchen": "🍳",
        "Office and School Supplies": "📚",
        "Fashion & Accessories": "👕",
        "Electronics & Gadgets": "🔌",
        "Ice Cream & Desserts": "🍦",
        "Toys, Games & Sports": "🧸",
        "Chicken, Meat & Fish": "🍗",
        "Paan Corner & Refreshers": "🌿"
    }

    # Verified quick scan parent URIs (clean parent routes, free of spam phone cases)
    parent_uris = {
        "Staples": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/bpe",
        "Tea & Coffee": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/ujs&p[]=facets.category[]=73z/ujs/amr/&p[]=facets.category[]=73z/ujs/t7k/&p[]=facets.category[]=73z/ujs/vnq/",
        "Cold Drinks & Juices": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/ujs&p[]=facets.category[]=73z/ujs/dfw/&p[]=facets.category[]=73z/ujs/afd/&p[]=facets.category[]=73z/ujs/iau/&p[]=facets.category[]=73z/ujs/wsx/",
        "Snacks & Munchies": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/ujs&p[]=facets.category[]=73z/ujs/eb9/&p[]=facets.category[]=73z/ujs/dd9/",
        "Dairy, Bakery and Eggs": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/esa",
        "Packaged Goods": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/u0u/",
        "Personal Care & Wellness": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/njl/",
        "Baby Care": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/njl/1a7/&p[]=facets.category[]=73z/njl/5w6/&p[]=facets.category[]=73z/njl/y5b/",
        "Fruits and Vegetables": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/mk9/",
        "Household Care": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/cwl/2z2/&p[]=facets.category[]=73z/cwl/bdc/&p[]=facets.category[]=73z/cwl/u3c/&p[]=facets.category[]=73z/cwl/qz9/&p[]=facets.category[]=73z/cwl/2wc/&p[]=facets.category[]=73z/cwl/0s4/",
        "Home & Kitchen": "/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]=73z/uyk/sgh/lbh/&p[]=facets.category[]=73z/uyk/sgh/ib1/&p[]=facets.category[]=73z/uyk/sgh/nlf/&p[]=facets.category[]=73z/uyk/hho/&p[]=facets.category[]=73z/uyk/vdx/&p[]=facets.category[]=73z/uyk/6f4/",
        "Electronics & Gadgets": "/hyperlocal/Speakers%20nd%20Earphones/pr?sid=hloc%2F0039&marketplace=HYPERLOCAL&sort=discount",
        "Ice Cream & Desserts": "/hyperlocal/IceCream-Desserts/pr?sid=hloc%2F0034&marketplace=HYPERLOCAL&sort=discount",
        "Toys, Games & Sports": "/hyperlocal/Toys-Games/pr?sid=hloc%2F0028&marketplace=HYPERLOCAL&sort=discount",
        "Office and School Supplies": "/grocery/office-school-supplies/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z,pyy&p[]=facets.category[]=73z&p[]=facets.category[]=73z/pyy/",
        "Fashion & Accessories": "/hyperlocal/Fashion-Accessories/pr?sid=hloc%2F0026&marketplace=HYPERLOCAL&sort=discount",
        "Chicken, Meat & Fish": "/hyperlocal/hloc/3106/pr?sid=hloc%2F7n35&marketplace=HYPERLOCAL&sort=discount",
        "Paan Corner & Refreshers": "/hyperlocal/hloc/4901/pr?sid=hloc%2F0049%2F4901&marketplace=HYPERLOCAL&sort=discount"
    }

    category_tree = []
    main_groups = []

    for group_name, subcats in cat_catalog["groups"].items():
        icon = icons.get(group_name, "📦")
        group_disp_name = f"{icon} {group_name}"
        parent_url = parent_uris.get(group_name, subcats[0]["url_path"])

        # Process subcategories: Clean names, direct leaf Solr facets
        children = []
        for sub in subcats:
            if "Excl." in sub["name"] or sub["name"].startswith("All "):
                continue
            if "(All Parent)" in sub["name"]:
                continue

            is_optin = not sub.get("default_selected", True)
            optin_suffix = " (Opt-in)" if is_optin else ""
            clean_sub_name = f"{sub['name']}{optin_suffix}".strip()

            children.append({
                "id": f"sub_{sub['category_code'].replace('/', '_')}",
                "name": clean_sub_name,
                "uri": sub["url_path"],
                "isOptin": is_optin
            })

        group_entry = {
            "id": f"grp_{group_name.replace(' ', '_').replace('&', 'and')}",
            "group": group_name,
            "name": group_disp_name,
            "uri": parent_url,
            "subs": children
        }
        category_tree.append(group_entry)
        main_groups.append({
            "id": group_entry["id"],
            "group": group_name,
            "name": group_disp_name,
            "uri": parent_url
        })

    print(f"Total category tree nodes generated: {len(category_tree)}")
    print(f"Total main scan groups: {len(main_groups)}")

    js_category_tree = json.dumps(category_tree, indent=2, ensure_ascii=False)
    js_main_groups = json.dumps(main_groups, indent=2, ensure_ascii=False)
    js_excluded_brands = json.dumps(excluded_brands, indent=2, ensure_ascii=False)

    template = f"""javascript:(function(){{
  try {{
    var tToast = document.getElementById("fk-loader-toast");
    if (tToast) tToast.remove();
  }} catch(e) {{}}

  /* Clean up existing instances */
  ['fk-deals-sidebar', 'fk-deals-pill', 'fk-deals-styles'].forEach(function(id){{
    var el = document.getElementById(id);
    if (el) el.remove();
  }});

  try {{
  var d = document;

  /* Verified Category Catalog (Direct Solr Facets Collapsible Tree) */
  var CATEGORY_TREE = {js_category_tree};

  /* Clean Main Groups for Full Store Scanning */
  var MAIN_GROUPS = {js_main_groups};

  /* Negative Filtering Blacklist */
  var EXCLUDED_KEYWORDS = [
    "back cover", "case cover", "phone cover", "mobile cover", "phone case",
    "mobile case", "mobile pouch", "phone pouch", "tempered glass", "screen protector",
    "screen guard", "camera protector", "camera lens protector",
    "rakhi", "rakshabandhan", "lumba", "chuda rakhi", "roli chawal", "rakhee",
    "puja thali", "pooja thali", "pooja needs", "puja needs", "hawan samagri",
    "sambrani cup", "camphor tablet", "dhoop cone", "agarbatti stand", "diya brass",
    "dog food", "cat food", "pet food", "puppy food", "kitten food", "bird food"
  ];
  var EXCLUDED_BRANDS = {js_excluded_brands};

  /* Dynamic Threshold Rules */
  var DEFAULT_MIN_DISCOUNT = 45;
  var BRAND_THRESHOLDS = {{
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
    "deodap": 90
  }};

  /* State Management */
  var st = {{
    mode: "IDLE",
    sort: "discount",
    searchQuery: "",
    items: [],
    seen: new Set(),
    hideOos: true,
    isCollapsed: false,
    allowPhoneCases: false
  }};

  /* Selected Subcategories & Parent Groups (None selected by default; Max 2 parent groups) */
  var selectedSubIds = new Set();
  var selectedParentGroups = new Set();

  window.fkDealsStop = false;

  /* Helper function: Extract human-friendly product title from Flipkart canonical URL slug */
  function extractTitleFromUrl(url) {{
    try {{
      if (!url) return "";
      var m = url.match(/\\/([a-z0-9][a-z0-9-]+[a-z0-9])\\/p\\/(?:itm|[a-z0-9]+)/i);
      if (m && m[1]) {{
        var slug = m[1].replace(/-/g, " ").trim();
        if (slug.length > 3) {{
          return slug.replace(/\\b[a-z]/g, function(c){{ return c.toUpperCase(); }});
        }}
      }}
    }} catch(e) {{}}
    return "";
  }}

  /* Safe HTML escaping helper to prevent XSS injection from product titles & images */
  function escapeHtml(s) {{
    if (s == null) return "";
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }}

  /* Inject Canva-inspired Clean Styles with Flipkart Minutes Colors */
  var style = d.createElement("style");
  style.id = "fk-deals-styles";
  style.textContent = `
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    #fk-deals-sidebar, #fk-deals-pill {{
      --fkd-bg: #F8F9FA;
      --fkd-header-bg: #FFFFFF;
      --fkd-border: #E5E7EB;
      --fkd-border-light: #F3F4F6;
      --fkd-text-main: #1F2937;
      --fkd-text-sub: #4B5563;
      --fkd-text-muted: #9CA3AF;
      --fkd-green: #0F8458;
      --fkd-green-hover: #0D724C;
      --fkd-green-tint: #E8F5E9;
      --fkd-danger: #DC2626;
      --fkd-danger-hover: #B91C1C;
      --fkd-card-bg: #FFFFFF;
      --fkd-card-border: #E5E7EB;
      --fkd-card-hover: #D1D5DB;
      --fkd-font: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
      font-family: var(--fkd-font);
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
      text-rendering: optimizeLegibility;
      box-sizing: border-box;
    }}

    #fk-deals-sidebar *, #fk-deals-pill * {{
      box-sizing: border-box;
    }}

    #fk-deals-sidebar {{
      position: fixed;
      top: 0;
      right: 0;
      width: 410px;
      max-width: 100vw;
      height: 100vh;
      background: var(--fkd-bg);
      z-index: 2147483647;
      display: flex;
      flex-direction: column;
      border-left: 1px solid var(--fkd-border);
      box-shadow: -4px 0 24px rgba(0, 0, 0, 0.08);
      color: var(--fkd-text-main);
      transition: transform 0.22s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    #fk-deals-sidebar.collapsed {{
      transform: translateX(105%);
      pointer-events: none;
    }}

    #fk-deals-pill {{
      position: fixed;
      bottom: 24px;
      right: 20px;
      z-index: 2147483647;
      background: var(--fkd-green);
      color: #FFFFFF;
      padding: 10px 16px;
      border-radius: 30px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      box-shadow: 0 4px 18px rgba(15, 132, 88, 0.35);
      display: flex;
      align-items: center;
      gap: 8px;
      border: 1px solid rgba(255, 255, 255, 0.2);
      transition: transform 0.18s ease, background 0.15s ease;
    }}
    #fk-deals-pill:hover {{
      transform: translateY(-2px);
      background: var(--fkd-green-hover);
    }}
    #fk-deals-pill.hidden {{
      display: none;
    }}

    .fkd-badge {{
      background: #F3F4F6;
      color: var(--fkd-text-sub);
      font-size: 11px;
      font-weight: 600;
      padding: 2px 8px;
      border-radius: 9999px;
      letter-spacing: -0.01em;
    }}
    #fk-deals-pill .fkd-badge {{
      background: #FFFFFF;
      color: var(--fkd-green);
    }}

    .fkd-header {{
      background: var(--fkd-header-bg);
      border-bottom: 1px solid var(--fkd-border);
      padding: 12px 14px;
      display: flex;
      flex-direction: column;
      gap: 9px;
    }}

    .fkd-top-row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .fkd-title {{
      font-size: 14px;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 8px;
      color: var(--fkd-text-main);
      letter-spacing: -0.02em;
    }}
    .fkd-controls {{
      display: flex;
      align-items: center;
      gap: 4px;
    }}
    .fkd-icon-btn {{
      background: transparent;
      border: none;
      color: var(--fkd-text-sub);
      width: 26px;
      height: 26px;
      border-radius: 6px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 13px;
      font-weight: 600;
      transition: background 0.12s ease, color 0.12s ease;
    }}
    .fkd-icon-btn:hover {{
      background: #F3F4F6;
      color: var(--fkd-text-main);
    }}

    .fkd-search-row {{
      display: flex;
      gap: 6px;
      align-items: center;
    }}
    .fkd-input {{
      background: #FFFFFF;
      color: var(--fkd-text-main);
      border: 1px solid #D1D5DB;
      border-radius: 7px;
      padding: 7px 11px;
      font-size: 12px;
      font-weight: 400;
      font-family: inherit;
      outline: none;
      transition: border-color 0.15s ease, box-shadow 0.15s ease;
    }}
    .fkd-input::placeholder {{
      color: var(--fkd-text-muted);
    }}
    .fkd-input:focus {{
      border-color: var(--fkd-green);
      box-shadow: 0 0 0 2px rgba(15, 132, 88, 0.15);
    }}

    .fkd-btn-search {{
      background: var(--fkd-green);
      color: #FFFFFF;
      border: 1px solid var(--fkd-green);
      border-radius: 7px;
      padding: 0 13px;
      height: 32px;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      font-family: inherit;
      transition: background 0.12s ease;
      flex: none;
    }}
    .fkd-btn-search:hover {{
      background: var(--fkd-green-hover);
    }}

    /* Canva-Style Category Dropdown */
    .fkd-row-2 {{
      position: relative;
      width: 100%;
    }}
    .fkd-cat-toggle {{
      width: 100%;
      background: #FFFFFF;
      color: var(--fkd-text-main);
      border: 1px solid #D1D5DB;
      border-radius: 7px;
      padding: 7px 11px;
      font-size: 12px;
      font-weight: 500;
      font-family: inherit;
      text-align: left;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      outline: none;
      transition: border-color 0.15s ease, background 0.15s ease;
    }}
    .fkd-cat-toggle:hover {{
      border-color: #9CA3AF;
      background: #FAFAFA;
    }}
    .fkd-cat-toggle-text {{
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      flex: 1;
    }}
    .fkd-caret {{
      font-size: 11px;
      color: var(--fkd-text-sub);
      transition: transform 0.15s ease;
    }}

    .fkd-cat-drawer {{
      position: absolute;
      top: calc(100% + 5px);
      left: 0;
      right: 0;
      background: #FFFFFF;
      border-radius: 10px;
      border: 1px solid #E5E7EB;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08), 0 2px 6px rgba(0, 0, 0, 0.03);
      max-height: 380px;
      overflow-y: auto;
      z-index: 50;
      padding: 7px;
      display: flex;
      flex-direction: column;
      gap: 2px;
    }}
    .fkd-cat-drawer.hidden {{
      display: none;
    }}

    /* Quick Scan & Subcategory Pills Drawer */
    .fkd-quick-scan-box {{
      padding: 8px 10px;
      margin-bottom: 6px;
      border-radius: 8px;
      background: #F0FDF4;
      border: 1px solid #BBF7D0;
      display: flex;
      flex-direction: column;
      gap: 3px;
    }}
    .fkd-quick-scan-btn {{
      width: 100%;
      height: 32px;
      border-radius: 6px;
      background: var(--fkd-green);
      color: #FFFFFF;
      border: none;
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      font-family: inherit;
      box-shadow: 0 1px 3px rgba(15, 132, 88, 0.25);
      transition: background 0.15s ease;
    }}
    .fkd-quick-scan-btn:hover {{
      background: var(--fkd-green-hover);
    }}
    .fkd-quick-scan-sub {{
      font-size: 10.5px;
      color: #166534;
      text-align: center;
      font-weight: 500;
    }}
    .fkd-drawer-hint {{
      font-size: 11px;
      font-weight: 600;
      color: var(--fkd-text-sub);
      padding: 4px 6px 6px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .fkd-dept-item {{
      display: flex;
      flex-direction: column;
      border-radius: 7px;
      margin-bottom: 2px;
    }}
    .fkd-dept-header {{
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 7px 9px;
      border-radius: 7px;
      cursor: pointer;
      user-select: none;
      background: #FAFAFA;
      border: 1px solid #F0F0F0;
      transition: all 0.12s ease;
    }}
    .fkd-dept-header:hover {{
      background: #F4F4F5;
      border-color: #E4E4E7;
    }}
    .fkd-dept-chevron {{
      font-size: 12px;
      font-weight: 700;
      color: var(--fkd-text-sub);
      width: 14px;
      text-align: center;
      display: inline-block;
      transition: transform 0.15s ease;
    }}
    .fkd-dept-chevron.expanded {{
      transform: rotate(90deg);
    }}
    .fkd-dept-name {{
      flex: 1;
      font-size: 12px;
      font-weight: 600;
      color: var(--fkd-text-main);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .fkd-dept-badge {{
      font-size: 10px;
      font-weight: 700;
      color: #FFFFFF;
      background: var(--fkd-green);
      padding: 1px 7px;
      border-radius: 10px;
      flex-shrink: 0;
    }}
    .fkd-dept-badge.hidden {{
      display: none;
    }}

    .fkd-sub-panel {{
      padding: 6px 8px 8px 24px;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}
    .fkd-sub-panel.collapsed {{
      display: none;
    }}
    .fkd-sub-toolbar {{
      display: flex;
      align-items: center;
      gap: 6px;
      padding-bottom: 2px;
    }}
    .fkd-link-btn {{
      background: none;
      border: none;
      padding: 2px 5px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 600;
      color: var(--fkd-green);
      cursor: pointer;
      font-family: inherit;
      transition: background 0.12s ease;
    }}
    .fkd-link-btn:hover {{
      background: rgba(15, 132, 88, 0.08);
    }}
    .fkd-toolbar-sep {{
      color: #D1D5DB;
      font-size: 10px;
    }}

    .fkd-pills-wrap {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }}
    .fkd-sub-pill {{
      background: #F4F4F5;
      color: #3F3F46;
      border: 1px solid #E4E4E7;
      border-radius: 14px;
      padding: 4px 10px;
      font-size: 11px;
      font-weight: 500;
      font-family: inherit;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      transition: all 0.12s ease;
      user-select: none;
      outline: none;
      line-height: 1.2;
    }}
    .fkd-sub-pill:hover {{
      background: #E4E4E7;
      border-color: #D4D4D8;
      color: #18181B;
    }}
    .fkd-sub-pill.active {{
      background: var(--fkd-green);
      color: #FFFFFF;
      border-color: var(--fkd-green);
      font-weight: 600;
      box-shadow: 0 1px 3px rgba(15, 132, 88, 0.25);
    }}

    .fkd-toast {{
      position: absolute;
      bottom: 12px;
      left: 12px;
      right: 12px;
      background: #18181B;
      color: #FFFFFF;
      padding: 8px 12px;
      border-radius: 8px;
      font-size: 11.5px;
      font-weight: 600;
      text-align: center;
      box-shadow: 0 4px 12px rgba(0,0,0,0.25);
      z-index: 100;
      pointer-events: none;
      opacity: 0;
      transform: translateY(6px);
      transition: opacity 0.2s ease, transform 0.2s ease;
    }}
    .fkd-toast.show {{
      opacity: 1;
      transform: translateY(0);
    }}

    /* Toolbar Controls (Off-White & Green Palette) */
    .fkd-toolbar {{
      display: flex;
      gap: 6px;
      align-items: center;
      width: 100%;
    }}
    .fkd-pill {{
      flex: 1 1 0;
      min-width: 0;
      height: 30px;
      padding: 0 4px;
      border-radius: 7px;
      background: #FFFFFF;
      color: var(--fkd-text-main);
      border: 1px solid #D1D5DB;
      font-size: 11px;
      font-weight: 500;
      font-family: inherit;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      white-space: nowrap;
      transition: all 0.12s ease;
      user-select: none;
      outline: none;
    }}
    .fkd-pill:hover {{
      background: #F3F4F6;
      border-color: #9CA3AF;
    }}
    .fkd-pill.active {{
      background: var(--fkd-green);
      color: #FFFFFF;
      border-color: var(--fkd-green);
      font-weight: 600;
    }}

    .fkd-pill-action {{
      background: var(--fkd-green) !important;
      color: #FFFFFF !important;
      border-color: var(--fkd-green) !important;
      font-weight: 700;
    }}
    .fkd-pill-action:hover {{
      background: var(--fkd-green-hover) !important;
    }}

    .fkd-pill-danger {{
      background: var(--fkd-danger) !important;
      color: #FFFFFF !important;
      border-color: var(--fkd-danger) !important;
      font-weight: 700;
    }}
    .fkd-pill-danger:hover {{
      background: var(--fkd-danger-hover) !important;
    }}

    .fkd-status-bar {{
      display: flex;
      align-items: center;
      gap: 6px;
      min-height: 15px;
    }}
    .fkd-status-dot {{
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: var(--fkd-green);
      flex-shrink: 0;
    }}
    .fkd-status-text {{
      font-size: 11px;
      color: var(--fkd-text-sub);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      flex: 1;
      font-weight: 400;
    }}

    /* Product Grid & Cards */
    .fkd-grid {{
      flex: 1;
      overflow-y: auto;
      padding: 12px;
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 10px;
      align-content: start;
      background: var(--fkd-bg);
    }}

    .fkd-card {{
      background: var(--fkd-card-bg);
      border: 1px solid var(--fkd-card-border);
      border-radius: 9px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
      padding: 8px;
      display: flex;
      flex-direction: column;
      cursor: pointer;
      position: relative;
      transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
    }}
    .fkd-card:hover {{
      transform: translateY(-2px);
      box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
      border-color: var(--fkd-card-hover);
    }}
    .fkd-card.oos {{
      opacity: 0.6;
      filter: grayscale(0.2);
    }}

    .fkd-img-box {{
      position: relative;
      width: 100%;
      height: 112px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 7px;
      background: #FFFFFF;
      border-radius: 6px;
      overflow: hidden;
    }}
    .fkd-img {{
      max-width: 100%;
      max-height: 100%;
      object-fit: contain;
    }}

    /* Stacked Larger Discount Tag (User Requested: 70% above OFF in Green) */
    .fkd-disc-tag {{
      position: absolute;
      top: 5px;
      left: 5px;
      background: var(--fkd-green);
      color: #FFFFFF;
      padding: 3px 6px;
      border-radius: 5px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      line-height: 1.05;
      box-shadow: 0 2px 6px rgba(15, 132, 88, 0.25);
      pointer-events: none;
      z-index: 2;
    }}
    .fkd-disc-pct {{
      font-size: 13px;
      font-weight: 800;
      letter-spacing: -0.02em;
    }}
    .fkd-disc-off {{
      font-size: 8px;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      opacity: 0.95;
    }}

    .fkd-oos-tag {{
      position: absolute;
      bottom: 4px;
      left: 4px;
      right: 4px;
      background: rgba(220, 38, 38, 0.92);
      color: #FFFFFF;
      font-size: 9px;
      font-weight: 700;
      text-align: center;
      padding: 2px 0;
      border-radius: 4px;
      letter-spacing: 0.3px;
    }}

    .fkd-card-title {{
      font-size: 11.5px;
      font-weight: 500;
      color: var(--fkd-text-main);
      line-height: 1.35;
      margin-bottom: 6px;
      height: 31px;
      overflow: hidden;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
    }}

    .fkd-price-row {{
      margin-top: auto;
      display: flex;
      align-items: baseline;
      gap: 6px;
    }}
    .fkd-price {{
      font-size: 14px;
      font-weight: 700;
      color: var(--fkd-green);
      letter-spacing: -0.01em;
    }}
    .fkd-mrp {{
      font-size: 11px;
      color: var(--fkd-text-muted);
      text-decoration: line-through;
      font-weight: 400;
    }}

    .fkd-empty {{
      grid-column: 1 / -1;
      text-align: center;
      padding: 40px 15px;
      color: var(--fkd-text-sub);
      font-size: 12.5px;
      line-height: 1.6;
    }}
  `;
  d.head.appendChild(style);

  /* Minimized Floating Pill */
  var pill = d.createElement("div");
  pill.id = "fk-deals-pill";
  pill.className = "hidden";
  pill.innerHTML = `<span>⚡ Minutes Deals</span><span class="fkd-badge" id="fkd-pill-count">0</span>`;
  d.body.appendChild(pill);

  /* Sidebar UI */
  var sb = d.createElement("div");
  sb.id = "fk-deals-sidebar";
  sb.innerHTML = `
    <div class="fkd-header">
      <div class="fkd-top-row">
        <div class="fkd-title">
          <span>⚡ Minutes Deals</span>
          <span class="fkd-badge" id="fkd-head-count">0 Items</span>
        </div>
        <div class="fkd-controls">
          <button class="fkd-icon-btn" id="fkd-btn-min" type="button" title="Minimize / Collapse">—</button>
          <button class="fkd-icon-btn" id="fkd-btn-close" type="button" title="Close">✕</button>
        </div>
      </div>
      <div class="fkd-search-row">
        <input type="text" class="fkd-input" id="fkd-input-search" placeholder="🔍 Search e.g. cake, ghee, surf..." style="flex:1" title="Type keyword and press Enter or click Search">
        <button class="fkd-btn-search" id="fkd-btn-search">Search</button>
      </div>
      <div class="fkd-row-2">
        <button class="fkd-cat-toggle" id="fkd-cat-toggle" type="button" title="Browse & select Flipkart Minutes categories">
          <span class="fkd-cat-toggle-text" id="fkd-selected-cat-name">📂 Select Categories (or Quick Scan)</span>
          <span class="fkd-caret" id="fkd-cat-caret">▾</span>
        </button>
        <div id="fkd-cat-drawer" class="fkd-cat-drawer hidden"></div>
      </div>
      <div class="fkd-toolbar">
        <button class="fkd-pill" id="fkd-sort-price" title="Sort by lowest price">Sort ₹</button>
        <button class="fkd-pill active" id="fkd-sort-disc" title="Sort by highest discount">Sort %</button>
        <button class="fkd-pill active" id="fkd-toggle-oos" title="Toggle Out of Stock items">In Stock</button>
        <button class="fkd-pill fkd-pill-action" id="fkd-btn-fetch" title="Run Quick Scan or Fetch Selected Categories">Quick Scan ⚡</button>
      </div>
      <div class="fkd-status-bar">
        <span class="fkd-status-dot"></span>
        <span class="fkd-status-text" id="fkd-status-msg">Ready</span>
      </div>
    </div>
        <div id="fkd-grid" class="fkd-grid">
      <div class="fkd-empty">Click <b>Quick Scan ⚡</b> to scan top deals across Flipkart Minutes, or pick categories above.</div>
    </div>
    <div id="fkd-toast" class="fkd-toast"></div>
  `;
  d.body.appendChild(sb);

  /* Element References */
  var catToggle = d.getElementById("fkd-cat-toggle");
  var catNameDisplay = d.getElementById("fkd-selected-cat-name");
  var catCaret = d.getElementById("fkd-cat-caret");
  var catDrawer = d.getElementById("fkd-cat-drawer");

  function closeCatDrawer() {{
    if (catDrawer && !catDrawer.classList.contains("hidden")) {{
      catDrawer.classList.add("hidden");
      if (catCaret) catCaret.textContent = "▾";
    }}
  }}

  function toggleCatDrawer() {{
    if (!catDrawer) return;
    if (catDrawer.classList.contains("hidden")) {{
      catDrawer.classList.remove("hidden");
      if (catCaret) catCaret.textContent = "▴";
    }} else {{
      closeCatDrawer();
    }}
  }}

  catToggle.onclick = function(e) {{
    e.stopPropagation();
    toggleCatDrawer();
  }};

  /* Toast Notification */
  var toastTimer = null;
  function showToast(msg) {{
    var toast = d.getElementById("fkd-toast");
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.add("show");
    if (toastTimer) clearTimeout(toastTimer);
    toastTimer = setTimeout(function() {{
      toast.classList.remove("show");
    }}, 2800);
  }}

  /* Update Category Selection Summary Label & Fetch Button */
  function updateCategorySummary() {{
    if (selectedSubIds.size === 0) {{
      catNameDisplay.textContent = "📂 Select Categories (or Quick Scan)";
      btnFetch.textContent = "Quick Scan ⚡";
      btnFetch.title = "Quick Scan across all 18 top departments";
      return;
    }}

    var selectedGrpNames = [];
    CATEGORY_TREE.forEach(function(g) {{
      var count = (g.subs || []).filter(function(s){{ return selectedSubIds.has(s.id); }}).length;
      if (count > 0) {{
        selectedGrpNames.push(g.group + " (" + count + ")");
      }}
    }});

    catNameDisplay.textContent = selectedGrpNames.join(", ");
    btnFetch.textContent = "Fetch (" + selectedSubIds.size + ") ⚡";
    btnFetch.title = "Fetch " + selectedSubIds.size + " selected subcategories";
  }}

  function updateDeptBadge(grp) {{
    var deptEl = catDrawer.querySelector(`.fkd-dept-item[data-grp-id="${{grp.id}}"]`);
    if (!deptEl) return;
    var badge = deptEl.querySelector(".fkd-dept-badge");
    if (!badge) return;
    var count = (grp.subs || []).filter(function(s){{ return selectedSubIds.has(s.id); }}).length;
    if (count > 0) {{
      badge.textContent = count + " selected";
      badge.classList.remove("hidden");
    }} else {{
      badge.textContent = "";
      badge.classList.add("hidden");
    }}
  }}

  function toggleSubcategory(sub, grp, pillEl) {{
    if (selectedSubIds.has(sub.id)) {{
      selectedSubIds.delete(sub.id);
      pillEl.classList.remove("active");
      var hasOther = (grp.subs || []).some(function(s){{ return selectedSubIds.has(s.id); }});
      if (!hasOther) {{
        selectedParentGroups.delete(grp.id);
      }}
    }} else {{
      if (!selectedParentGroups.has(grp.id) && selectedParentGroups.size >= 2) {{
        showToast("⚠️ Select subcategories from up to 2 departments only. Clear one first!");
        return;
      }}
      selectedSubIds.add(sub.id);
      selectedParentGroups.add(grp.id);
      pillEl.classList.add("active");
    }}
    updateDeptBadge(grp);
    updateCategorySummary();
  }}

  function selectAllInDept(grp) {{
    if (!selectedParentGroups.has(grp.id) && selectedParentGroups.size >= 2) {{
      showToast("⚠️ Select subcategories from up to 2 departments only. Clear one first!");
      return;
    }}
    selectedParentGroups.add(grp.id);
    (grp.subs || []).forEach(function(sub) {{
      if (!sub.isOptin) {{
        selectedSubIds.add(sub.id);
        var p = catDrawer.querySelector(`.fkd-sub-pill[data-sub-id="${{sub.id}}"]`);
        if (p) p.classList.add("active");
      }}
    }});
    updateDeptBadge(grp);
    updateCategorySummary();
  }}

  function clearDept(grp) {{
    (grp.subs || []).forEach(function(sub) {{
      selectedSubIds.delete(sub.id);
      var p = catDrawer.querySelector(`.fkd-sub-pill[data-sub-id="${{sub.id}}"]`);
      if (p) p.classList.remove("active");
    }});
    selectedParentGroups.delete(grp.id);
    updateDeptBadge(grp);
    updateCategorySummary();
  }}

  /* Render Drawer: Top Quick Scan Box + Department Accordions with Pills */
  catDrawer.innerHTML = `
    <div class="fkd-quick-scan-box">
      <button type="button" class="fkd-quick-scan-btn" id="fkd-btn-quick-scan">
        ⚡ Quick Scan (All 18 Departments)
      </button>
      <div class="fkd-quick-scan-sub">Scans top store departments with 1 click</div>
    </div>
    <div class="fkd-drawer-hint">
      <span>Or pick subcategories (max 2 departments):</span>
      <button type="button" class="fkd-link-btn" id="fkd-btn-clear-all" style="font-size:10.5px;">Clear All</button>
    </div>
  `;

  var btnDrawerQuickScan = d.getElementById("fkd-btn-quick-scan");
  btnDrawerQuickScan.onclick = function(e) {{
    e.stopPropagation();
    closeCatDrawer();
    startFetch(true);
  }};

  var btnClearAll = d.getElementById("fkd-btn-clear-all");
  btnClearAll.onclick = function(e) {{
    e.stopPropagation();
    selectedSubIds.clear();
    selectedParentGroups.clear();
    catDrawer.querySelectorAll(".fkd-sub-pill.active").forEach(function(p){{ p.classList.remove("active"); }});
    catDrawer.querySelectorAll(".fkd-dept-badge").forEach(function(b){{ b.classList.add("hidden"); b.textContent = ""; }});
    updateCategorySummary();
  }};

  CATEGORY_TREE.forEach(function(item) {{
    var deptEl = d.createElement("div");
    deptEl.className = "fkd-dept-item";
    deptEl.dataset.grpId = item.id;

    var headerRow = d.createElement("div");
    headerRow.className = "fkd-dept-header";

    var chevron = d.createElement("span");
    chevron.className = "fkd-dept-chevron";
    chevron.textContent = "›";

    var nameSpan = d.createElement("span");
    nameSpan.className = "fkd-dept-name";
    nameSpan.textContent = item.name;

    var badge = d.createElement("span");
    badge.className = "fkd-dept-badge hidden";

    headerRow.appendChild(chevron);
    headerRow.appendChild(nameSpan);
    headerRow.appendChild(badge);
    deptEl.appendChild(headerRow);

    var subPanel = d.createElement("div");
    subPanel.className = "fkd-sub-panel collapsed";

    var toolbar = d.createElement("div");
    toolbar.className = "fkd-sub-toolbar";

    var btnSelectAll = d.createElement("button");
    btnSelectAll.type = "button";
    btnSelectAll.className = "fkd-link-btn";
    btnSelectAll.textContent = "Select All";

    var sep = d.createElement("span");
    sep.className = "fkd-toolbar-sep";
    sep.textContent = "•";

    var btnClearDept = d.createElement("button");
    btnClearDept.type = "button";
    btnClearDept.className = "fkd-link-btn";
    btnClearDept.textContent = "Clear";

    toolbar.appendChild(btnSelectAll);
    toolbar.appendChild(sep);
    toolbar.appendChild(btnClearDept);
    subPanel.appendChild(toolbar);

    var pillsWrap = d.createElement("div");
    pillsWrap.className = "fkd-pills-wrap";

    (item.subs || []).forEach(function(sub) {{
      var pill = d.createElement("button");
      pill.type = "button";
      pill.className = "fkd-sub-pill" + (selectedSubIds.has(sub.id) ? " active" : "");
      pill.dataset.subId = sub.id;
      pill.textContent = sub.name;

      pill.onclick = function(e) {{
        e.stopPropagation();
        toggleSubcategory(sub, item, pill);
      }};

      pillsWrap.appendChild(pill);
    }});

    subPanel.appendChild(pillsWrap);
    deptEl.appendChild(subPanel);

    headerRow.onclick = function(e) {{
      e.stopPropagation();
      var isCol = subPanel.classList.contains("collapsed");
      if (isCol) {{
        subPanel.classList.remove("collapsed");
        chevron.classList.add("expanded");
        chevron.textContent = "▾";
      }} else {{
        subPanel.classList.add("collapsed");
        chevron.classList.remove("expanded");
        chevron.textContent = "›";
      }}
    }};

    btnSelectAll.onclick = function(e) {{
      e.stopPropagation();
      selectAllInDept(item);
    }};

    btnClearDept.onclick = function(e) {{
      e.stopPropagation();
      clearDept(item);
    }};

    catDrawer.appendChild(deptEl);
  }});

  /* Close drawer when clicking outside inside sidebar */
  sb.addEventListener("click", function(e){{
    if (catDrawer && !catDrawer.contains(e.target) && !catToggle.contains(e.target)) {{
      closeCatDrawer();
    }}
  }});

  var btnToggleOos = d.getElementById("fkd-toggle-oos");
  var btnMin = d.getElementById("fkd-btn-min");
  var btnClose = d.getElementById("fkd-btn-close");
  var btnSortDisc = d.getElementById("fkd-sort-disc");
  var btnSortPrice = d.getElementById("fkd-sort-price");
  var btnFetch = d.getElementById("fkd-btn-fetch");
  var inputSearch = d.getElementById("fkd-input-search");
  var btnSearch = d.getElementById("fkd-btn-search");
  var grid = d.getElementById("fkd-grid");
  var statusMsg = d.getElementById("fkd-status-msg");
  var headCount = d.getElementById("fkd-head-count");
  var pillCount = d.getElementById("fkd-pill-count");

  function setStatus(txt) {{
    if (statusMsg) statusMsg.textContent = txt;
  }}

  function toggleCollapse(collapsed) {{
    st.isCollapsed = collapsed;
    if (collapsed) {{
      sb.classList.add("collapsed");
      pill.classList.remove("hidden");
    }} else {{
      sb.classList.remove("collapsed");
      pill.classList.add("hidden");
    }}
  }}

  function stopAll() {{
    window.fkDealsStop = true;
    st.mode = "STOPPED";
    btnFetch.className = "fkd-pill fkd-pill-action";
    if (selectedSubIds.size === 0) {{
      btnFetch.textContent = "Quick Scan ⚡";
    }} else {{
      btnFetch.textContent = `Fetch (${{selectedSubIds.size}}) ⚡`;
    }}
    if (btnSearch) {{
      btnSearch.textContent = "Search";
      btnSearch.className = "fkd-btn-search";
    }}
  }}

  btnSearch.onclick = function() {{
    if (st.mode === "RUN") {{
      stopAll();
      setStatus("Stopped (" + st.items.length + " items)");
    }} else {{
      startSearch(inputSearch.value);
    }}
  }};

  inputSearch.onkeydown = function(e) {{
    if (e.key === "Enter") {{
      if (st.mode === "RUN") {{
        stopAll();
      }}
      startSearch(inputSearch.value);
    }}
  }};

  btnMin.onclick = function() {{ toggleCollapse(true); }};
  pill.onclick = function() {{ toggleCollapse(false); }};

  btnClose.onclick = function() {{
    stopAll();
    sb.remove();
    pill.remove();
    style.remove();
  }};

  btnSortPrice.onclick = function() {{
    st.sort = "price_asc";
    btnSortPrice.classList.add("active");
    btnSortDisc.classList.remove("active");
    renderGrid();
  }};

  btnSortDisc.onclick = function() {{
    st.sort = "discount";
    btnSortDisc.classList.add("active");
    btnSortPrice.classList.remove("active");
    renderGrid();
  }};

  btnToggleOos.onclick = function() {{
    st.hideOos = !st.hideOos;
    if (st.hideOos) {{
      btnToggleOos.classList.add("active");
      btnToggleOos.textContent = "In Stock";
    }} else {{
      btnToggleOos.classList.remove("active");
      btnToggleOos.textContent = "All Items";
    }}
    renderGrid();
  }};

  btnFetch.onclick = function() {{
    closeCatDrawer();
    if (st.mode === "RUN") {{
      stopAll();
      setStatus("Stopped (" + st.items.length + " items)");
    }} else {{
      startFetch(selectedSubIds.size === 0);
    }}
  }};

    function renderGrid() {{
    grid.innerHTML = "";
    var filtered = st.items.filter(function(it){{
      if (st.hideOos && it.oos) return false;
      return true;
    }});

    if (st.sort === "discount") {{
      filtered.sort(function(a, b){{ return b.d - a.d; }});
    }} else {{
      filtered.sort(function(a, b){{ return a.f - b.f; }});
    }}

    var inStockCount = filtered.filter(function(x){{ return !x.oos; }}).length;
    var oosCount = filtered.length - inStockCount;
    headCount.textContent = st.hideOos
      ? `${{filtered.length}} Deals (${{inStockCount}} In Stock)`
      : `${{filtered.length}} Deals (${{inStockCount}} In Stock, ${{oosCount}} OOS)`;
    pillCount.textContent = filtered.length;

    if (!filtered.length) {{
      grid.innerHTML = `<div class="fkd-empty">${{st.items.length ? 'No items match current criteria.<br><br>(Total scanned: ' + st.items.length + (st.hideOos ? ', Out of stock hidden' : '') + ')' : 'No deals loaded yet. Click <b>Quick Scan ⚡</b> or select categories.'}}</div>`;
      return;
    }}

    filtered.forEach(function(it){{
      var card = d.createElement("div");
      card.className = "fkd-card" + (it.oos ? " oos" : "");
      var safeTitle = escapeHtml(it.t);
      var safeImg = escapeHtml(it.i);
      card.innerHTML = `
        <div class="fkd-img-box">
          <img src="${{safeImg}}" class="fkd-img" loading="lazy" onerror="this.src='https://rukminim1.flixcart.com/flap/200/200/image/placeholder.png'">
          ${{it.d > 0 ? `
            <div class="fkd-disc-tag">
              <span class="fkd-disc-pct">${{it.d}}%</span>
              <span class="fkd-disc-off">OFF</span>
            </div>
          ` : ''}}
          ${{it.oos ? `<div class="fkd-oos-tag">OUT OF STOCK</div>` : ''}}
        </div>
        <div class="fkd-card-title" title="${{safeTitle}}">${{safeTitle}}</div>
        <div class="fkd-price-row">
          <span class="fkd-price">₹${{it.f}}</span>
          ${{it.m > it.f ? `<span class="fkd-mrp">₹${{it.m}}</span>` : ''}}
        </div>
      `;
      card.onclick = function() {{
        if (it.l) window.open(it.l, "_blank");
      }};
      grid.appendChild(card);
    }});
  }}

  /* Recursively extracts integer price from any Rome label structure, dict, or string */
  function extractPrice(val) {{
    if (!val) return 0;
    if (typeof val === "number") return Math.round(val);
    if (typeof val === "string") {{
      var m = val.replace(/,/g, "").match(/\\d+/);
      return m ? parseInt(m[0], 10) : 0;
    }}
    if (typeof val === "object") {{
      if (val.text !== undefined && val.text !== null) {{
        var p = extractPrice(val.text);
        if (p > 0) return p;
      }}
      if (val.defaultValue !== undefined && val.defaultValue !== null) {{
        var p2 = extractPrice(val.defaultValue);
        if (p2 > 0) return p2;
      }}
      if (val.params && typeof val.params === "object") {{
        var p3 = extractPrice(val.params.defaultValue || val.params.price);
        if (p3 > 0) return p3;
      }}
      if (val.value !== undefined && val.value !== null) {{
        var p4 = extractPrice(val.value);
        if (p4 > 0) return p4;
      }}
      if (val.UNLOCKED) {{
        var p5 = extractPrice(val.UNLOCKED);
        if (p5 > 0) return p5;
      }}
      if (val.LOCKED) {{
        var p6 = extractPrice(val.LOCKED);
        if (p6 > 0) return p6;
      }}
      if (val.tracking && typeof val.tracking === "object") {{
        var p7 = extractPrice(val.tracking.fsp || val.tracking.mrp);
        if (p7 > 0) return p7;
      }}
    }}
    return 0;
  }}

  function addProduct(title, fsp, mrp, disc, img, lnk, isOos, minKeep) {{
    if (!fsp) return false;
    fsp = parseInt(fsp, 10);
    if (isNaN(fsp) || fsp <= 0) return false;

    /* Clean fallback for generic or missing title */
    if (!title || title === "Product" || title.length < 3) {{
      var urlTitle = extractTitleFromUrl(lnk);
      title = urlTitle || title || "Product";
    }}

    var tLower = (title || "").toLowerCase();

    /* Phone Case / Cover Filter for Electronics & Gadgets */
    if (!st.allowPhoneCases) {{
      if (/\\b(back\\s*cover|phone\\s*case|tempered\\s*glass|camera\\s*lens\\s*protector|screen\\s*protector|mobile\\s*pouch|silicone\\s*case|flip\\s*cover|mobile\\s*skin|bumper\\s*case)\\b/i.test(tLower)) {{
        return false;
      }}
      if (/\\b(cover|case|glass|protector|pouch|sleeve|skin)\\b/i.test(tLower) &&
          /\\b(iphone|galaxy|samsung|redmi|oneplus|realme|vivo|oppo|pixel|moto|xiaomi|iqoo|apple|ipad|airpods)\\b/i.test(tLower)) {{
        return false;
      }}
    }}

    /* Negative keyword & brand filtration (Junk prevention) */
    for (var k = 0; k < EXCLUDED_KEYWORDS.length; k++) {{
      if (tLower.includes(EXCLUDED_KEYWORDS[k])) return false;
    }}
    /* Religious brands exclusion (starts with reli... except relish) */
    var words = tLower.match(/\b[a-z]+/g) || [];
    for (var w = 0; w < words.length; w++) {{
      if (words[w].startsWith("reli") && !words[w].startsWith("relish")) return false;
    }}
    for (var b = 0; b < EXCLUDED_BRANDS.length; b++) {{
      var eb = EXCLUDED_BRANDS[b].toLowerCase();
      if (tLower.startsWith(eb + " ") || tLower.includes(" by " + eb) || tLower === eb || tLower.includes(" " + eb + " ")) return false;
    }}

    mrp = mrp ? parseInt(mrp, 10) : fsp;
    if (isNaN(mrp) || mrp <= 0) mrp = fsp;

    /* Selling price is ALWAYS <= MRP. If swapped, correct them */
    if (fsp > mrp) {{
      var tmp = fsp;
      fsp = mrp;
      mrp = tmp;
    }}

    /* Derive MRP if discount given but MRP missing */
    if (disc > 0 && disc < 100 && fsp === mrp) {{
      mrp = Math.round(fsp / (1 - disc / 100));
    }}

    /* Normalize discount percentage (0 to 99) */
    if (disc === undefined || isNaN(disc) || disc > 99 || disc <= 0) {{
      disc = (mrp > fsp) ? Math.round(((mrp - fsp) / mrp) * 100) : 0;
    }}

    /* Bug Fix: Concatenated MRP and Discount */
    if (mrp > fsp * 4 && disc > 0 && String(mrp).endsWith(String(disc))) {{
      var cleanMrp = parseInt(String(mrp).slice(0, -String(disc).length), 10);
      if (cleanMrp >= fsp) {{
        mrp = cleanMrp;
        disc = Math.round(((mrp - fsp) / mrp) * 100);
      }}
    }}

    /* Min keep check: for Page 2+, items below threshold (50% or 40% for Staples) are dropped */
    if (minKeep && disc < minKeep) return false;

    /* Brand-specific high thresholds (e.g. 13 junk home brands gated at 90%) */
    var isSearchMode = !!(st.searchQuery && st.searchQuery.trim().length > 0);
    if (!isSearchMode) {{
      for (var bt in BRAND_THRESHOLDS) {{
        if (tLower.startsWith(bt + " ") || tLower.includes(" by " + bt) || tLower === bt || tLower.includes(" " + bt + " ")) {{
          if (disc < BRAND_THRESHOLDS[bt]) return false;
          break;
        }}
      }}
    }}

      /* Ensure deal links open directly in Flipkart Minutes */
    if (lnk && !lnk.includes("marketplace=HYPERLOCAL")) {{
      lnk += (lnk.includes("?") ? "&" : "?") + "marketplace=HYPERLOCAL";
    }}

    /* Robust UID: extract Flipkart PID from product URL, fallback to normalized title + price */
    var pid = "";
    if (lnk) {{
      var mPid = lnk.match(/[?&]pid=([a-zA-Z0-9_-]+)/i);
      if (mPid && mPid[1]) {{
        pid = mPid[1];
      }} else {{
        var mItm = lnk.match(/\\/p\\/(itm[a-zA-Z0-9_-]+)/i);
        if (mItm && mItm[1]) pid = mItm[1];
      }}
    }}
    var normTitle = (title || "").toLowerCase().replace(/\\s+/g, " ").trim();
    var uid = pid ? ("pid_" + pid) : (normTitle + "_" + fsp);

    if (!st.seen.has(uid)) {{
      st.seen.add(uid);
      st.items.push({{ t: title, f: fsp, m: mrp, d: disc, i: img, l: lnk, oos: !!isOos }});
      return true;
    }}
    return false;
  }}

  /* Parse products from Rome API JSON structure */
  function parseProducts(json, minKeep) {{
    var count = 0;
    var pageDiscounts = [];
    var count = 0;
    if (!json) return count;
    var slots = json.RESPONSE?.slots || json.slots || json.pageData?.slots || json.multiWidgetState?.widgetsData?.slots || json.multiWidgetState?.pageDataResponse?.slots || [];
    slots.forEach(function(s){{
      var slotObj = s.slotData || s;
      var w = slotObj.widget || slotObj;
      var wdata = w.data || {{}};

      /* 1. Standard Product Summaries */
      var comps = wdata.products || wdata.renderableComponents || [];
      comps.forEach(function(item){{
        try {{
          var pinfo = item.productInfo || item;
          var v = pinfo.value || pinfo;
          if (v && v.pricing && v.pricing.finalPrice) {{
            var fsp = extractPrice(v.pricing.finalPrice.value);
            var mrp = fsp;
            if (v.pricing.prices) {{
              var mrpObj = v.pricing.prices.find(function(x){{ return x.priceType === "MRP"; }});
              if (mrpObj) mrp = extractPrice(mrpObj.value) || mrp;
            }}
            if (mrp === fsp && v.pricing.mrp) {{
              mrp = extractPrice(v.pricing.mrp) || mrp;
            }}
            if (fsp && mrp && fsp > mrp) {{
              var t = fsp; fsp = mrp; mrp = t;
            }}
            var disc = v.pricing.totalDiscount;
            var lnk = v.baseUrl ? ("https://www.flipkart.com" + v.baseUrl) : (v.smartUrl ? ("https://www.flipkart.com" + v.smartUrl) : "");
            var title = v.titles?.title || v.titles?.newTitle || v.titles?.superTitle || v.productTitle || extractTitleFromUrl(lnk) || "Product";
            var img = v.media?.images?.[0]?.url || v.images?.[0]?.url || "";
            img = img.replace("{{@width}}", "200").replace("{{@height}}", "200").replace("?q={{@quality}}", "?q=80");

            var isOos = (v.availability?.displayState === "OUT_OF_STOCK") ||
                        (v.productAction?.value?.enabled === false) ||
                        (v.productAction?.value?.actionType === "NOTIFY_ME") ||
                        (v.buyability?.intent === "negative") ||
                        (v.action?.params?.isAvailable === false) ||
                        (v.availability && v.availability.displayState && v.availability.displayState !== "IN_STOCK");

            pageDiscounts.push(disc || 0); if (addProduct(title, fsp, mrp, disc, img, lnk, isOos, minKeep)) count++;
          }}
        }} catch (e) {{}}
      }});

      /* 2. DLS / Atlas Recommendation & Search Grid Widgets */
      var dls = wdata.dlsData || {{}};
      for (var k in dls) {{
        if (k.indexOf("MRCSV") !== -1 || k.indexOf("carouselData") !== -1 || k.indexOf("gridData") !== -1 || k.indexOf("horizontalListData") !== -1) {{
          var cardList = dls[k]?.value || [];
          if (Array.isArray(cardList)) {{
            cardList.forEach(function(cardWrapper){{
              try {{
                var cval = cardWrapper?.value || {{}};

                /* Case A: ATLAS Search & Grid Cards (snb_hl_text_0) */
                if (cval.snb_hl_text_0?.value) {{
                  var snbText = cval.snb_hl_text_0.value;
                  var lnk = cval.col_0?.action?.url || cval.col_0?.action?.originalUrl || "";
                  if (lnk && !lnk.startsWith("http")) lnk = "https://www.flipkart.com" + lnk;

                  var title = snbText.label_0?.value?.text || snbText.label_1?.value?.text || cval.trackerData_0?.tracking?.contentTitle || extractTitleFromUrl(lnk) || "Product";

                  var stepper = cval.stepperData_0?.action || cval.snb_beauty_gmh_image_0?.value?.stepperData_0?.action;
                  var p1 = extractPrice(snbText.label_4);
                  var p2 = extractPrice(snbText.label_3);
                  if (!p1 && stepper) {{
                    p1 = extractPrice(stepper.params?.price || stepper.tracking?.fsp);
                  }}
                  if (!p2 && stepper) {{
                    p2 = extractPrice(stepper.tracking?.mrp);
                  }}

                  var fsp = 0;
                  var mrp = 0;
                  if (p1 && p2) {{
                    fsp = Math.min(p1, p2);
                    mrp = Math.max(p1, p2);
                  }} else {{
                    fsp = p1 || p2 || 0;
                    mrp = fsp;
                  }}

                  var disc = 0;
                  var l2 = snbText.label_2?.value;
                  var l2Val = (typeof l2 === "object") ? (l2.params?.defaultValue || l2.text || "") : String(l2 || "");
                  var matchDisc = l2Val.match(/(\\d+)%/);
                  if (matchDisc) {{
                    disc = parseInt(matchDisc[1], 10);
                  }} else if (mrp > fsp) {{
                    disc = Math.round(((mrp - fsp) / mrp) * 100);
                  }}

                  var isOos = (stepper?.tracking?.isAvailable === "false") || (stepper?.enabled === false) || (cval.action?.params?.isAvailable === false);

                  var img = cval.col_0?.action?.params?.imageUrl || stepper?.params?.productImage || "";
                  if (!img) {{
                    var imgObj = cval.image_0?.value || cval.snb_beauty_gmh_image_0?.value?.image_0?.value;
                    img = imgObj?.params?.defaultValue || imgObj?.imageHack || imgObj?.dynamicImageUrl || "";
                  }}
                  img = img.replace("{{@width}}", "200").replace("{{@height}}", "200").replace("?q={{@quality}}", "?q=80");

                  pageDiscounts.push(disc || 0); if (fsp && addProduct(title, fsp, mrp, disc, img, lnk, isOos, minKeep)) count++;
                  return;
                }}

                /* Case B: MRCSV / Product Cards */
                var pcard = null;
                for (var pk in cval) {{
                  if (pk.indexOf("product-card") !== -1 || pk.indexOf("productCard") !== -1) {{
                    pcard = cval[pk]?.value || {{}};
                    break;
                  }}
                }}
                if (pcard) {{
                  var stepperAction = pcard.stepperData_0?.action || {{}};
                  var stepperTracking = stepperAction.tracking || {{}};
                  var stepperFsp = extractPrice(stepperAction.params?.price || stepperTracking.fsp);
                  var stepperMrp = extractPrice(stepperTracking.mrp);
                  var l5Val = extractPrice(pcard.label_5);
                  var l4Val = extractPrice(pcard.label_4);

                  var pSell = stepperFsp || l5Val || 0;
                  var pMrp = stepperMrp || l4Val || 0;

                  var fsp = 0;
                  var mrp = 0;
                  if (pSell && pMrp) {{
                    fsp = Math.min(pSell, pMrp);
                    mrp = Math.max(pSell, pMrp);
                  }} else {{
                    fsp = pSell || pMrp || 0;
                    mrp = fsp;
                  }}

                  var disc = 0;
                  if (pcard.label_15?.value) {{
                    var l15 = pcard.label_15.value;
                    var l15Str = (typeof l15 === "object") ? (l15.UNLOCKED?.value?.text || l15.LOCKED?.value?.text || l15.text || "") : String(l15);
                    var discMatch = l15Str.match(/(\\d+)%/);
                    if (discMatch) disc = parseInt(discMatch[1], 10);
                  }} else if (mrp > fsp) {{
                    disc = Math.round(((mrp - fsp) / mrp) * 100);
                  }}

                  var lnk = "";
                  var b5 = pcard.box_5?.action?.url || pcard.col_0?.action?.url || pcard.box_0?.action?.url || "";
                  if (b5) lnk = "https://www.flipkart.com" + b5;

                  var title = pcard.label_2?.value?.text || pcard.label_1?.value?.text || pcard.label_0?.value?.text || pcard.trackerData_0?.tracking?.contentTitle || extractTitleFromUrl(lnk) || "Product";

                  var img = stepperAction.params?.productImage || "";
                  if (!img) {{
                    var imgObj = pcard["hp_reco_pmu_product-card_image_0"]?.value || {{}};
                    img = imgObj.image_0?.value?.dynamicImageUrl || imgObj.video_0?.value?.dynamicImageUrl || "";
                  }}
                  img = img.replace("{{@width}}", "200").replace("{{@height}}", "200").replace("?q={{@quality}}", "?q=80");

                  var isOos = (stepperAction.enabled === false) || (pcard.button_0?.value?.actionType === "NOTIFY_ME") || (pcard.button_0?.value?.text && /notify/i.test(pcard.button_0.value.text));
                  pageDiscounts.push(disc || 0); if (fsp && addProduct(title, fsp, mrp, disc, img, lnk, isOos, minKeep)) count++;
                }}
              }} catch (err) {{}}
            }});
          }}
        }}
      }}
    }});
    var tailDisc = pageDiscounts.length ? pageDiscounts[pageDiscounts.length - 1] : 0;
    return {{ count: count, tailDiscount: tailDisc, totalFound: pageDiscounts.length }};
  }}

  /* Scrape items from DOM */
  function parseDomProducts(rootDoc, minKeep) {{
    var doc = rootDoc || document;
    var count = 0;
    var pageDiscounts = [];
    var doc = rootDoc || document;
    var count = 0;
    var anchors = doc.querySelectorAll('a[href*="/p/itm"], a[href*="/p/"], a[href*="pid="]');
    var processedCards = new Set();

    anchors.forEach(function(a){{
      try {{
        var href = a.getAttribute("href") || "";
        if (!href || href.includes("javascript:") || href.length < 5) return;
        if (!href.startsWith("http")) href = "https://www.flipkart.com" + href;

        var card = a.closest('[data-id], [class*="card" i], [class*="product" i], [class*="grid" i], [class*="_1AtVbE"]') || a.parentElement;
        var cardKey = (card && card.getAttribute && card.getAttribute("data-id")) || href.split("?")[0];
        if (cardKey && processedCards.has(cardKey)) return;
        if (cardKey) processedCards.add(cardKey);

        var fsp = 0;
        var mrp = 0;
        var disc = 0;

        var fspEl = (card || a).querySelector('.hZ3P6w, ._30jeq3, .Nx9bqj');
        var mrpEl = (card || a).querySelector('.kRYCnD, ._3I9_wc, .yRaY8j');
        var discEl = (card || a).querySelector('.HQe8jr, ._3Ay6Sb');

        if (fspEl) {{
          var m1 = fspEl.innerText.replace(/[^\\d]/g, "");
          if (m1) fsp = parseInt(m1, 10);
        }}
        if (mrpEl) {{
          var m2 = mrpEl.innerText.replace(/[^\\d]/g, "");
          if (m2) mrp = parseInt(m2, 10);
        }}
        if (discEl) {{
          var m3 = discEl.innerText.match(/\\b([1-9][0-9]?)\\s*%/);
          if (m3) disc = parseInt(m3[1], 10);
        }}

        if (!fsp) {{
          var text = (card ? card.innerText : a.innerText) || "";
          text = text.replace(/save\\s*(?:extra\\s*)?(?:₹|\\u20b9)\\s*\\d+/gi, "")
                     .replace(/buy\\s*\\d+\\s*(?:items|get|for)[^₹\\n]*(?:₹|\\u20b9)\\s*\\d+/gi, "");

          text = text.replace(/(?:₹|\\u20b9)\\s*([0-9,]+?)(\\d{{1,2}})%\\s*off/gi, "₹$1 $2% off")
                     .replace(/([0-9])([0-9]{{2}}%)/g, "$1 $2")
                     .replace(/(?:₹|\\u20b9)\\s*([0-9,]+)(?=[0-9]{{2}}%)/g, "₹$1 ");

          var priceMatches = text.match(/(?:₹|\\u20b9)\\s*([0-9,]+)/g);
          if (!priceMatches || !priceMatches.length) return;

          var prices = priceMatches.map(function(p){{
            return parseInt(p.replace(/[^\\d]/g, ""), 10);
          }}).filter(function(n){{ return !isNaN(n) && n > 0; }});

          if (!prices.length) return;

          if (prices.length === 1) {{
            fsp = prices[0];
            mrp = fsp;
          }} else {{
            fsp = Math.min(prices[0], prices[1]);
            mrp = Math.max(prices[0], prices[1]);
          }}

          if (!disc) {{
            var discMatch = text.match(/\\b([1-9][0-9]?)\\s*%\\s*off/i);
            if (discMatch) disc = parseInt(discMatch[1], 10);
          }}
        }}

        var imgEl = (card || a).querySelector('img[src*="rukminim"], img[src*="flixcart"], img');
        var img = imgEl ? (imgEl.src || imgEl.getAttribute("src") || "") : "";

        var title = "";
        var titleEl = (card || a).querySelector('[class*="title" i], [class*="name" i], [class*="pIpigb"], [class*="wjcEIp"], [class*="s1Q9rs"], [class*="_4rR01T"], [class*="_2Wk75y"]');
        if (titleEl && titleEl.innerText && titleEl.innerText.trim().length > 3) {{
          title = titleEl.innerText.trim();
        }}
        if (!title && a.getAttribute("title")) {{
          title = a.getAttribute("title").trim();
        }}
        if (!title) {{
          var anyTitleA = (card || a).querySelector("a[title]");
          if (anyTitleA && anyTitleA.getAttribute("title")) {{
            title = anyTitleA.getAttribute("title").trim();
          }}
        }}
        if (!title && imgEl && imgEl.alt && imgEl.alt.length > 3) {{
          title = imgEl.alt.trim();
        }}
        if (!title) {{
          var cardText = (card ? card.innerText : a.innerText) || "";
          var lines = cardText.split("\\n").map(function(s){{ return s.trim(); }}).filter(Boolean);
          for (var i = 0; i < lines.length; i++) {{
            if (!lines[i].includes("₹") && !lines[i].includes("\\u20b9") && !lines[i].includes("%") && lines[i].length > 3) {{
              title = lines[i];
              break;
            }}
          }}
        }}
        if (!title || title === "Product") {{
          title = extractTitleFromUrl(href) || "Product";
        }}

        var isOos = /currently\\s*unavailable|unavailable|out\\s*of\\s*stock|sold\\s*out|notify\\s*me/i.test((card ? card.innerText : a.innerText) || "") ||
                    !!(card && card.querySelector('button[disabled], [class*="unavailable" i], [class*="outOfStock" i], [class*="notify" i], [aria-label*="notify" i]'));

        if (addProduct(title, fsp, mrp, disc, img, href, isOos)) count++;
      }} catch (e) {{}}
    }});
    var tailDisc = pageDiscounts.length ? pageDiscounts[pageDiscounts.length - 1] : 0;
    return {{ count: count, tailDiscount: tailDisc, totalFound: pageDiscounts.length }};
  }}

  /* Safe URI sanitizer */
  function sanitizePageUri(uri) {{
    if (!uri) return "";
    var u = uri.startsWith("http") ? uri.replace(/^https?:\\/\\/[^\\/]+/, "") : uri;
    return u.replace(/([?&]sid=)([^&]+)/gi, function(match, prefix, val) {{
      return prefix + val.replace(/\\//g, "%2F");
    }});
  }}

  /* Get user agent header */
  function getXUserAgent() {{
    var ua = navigator.userAgent || "";
    if (ua.includes("FKUA/msite")) return ua;
    return ua + " FKUA/msite/0.0.4/msite/Mobile";
  }}

  /* Get active pincode dynamically from session state, cookies, or storage */
  function getActivePincode() {{
    try {{
      if (window.__INITIAL_STATE__) {{
        var s = window.__INITIAL_STATE__;
        var pc = s.multiWidgetState?.pincode?.pincode || 
                 s.multiWidgetState?.pincode?.systemPincode ||
                 s.multiWidgetState?.appContext?.meta?.pc ||
                 s.pageDataResponse?.pageData?.pageContext?.pincode ||
                 s.pageData?.pageContext?.pincode;
        if (pc && /^[0-9]{{6}}$/.test(String(pc))) return parseInt(pc, 10);
      }}
    }} catch(e) {{}}
    try {{
      var m = document.cookie.match(/(?:^|;\\s*)(?:pincode|snPincode|deliveryPincode)=([0-9]{{6}})/i);
      if (m) return parseInt(m[1], 10);
    }} catch(e) {{}}
    try {{
      var stored = localStorage.getItem("pincode") || sessionStorage.getItem("pincode");
      if (stored && /^[0-9]{{6}}$/.test(stored)) return parseInt(stored, 10);
    }} catch(e) {{}}
    return 560032;
  }}

  /* Extract active session context */
  function getRequestContext() {{
    var ctx = {{ type: "BROWSE_PAGE" }};
    try {{
      if (window.__INITIAL_STATE__) {{
        var s = window.__INITIAL_STATE__;
        var rc = s.multiWidgetState?.pageDataResponse?.requestContext || 
                 s.pageDataResponse?.requestContext || 
                 s.requestContext;
        if (rc?.ssid) ctx.ssid = rc.ssid;
        if (rc?.sqid) ctx.sqid = rc.sqid;
      }}
    }} catch(e) {{}}
    return ctx;
  }}

  /* Fetch page data using Rome API */
  async function fetchRomePage(pageUri, redirectCount) {{
    if (!pageUri) return null;
    redirectCount = redirectCount || 0;
    if (redirectCount > 2) return null;

    var cleanUri = sanitizePageUri(pageUri);
    var bodyPayload = {{
      pageUri: cleanUri,
      pageContext: {{
        trackingContext: {{
          context: {{
            eVar51: "neo/merchandising",
            eVar61: "creative_card"
          }}
        }},
        networkSpeed: 1700
      }},
      requestContext: getRequestContext(),
      locationContext: {{
        pincode: getActivePincode(),
        changed: false
      }}
    }};

    try {{
      var resp = await fetch("https://1.rome.api.flipkart.com/api/4/page/fetch?cacheFirst=false", {{
        headers: {{
          "accept": "*/*",
          "accept-language": "en-US,en;q=0.9",
          "content-type": "application/json",
          "flipkart_secure": "true",
          "x-user-agent": getXUserAgent()
        }},
        body: JSON.stringify(bodyPayload),
        method: "POST",
        mode: "cors",
        credentials: "include"
      }});
      if (resp.ok) {{
        var json = await resp.json();
        var slots = json.RESPONSE?.slots || json.slots || [];
        var redir = json.RESPONSE?.pageMeta?.redirectionObject || json.pageMeta?.redirectionObject;
        if ((!slots || slots.length === 0) && redir && redir.url) {{
          var targetPath = redir.url;
          if (targetPath.startsWith("http")) {{
            try {{
              var parsedUrl = new URL(targetPath);
              targetPath = parsedUrl.pathname + parsedUrl.search;
            }} catch(e) {{
              targetPath = targetPath.replace(/^https?:\\/\\/[^\\/]+/, "");
            }}
          }}
          if (targetPath && targetPath !== cleanUri) {{
            var redirectedJson = await fetchRomePage(targetPath, redirectCount + 1);
            if (redirectedJson) return redirectedJson;
          }}
        }}
        return json;
      }}
    }} catch(e) {{}}
    return null;
  }}

  /* Fetch full HTML of any Flipkart page with session cookies (fallback) */
  async function fetchCategoryHtml(uri) {{
    var cleanUri = sanitizePageUri(uri);
    var url = cleanUri.startsWith("http") ? cleanUri : ("https://www.flipkart.com" + cleanUri);
    try {{
      var resp = await fetch(url, {{
        method: "GET",
        credentials: "include"
      }});
      if (!resp.ok) return null;
      return await resp.text();
    }} catch(e) {{
      return null;
    }}
  }}

  /* Extract __INITIAL_STATE__ JSON reliably without regex backtracking */
  function extractStateJsonFromHtml(html) {{
    if (!html) return null;
    var startIdx = html.indexOf("window.__INITIAL_STATE__");
    if (startIdx === -1) return null;
    var jsonStart = html.indexOf("{{", startIdx);
    if (jsonStart === -1) return null;
    var scriptEnd = html.indexOf("</script>", jsonStart);
    if (scriptEnd === -1) return null;
    var jsonEnd = html.lastIndexOf("}}", scriptEnd);
    if (jsonEnd <= jsonStart) return null;
    try {{
      return JSON.parse(html.substring(jsonStart, jsonEnd + 1));
    }} catch(e) {{
      return null;
    }}
  }}

  /* Parse products from raw HTML text */
  function parseHtmlString(html, minKeep) {{
    if (!html) return {{ count: 0, tailDiscount: 0, totalFound: 0 }};
    try {{
      var json = extractStateJsonFromHtml(html);
      if (json) {{
        var r = parseProducts(json, minKeep);
        if (r && r.totalFound > 0) return r;
      }}
    }} catch(e) {{}}

    try {{
      var parser = new DOMParser();
      var doc = parser.parseFromString(html, "text/html");
      return parseDomProducts(doc, minKeep);
    }} catch(e) {{}}

    return {{ count: 0, tailDiscount: 0, totalFound: 0 }};
  }}

  /* Unified page fetcher */
  async function fetchAndParsePage(uri, minKeep) {{
    if (!uri) return {{ count: 0, tailDiscount: 0, totalFound: 0 }};
    minKeep = minKeep || 0;
    // 1. Same-origin HTML fetch with session cookies
    var html = await fetchCategoryHtml(uri);
    if (html) {{
      var r1 = parseHtmlString(html, minKeep);
      if (r1 && r1.totalFound > 0) return r1;
    }}
    // 2. Fallback: Rome API with credentials included
    var json = await fetchRomePage(uri);
    if (json) {{
      var r2 = parseProducts(json, minKeep);
      if (r2 && r2.totalFound > 0) return r2;
    }}
    return {{ count: 0, tailDiscount: 0, totalFound: 0 }};
  }}

  /* Search Flipkart Minutes via unified fetcher */
  async function startSearch(query) {{
    if (!query || !query.trim()) {{
      setStatus("Enter search keyword");
      return;
    }}
    query = query.trim();
    st.searchQuery = query;
    st.allowPhoneCases = true;
    window.fkDealsStop = false;
    st.mode = "RUN";
    if (btnSearch) {{
      btnSearch.textContent = "Stop ⏹";
      btnSearch.className = "fkd-btn-search";
      btnSearch.style.background = "#DC2626";
      btnSearch.style.borderColor = "#DC2626";
    }}

    st.items = [];
    st.seen.clear();
    renderGrid();

    setStatus(`Searching "${{query}}"...`);
    var sortParam = (st.sort === "discount") ? "&sort=discount" : "&sort=price_asc";
    var searchUri = "/hyperlocal/pr?q=" + encodeURIComponent(query) + "&marketplace=HYPERLOCAL&searchSourceContext=experience%3D&widgetUniqueId=1&sid=search.flipkart.com&as-show=on" + sortParam;

    var res1 = await fetchAndParsePage(searchUri, 0);
    renderGrid();

    if (st.mode === "RUN" && !window.fkDealsStop && res1 && res1.totalFound >= 6 && res1.tailDiscount >= 50) {{
      setStatus(`Loading more "${{query}}"...`);
      var p2Uri = searchUri + "&page=2";
      await fetchAndParsePage(p2Uri, 50);
      renderGrid();
    }}

    stopAll();
    var finalIn = st.items.filter(function(x){{ return !x.oos; }}).length;
    setStatus(`Search done! ${{st.items.length}} items (${{finalIn}} in stock)`);
  }}

  /* Multi-Category Scanning based on checked categories */
  async function startFetch(forceQuickScan) {{
    closeCatDrawer();
    st.searchQuery = "";
    if (inputSearch) inputSearch.value = "";
    window.fkDealsStop = false;
    st.mode = "RUN";
    btnFetch.textContent = "Stop ⏹";
    btnFetch.className = "fkd-pill fkd-pill-danger";

    st.items = [];
    st.seen.clear();
    renderGrid();

    // Check if phone cases allowed (opt-in)
    st.allowPhoneCases = Array.from(selectedSubIds).some(function(id){{
      return id.includes("0040") || id.includes("sgh_jaa");
    }});

    var isQuick = !!forceQuickScan || (selectedSubIds.size === 0);
    var endpoints = [];

    if (isQuick) {{
      endpoints = MAIN_GROUPS.map(function(mg) {{
        return {{
          name: mg.name,
          uri: mg.uri,
          isStaples: (mg.group === "Staples")
        }};
      }});
      setStatus(`Quick Scan across ${{endpoints.length}} top departments...`);
    }} else {{
      CATEGORY_TREE.forEach(function(grp) {{
        (grp.subs || []).forEach(function(sub) {{
          if (selectedSubIds.has(sub.id)) {{
            endpoints.push({{
              name: grp.name + " › " + sub.name,
              uri: sub.uri,
              isStaples: (grp.group === "Staples")
            }});
          }}
        }});
      }});
      setStatus(`Scanning ${{endpoints.length}} selected subcategories...`);
    }}

    if (!endpoints.length) {{
      stopAll();
      setStatus("No categories to scan");
      return;
    }}

    var totalEps = endpoints.length;
    var completedCount = 0;
    var epIndex = 0;
    var CONCURRENCY = Math.min(3, totalEps);

    async function scanWorker() {{
      while (epIndex < totalEps) {{
        if (st.mode !== "RUN" || window.fkDealsStop) break;
        var myIdx = epIndex++;
        var ep = endpoints[myIdx];
        setStatus(`[${{completedCount + 1}}/${{totalEps}}] ${{ep.name.trim()}}...`);
        var pUri = ep.uri;
        if (!pUri.includes("sort=discount")) {{
          pUri += (pUri.includes("?") ? "&" : "?") + "sort=discount";
        }}

        // Requirements 5 & 6:
        // Staples threshold = 40%
        // Other departments threshold = 50%
        var threshold = ep.isStaples ? 40 : 50;

        // Page 1 is ALWAYS fetched and displayed (minDiscKeep = 0)
        var res1 = await fetchAndParsePage(pUri, 0);
        completedCount++;
        renderGrid();

        // If Page 1 ends with discount >= threshold, fetch Page 2!
        // Stop when the last row items of the page is less than threshold
        if (st.mode === "RUN" && !window.fkDealsStop && res1 && res1.totalFound >= 6 && res1.tailDiscount >= threshold) {{
          var p2Uri = pUri + (pUri.includes("?") ? "&" : "?") + "page=2&sort=discount";
          var res2 = await fetchAndParsePage(p2Uri, threshold);
          renderGrid();

          // If Page 2 also ends with discount >= threshold, can fetch Page 3
          if (st.mode === "RUN" && !window.fkDealsStop && res2 && res2.totalFound >= 6 && res2.tailDiscount >= threshold) {{
            var p3Uri = pUri + (pUri.includes("?") ? "&" : "?") + "page=3&sort=discount";
            await fetchAndParsePage(p3Uri, threshold);
            renderGrid();
          }}
        }}
        await new Promise(function(r){{ setTimeout(r, 100); }});
      }}
    }}

    var workers = [];
    for (var w = 0; w < CONCURRENCY; w++) {{
      workers.push(scanWorker());
    }}
    await Promise.all(workers);

    stopAll();
    var finalIn = st.items.filter(function(x){{ return !x.oos; }}).length;
    setStatus(`Done! Found ${{st.items.length}} deals (${{finalIn}} in stock)`);
  }}

    /* Initialize */
  updateCategorySummary();
  setStatus("Ready - Click Fetch ⚡ or pick categories");
  }} catch(err) {{
    alert("Flipkart Minutes Deals Error: " + (err.stack || err.message || err));
  }}
}})();
"""

    with open("FKMinutes_Readable.js", "w", encoding="utf-8") as f:
        f.write(template)

    print("FKMinutes_Readable.js updated successfully!")
    print(f"Size of FKMinutes_Readable.js: {len(template)} characters")

    # Minify for compact / offline bookmarklet
    compact_lines = [line.strip() for line in template.split("\n") if line.strip() and not line.strip().startswith("//")]
    minified_js = " ".join(compact_lines)

    with open("FKMinutes_Compact.txt", "w", encoding="utf-8") as f:
        f.write(minified_js)
    print(f"Size of FKMinutes_Compact.txt: {len(minified_js)} characters")

    with open("FKMinutes.txt", "w", encoding="utf-8") as f:
        f.write(template)
    print("FKMinutes.txt synced successfully!")

    # Standalone offline JS URL (100% self-contained, zero network requests, immune to CSP & ISP blocking)
    clean_js = template
    if clean_js.startswith("javascript:"):
        clean_js = clean_js[len("javascript:"):]
    encoded_standalone_js = "javascript:" + urllib.parse.quote(clean_js)

    # Multi-CDN, CSP-compliant mobile loader with instant visual feedback and multi-method execution
    # 1. Shows instant floating toast '⚡ Loading Minutes Deals...' so mobile users immediately see it triggered
    # 2. Downloads across Fastly jsdelivr -> GitHub raw -> jsdelivr
    # 3. Executes via Blob URL script (allowed by Flipkart CSP: script-src ... blob:)
    #    with fallback to global eval and new Function (allowed by Flipkart CSP: script-src ... 'unsafe-eval')
    # 4. Removes toast on successful launch or displays helpful red error banner if anything fails
    short_loader_js = "javascript:(function(){var old=document.getElementById('fk-loader-toast');if(old)old.remove();var t=document.createElement('div');t.id='fk-loader-toast';t.style.cssText='position:fixed;top:16px;left:50%;transform:translateX(-50%);background:#0F8458;color:#fff;padding:10px 20px;border-radius:24px;font-size:13px;font-weight:700;z-index:2147483647;box-shadow:0 4px 16px rgba(0,0,0,0.3);font-family:sans-serif;pointer-events:none;white-space:nowrap;';t.textContent='⚡ Loading Minutes Deals...';(document.body||document.documentElement).appendChild(t);function fail(msg){if(t){t.style.background='#DC2626';t.textContent='❌ '+msg;setTimeout(function(){t.remove();},6000);}alert('Flipkart Minutes Deals: '+msg);}var u=['https://fastly.jsdelivr.net/gh/jairaj26/flipkart-minutes-deals@main/FKMinutes_Readable.js','https://raw.githubusercontent.com/jairaj26/flipkart-minutes-deals/main/FKMinutes_Readable.js','https://cdn.jsdelivr.net/gh/jairaj26/flipkart-minutes-deals@main/FKMinutes_Readable.js'];function l(i){if(i>=u.length){fail('Network error: Could not download script from CDN or GitHub.');return;}fetch(u[i]+'?t='+Date.now()).then(function(r){if(!r.ok)throw new Error('HTTP '+r.status);return r.text();}).then(function(c){var code=c.replace(/^javascript:/i,'');try{var blob=new Blob([code],{type:'application/javascript'});var url=URL.createObjectURL(blob);var s=document.createElement('script');s.src=url;s.onload=function(){URL.revokeObjectURL(url);if(t)t.remove();};(document.head||document.documentElement).appendChild(s);}catch(e1){try{(1,eval)(code);if(t)t.remove();}catch(e2){try{new Function(code)();if(t)t.remove();}catch(e3){fail(e3.message||e3);}}}}).catch(function(){l(i+1);});}l(0);})();"

    # Update Install_Bookmarklet.html and index.html
    for html_path in ["Install_Bookmarklet.html", "index.html"]:
        if os.path.exists(html_path):
            with open(html_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 1. Update the primary PC/Desktop button to use the bulletproof standalone offline bookmarklet
            # Desktop browsers have no bookmark length limits, so standalone is 100% reliable, instant, and CSP-proof
            content = re.sub(
                r'(<div class="btn-box">\s*<a class="bookmarklet-btn" href=")[^"]+(")',
                lambda m: m.group(1) + encoded_standalone_js + m.group(2),
                content
            )

            # 2. Update the mobile textarea to display the CSP-compliant multi-CDN short loader
            escaped_short_loader = html.escape(short_loader_js)
            content = re.sub(
                r'(<textarea id="mobile-code"[^>]*>)[^<]*(</textarea>)',
                lambda m: m.group(1) + escaped_short_loader + m.group(2),
                content
            )

            # 3. Update the offline fallback button inside details with full standalone bundle
            content = re.sub(
                r'(<summary>🛡️ Looking for the 100% Offline Standalone Version\?</summary>[\s\S]*?<a class="bookmarklet-btn" href=")[^"]+(")',
                lambda m: m.group(1) + encoded_standalone_js + m.group(2),
                content
            )

            # 4. Modernize theme colors in the HTML install guides: from blue to Flipkart Minutes Green (#0F8458)
            content = content.replace("--primary: #2563eb;", "--primary: #0F8458;")
            content = content.replace("--primary-hover: #1d4ed8;", "--primary-hover: #0D724C;")
            content = content.replace("#1e3a8a", "#0F8458")
            content = content.replace("#dbeafe", "#E8F5E9")
            content = content.replace("#eff6ff", "#F0FDF4")
            content = content.replace("linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)", "linear-gradient(135deg, #0F8458 0%, #0D724C 100%)")
            content = content.replace("rgba(37, 99, 235, 0.35)", "rgba(15, 132, 88, 0.35)")
            content = content.replace("rgba(37, 99, 235, 0.45)", "rgba(15, 132, 88, 0.45)")

            with open(html_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Updated all bookmarklet links & Flipkart Minutes theme in {html_path} successfully!")

if __name__ == "__main__":
    build_bookmarklet()
