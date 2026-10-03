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

    # Structure category entries
    # Group icons
    icons = {
        "Staples": "🌾",
        "Snacks & Beverages": "🍟",
        "Dairy, Bakery and Eggs": "🥛",
        "Packaged Goods": "🥫",
        "Personal and Baby Care": "🧼",
        "Fruits and Vegetables": "🍎",
        "Household Care": "🧹",
        "Home & Kitchen": "🍳",
        "Office and School Supplies": "📚"
    }

    # We will build an array of items for the drawer:
    # 1. Master: { id: "all", name: "🔥 Scan All Categories (Top Deals)", isMaster: true, uri: "" }
    # 2. For each group:
    #    - Group Main: { id: "grp_...", name: "... (All)", isGroup: true, uri: "..." }
    #    - Subcategories: { id: "sub_...", name: "↳ ...", isSub: true, uri: "...", defaultSelected: bool }
    
    drawer_items = [
        {
            "id": "master_all",
            "name": "🔥 Scan All Categories (Top Deals)",
            "isMaster": True,
            "uri": ""
        }
    ]

    main_groups = []

    for group_name, subcats in cat_catalog["groups"].items():
        icon = icons.get(group_name, "📦")
        
        # Find group main or clean composite
        # For Household Care: 'Household Care (Excl. Pooja Needs)'
        # For Home & Kitchen: 'Home & Kitchen (Excl. Festive & Cases)'
        # For Packaged Goods: 'All Packaged Goods'
        # For Personal & Baby: 'All Personal & Baby Care'
        # For Fruits & Veg: 'All Fruits & Vegetables'
        # For Office Supplies: 'All Office and School Supplies'
        # For Staples / Snacks / Dairy: first or composite or general group code
        
        main_item = None
        # Check if there is an explicit clean composite or 'All ...' item
        for item in subcats:
            if "Excl." in item["name"] or item["name"].startswith("All "):
                main_item = item
                break
        
        if not main_item:
            # For Staples (73z/bpe), Snacks (73z/ujs), Dairy (73z/esa)
            first_p = subcats[0].get("parent_code", "")
            if first_p:
                main_uri = f"/grocery/pr?marketplace=HYPERLOCAL&sort=discount&sid=73z&p[]=facets.category[]={first_p}"
            else:
                main_uri = subcats[0]["url_path"]
            main_item = {
                "name": f"{group_name} (All)",
                "url_path": main_uri,
                "category_code": first_p
            }

        group_disp_name = f"{icon} {group_name} (All)"
        if "Excl. Pooja" in main_item["name"]:
            group_disp_name = f"{icon} Household Care (Excl. Pooja & Pet)"
        elif "Excl. Festive" in main_item["name"]:
            group_disp_name = f"{icon} Home & Kitchen (Clean - Excl. Cases)"
        
        group_entry = {
            "id": f"grp_{group_name.replace(' ', '_')}",
            "group": group_name,
            "name": group_disp_name,
            "isGroup": True,
            "uri": main_item["url_path"]
        }
        drawer_items.append(group_entry)
        main_groups.append(group_entry)

        # Now add individual subcategories
        for sub in subcats:
            # Skip if it is the composite item itself
            if sub == main_item:
                continue
            if "Excl." in sub["name"] or sub["name"].startswith("All "):
                continue
            if "(All Parent)" in sub["name"]:
                continue
            
            is_optin = not sub.get("default_selected", True)
            optin_suffix = " (Opt-in)" if is_optin else ""
            sub_disp_name = f"  ↳ {sub['name']}{optin_suffix}"

            drawer_items.append({
                "id": f"sub_{sub['category_code'].replace('/', '_')}",
                "group": group_name,
                "name": sub_disp_name,
                "isSub": True,
                "isOptin": is_optin,
                "uri": sub["url_path"]
            })

    print(f"Total drawer items generated: {len(drawer_items)}")
    print(f"Total main scan groups: {len(main_groups)}")

    # Read base template or write updated FKMinutes_Readable.js
    # Let's inspect how cleanly we can construct the JS code.
    
    js_drawer_items = json.dumps(drawer_items, indent=2, ensure_ascii=False)
    js_main_groups = json.dumps(main_groups, indent=2, ensure_ascii=False)
    js_excluded_brands = json.dumps(excluded_brands, indent=2, ensure_ascii=False)

    template = f"""javascript:(function(){{
  /* Clean up existing instances */
  ['fk-deals-sidebar', 'fk-deals-pill', 'fk-deals-styles'].forEach(function(id){{
    var el = document.getElementById(id);
    if (el) el.remove();
  }});

  var THEME = "#2563eb";
  var THEME_DARK = "#1d4ed8";
  var d = document;

  /* Verified Category Catalog (Direct Solr Facets) */
  var DRAWER_ITEMS = {js_drawer_items};

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

  var initialIdx = 0;
  var st = {{
    mode: "IDLE",
    sort: "discount",
    searchQuery: "",
    items: [],
    seen: new Set(),
    selectedIdx: initialIdx,
    selectedItem: DRAWER_ITEMS[initialIdx],
    hideOos: true,
    isCollapsed: false
  }};

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

  /* Inject Sidebar Styles */
  var style = d.createElement("style");
  style.id = "fk-deals-styles";
  style.textContent = `
    #fk-deals-sidebar {{
      position: fixed;
      top: 0;
      right: 0;
      width: 400px;
      max-width: 100vw;
      height: 100vh;
      background: #f8fafc;
      z-index: 2147483647;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Inter, Helvetica, Arial, sans-serif;
      display: flex;
      flex-direction: column;
      border: none;
      box-shadow: -10px 0 35px rgba(0,0,0,0.14);
      color: #0f172a;
      transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    #fk-deals-sidebar.collapsed {{
      transform: translateX(105%);
      pointer-events: none;
    }}
    #fk-deals-pill {{
      position: fixed;
      bottom: 24px;
      right: 18px;
      z-index: 2147483647;
      background: ${{THEME}};
      color: #ffffff;
      padding: 10px 18px;
      border-radius: 30px;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      font-size: 13px;
      font-weight: 700;
      cursor: pointer;
      box-shadow: 0 4px 18px rgba(37,99,235,0.45), 0 2px 6px rgba(0,0,0,0.15);
      display: flex;
      align-items: center;
      gap: 8px;
      border: none;
      transition: transform 0.2s ease, background 0.15s ease;
    }}
    #fk-deals-pill:hover {{
      transform: scale(1.05);
      background: ${{THEME_DARK}};
    }}
    #fk-deals-pill.hidden {{
      display: none;
    }}
    .fkd-badge {{
      background: #fde047;
      color: #0f172a;
      font-size: 11px;
      font-weight: 800;
      padding: 2px 8px;
      border-radius: 12px;
    }}
    .fkd-header {{
      background: linear-gradient(135deg, ${{THEME_DARK}} 0%, ${{THEME}} 100%);
      color: #ffffff;
      padding: 14px 14px 12px 14px;
      display: flex;
      flex-direction: column;
      gap: 9px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.08);
      position: relative;
    }}
    .fkd-top-row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .fkd-title {{
      font-size: 15px;
      font-weight: 800;
      display: flex;
      align-items: center;
      gap: 6px;
      letter-spacing: -0.2px;
    }}
    .fkd-controls {{
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .fkd-icon-btn {{
      background: rgba(255,255,255,0.2);
      border: none;
      color: #ffffff;
      width: 28px;
      height: 28px;
      border-radius: 6px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 15px;
      font-weight: bold;
      transition: background 0.15s ease;
    }}
    .fkd-icon-btn:hover {{
      background: rgba(255,255,255,0.35);
    }}
    .fkd-search-row {{
      display: flex;
      gap: 6px;
      align-items: center;
    }}
    .fkd-input {{
      background: #ffffff;
      color: #0f172a;
      border: none;
      border-radius: 8px;
      padding: 7px 10px;
      font-size: 12px;
      font-weight: 500;
      outline: none;
      box-shadow: 0 1px 3px rgba(0,0,0,0.12);
      transition: box-shadow 0.15s ease;
    }}
    .fkd-input:focus {{
      box-shadow: 0 0 0 2px rgba(255,255,255,0.8), 0 1px 4px rgba(0,0,0,0.2);
    }}
    .fkd-row-2 {{
      position: relative;
      width: 100%;
    }}
    .fkd-cat-toggle {{
      width: 100%;
      background: #ffffff;
      color: #0f172a;
      border: none;
      border-radius: 8px;
      padding: 7px 12px;
      font-size: 12px;
      font-weight: 700;
      text-align: left;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 6px;
      overflow: hidden;
      outline: none;
      box-shadow: 0 1px 3px rgba(0,0,0,0.12);
      transition: background 0.15s ease, box-shadow 0.15s ease;
    }}
    .fkd-cat-toggle:hover {{
      background: #f8fafc;
      box-shadow: 0 2px 6px rgba(0,0,0,0.18);
    }}
    .fkd-cat-toggle-text {{
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      flex: 1;
    }}
    .fkd-caret {{
      font-size: 10px;
      color: #64748b;
      transition: transform 0.2s ease;
    }}
    .fkd-cat-drawer {{
      position: absolute;
      top: calc(100% + 4px);
      left: 0;
      right: 0;
      background: #ffffff;
      border-radius: 10px;
      border: none;
      box-shadow: 0 10px 30px rgba(0,0,0,0.22), 0 2px 8px rgba(0,0,0,0.08);
      max-height: 360px;
      overflow-y: auto;
      z-index: 50;
      padding: 6px;
      display: flex;
      flex-direction: column;
      gap: 2px;
    }}
    .fkd-cat-drawer.hidden {{
      display: none;
    }}
    .fkd-cat-item {{
      padding: 7px 10px;
      border-radius: 6px;
      font-size: 11.5px;
      font-weight: 600;
      color: #334155;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: space-between;
      transition: background 0.15s ease, color 0.15s ease;
    }}
    .fkd-cat-item:hover {{
      background: #eff6ff;
      color: #1d4ed8;
    }}
    .fkd-cat-item.active {{
      background: #dbeafe;
      color: #1e40af;
      font-weight: 800;
    }}
    .fkd-cat-item.fkd-master {{
      background: linear-gradient(135deg, #fef08a 0%, #fde047 100%);
      color: #0f172a;
      font-weight: 800;
      margin-bottom: 4px;
      border: 1px solid #facc15;
    }}
    .fkd-cat-item.fkd-master:hover {{
      background: #facc15;
      color: #000000;
    }}
    .fkd-cat-item.fkd-group-head {{
      font-weight: 700;
      background: #f1f5f9;
      color: #0f172a;
      margin-top: 3px;
    }}
    .fkd-cat-item.fkd-sub {{
      padding-left: 20px;
      font-size: 11px;
      color: #475569;
    }}
    .fkd-cat-item.fkd-optin {{
      color: #94a3b8;
      font-style: italic;
    }}
    /* Toolbar: Exact Equal-Sized Pills */
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
      border-radius: 6px;
      background: rgba(255, 255, 255, 0.18);
      color: #ffffff;
      border: 1px solid rgba(255, 255, 255, 0.28);
      font-size: 11px;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      white-space: nowrap;
      transition: all 0.15s ease;
      user-select: none;
      box-sizing: border-box;
      outline: none;
    }}
    .fkd-pill:hover {{
      background: rgba(255, 255, 255, 0.28);
    }}
    .fkd-pill.active {{
      background: #ffffff;
      color: ${{THEME_DARK}};
      border-color: #ffffff;
      box-shadow: 0 1px 3px rgba(0,0,0,0.12);
    }}
    .fkd-pill-action {{
      background: #fde047;
      color: #0f172a;
      border-color: #fde047;
      font-weight: 800;
    }}
    .fkd-pill-action:hover {{
      background: #facc15;
    }}
    .fkd-pill-danger {{
      background: #ef4444 !important;
      color: #ffffff !important;
      border-color: #ef4444 !important;
      font-weight: 800;
    }}
    .fkd-status-bar {{
      display: flex;
      align-items: center;
      gap: 6px;
      padding-top: 2px;
      min-height: 16px;
    }}
    .fkd-status-dot {{
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: #38bdf8;
      flex-shrink: 0;
    }}
    .fkd-status-text {{
      font-size: 11px;
      color: #e0e7ff;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      flex: 1;
      font-weight: 500;
    }}
    .fkd-grid {{
      flex: 1;
      overflow-y: auto;
      padding: 12px;
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 10px;
      align-content: start;
    }}
    .fkd-card {{
      background: #ffffff;
      border-radius: 10px;
      border: none;
      box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
      padding: 8px;
      display: flex;
      flex-direction: column;
      cursor: pointer;
      position: relative;
      transition: transform 0.15s ease, box-shadow 0.15s ease;
    }}
    .fkd-card:hover {{
      transform: translateY(-2px);
      box-shadow: 0 8px 16px -2px rgba(0,0,0,0.08), 0 4px 6px -2px rgba(0,0,0,0.04);
    }}
    .fkd-card.oos {{
      opacity: 0.62;
      background: #f8fafc;
      box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }}
    .fkd-img-box {{
      position: relative;
      width: 100%;
      height: 110px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 6px;
      background: #f8fafc;
      border-radius: 8px;
      overflow: hidden;
    }}
    .fkd-img {{
      max-width: 100%;
      max-height: 100%;
      object-fit: contain;
    }}
    .fkd-disc-tag {{
      position: absolute;
      top: 4px;
      left: 4px;
      background: #15803d;
      color: #ffffff;
      font-size: 10px;
      font-weight: 800;
      padding: 2px 6px;
      border-radius: 4px;
      box-shadow: 0 1px 2px rgba(0,0,0,0.12);
    }}
    .fkd-oos-tag {{
      position: absolute;
      bottom: 4px;
      left: 4px;
      right: 4px;
      background: rgba(220, 38, 38, 0.92);
      color: #ffffff;
      font-size: 9px;
      font-weight: 800;
      text-align: center;
      padding: 2px 0;
      border-radius: 4px;
      letter-spacing: 0.3px;
    }}
    .fkd-card-title {{
      font-size: 11px;
      font-weight: 600;
      color: #1e293b;
      line-height: 1.35;
      margin-bottom: 6px;
      height: 29px;
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
      font-weight: 800;
      color: #0f172a;
    }}
    .fkd-mrp {{
      font-size: 11px;
      color: #94a3b8;
      text-decoration: line-through;
      font-weight: 500;
    }}
    .fkd-empty {{
      grid-column: 1 / -1;
      text-align: center;
      padding: 40px 15px;
      color: #64748b;
      font-size: 13px;
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
          <button class="fkd-icon-btn" id="fkd-btn-min" title="Minimize / Collapse">_</button>
          <button class="fkd-icon-btn" id="fkd-btn-close" title="Close">✕</button>
        </div>
      </div>
      <div class="fkd-search-row">
        <input type="text" class="fkd-input" id="fkd-input-search" placeholder="🔍 Search e.g. cake, ghee, surf..." style="flex:1" title="Type keyword and press Enter or click Search">
        <button class="fkd-pill fkd-pill-action" id="fkd-btn-search" style="flex:none;width:68px">Search</button>
      </div>
      <div class="fkd-row-2">
        <button class="fkd-cat-toggle" id="fkd-cat-toggle" type="button" title="Browse & select Flipkart Minutes categories">
          <span class="fkd-cat-toggle-text" id="fkd-selected-cat-name">${{DRAWER_ITEMS[initialIdx].name}}</span>
          <span class="fkd-caret" id="fkd-cat-caret">▾</span>
        </button>
        <div id="fkd-cat-drawer" class="fkd-cat-drawer hidden"></div>
      </div>
      <div class="fkd-toolbar">
        <button class="fkd-pill" id="fkd-sort-price" title="Sort by lowest price">Sort ₹</button>
        <button class="fkd-pill active" id="fkd-sort-disc" title="Sort by highest discount">Sort %</button>
        <button class="fkd-pill active" id="fkd-toggle-oos" title="Toggle Out of Stock items">In Stock</button>
        <button class="fkd-pill fkd-pill-action" id="fkd-btn-fetch" title="Fetch category deals">Fetch ⚡</button>
      </div>
      <div class="fkd-status-bar">
        <span class="fkd-status-dot"></span>
        <span class="fkd-status-text" id="fkd-status-msg">Ready</span>
      </div>
    </div>
    <div id="fkd-grid" class="fkd-grid">
      <div class="fkd-empty">Click <b>Fetch ⚡</b> to scan top deals across Flipkart Minutes, or pick a category above.</div>
    </div>
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

  /* Render Drawer Items */
  DRAWER_ITEMS.forEach(function(item, idx){{
    var itemEl = d.createElement("div");
    var cls = "fkd-cat-item";
    if (idx === initialIdx) cls += " active";
    if (item.isMaster) cls += " fkd-master";
    else if (item.isGroup) cls += " fkd-group-head";
    else if (item.isSub) cls += " fkd-sub";
    if (item.isOptin) cls += " fkd-optin";
    itemEl.className = cls;
    itemEl.textContent = item.name;

    itemEl.onclick = function(e) {{
      e.stopPropagation();
      d.querySelectorAll(".fkd-cat-item").forEach(function(el){{ el.classList.remove("active"); }});
      itemEl.classList.add("active");
      st.selectedIdx = idx;
      st.selectedItem = item;
      catNameDisplay.textContent = item.name.trim();
      if (inputSearch) inputSearch.value = "";
      st.searchQuery = "";

      /* User Requirement: Default option should be sort by discount */
      st.sort = "discount";
      btnSortDisc.classList.add("active");
      btnSortPrice.classList.remove("active");

      closeCatDrawer();
      setStatus("Selected: " + item.name.trim());
    }};
    catDrawer.appendChild(itemEl);
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
    btnFetch.textContent = "Fetch ⚡";
    btnFetch.className = "fkd-pill fkd-pill-action";
    if (btnSearch) {{
      btnSearch.textContent = "Search";
      btnSearch.className = "fkd-pill fkd-pill-action";
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
      btnFetch.textContent = "Stop ⏹";
      btnFetch.className = "fkd-pill fkd-pill-danger";
      if (st.selectedItem && st.selectedItem.isMaster) {{
        startAllCategoriesFetch();
      }} else {{
        startCategoryFetch();
      }}
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
      grid.innerHTML = `<div class="fkd-empty">${{st.items.length ? 'No items match current criteria.<br><br>(Total scanned: ' + st.items.length + (st.hideOos ? ', Out of stock hidden' : '') + ')' : 'No deals loaded yet. Click Fetch ⚡ or search above.'}}</div>`;
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
          ${{it.d > 0 ? `<div class="fkd-disc-tag">${{it.d}}% OFF</div>` : ''}}
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

  function addProduct(title, fsp, mrp, disc, img, lnk, isOos) {{
    if (!fsp) return false;
    fsp = parseInt(fsp, 10);
    if (isNaN(fsp) || fsp <= 0) return false;

    /* Clean fallback for generic or missing title */
    if (!title || title === "Product" || title.length < 3) {{
      var urlTitle = extractTitleFromUrl(lnk);
      title = urlTitle || title || "Product";
    }}

    /* Negative keyword & brand filtration (Junk prevention) */
    var tLower = (title || "").toLowerCase();
    for (var k = 0; k < EXCLUDED_KEYWORDS.length; k++) {{
      if (tLower.includes(EXCLUDED_KEYWORDS[k])) return false;
    }}
    /* Religious brands exclusion (starts with reli... except relish) */
    var words = tLower.match(/\\b[a-z]+/g) || [];
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

    /* If discount is present but fsp == mrp, compute selling price from discount */
    if (disc > 0 && disc < 100 && fsp === mrp) {{
      fsp = Math.round(mrp * (1 - disc / 100));
    }}

    /* Normalize discount percentage (0 to 99) */
    if (disc === undefined || isNaN(disc) || disc > 99 || disc < 0) {{
      disc = (mrp > fsp) ? Math.round(((mrp - fsp) / mrp) * 100) : 0;
    }}

    /* Bug Fix: Concatenated MRP and Discount (e.g. 750 MRP + 37% off = 75037) */
    if (mrp > fsp * 4 && disc > 0 && String(mrp).endsWith(String(disc))) {{
      var cleanMrp = parseInt(String(mrp).slice(0, -String(disc).length), 10);
      if (cleanMrp >= fsp) {{
        mrp = cleanMrp;
        disc = Math.round(((mrp - fsp) / mrp) * 100);
      }}
    }}

    /* Threshold verification (default 45% across all categories, bypassed during search) */
    var isSearchMode = !!(st.searchQuery && st.searchQuery.trim().length > 0);
    if (!isSearchMode) {{
      var effectiveMin = DEFAULT_MIN_DISCOUNT;
      for (var bt in BRAND_THRESHOLDS) {{
        if (tLower.startsWith(bt + " ") || tLower.includes(" by " + bt) || tLower === bt || tLower.includes(" " + bt + " ")) {{
          effectiveMin = Math.max(effectiveMin, BRAND_THRESHOLDS[bt]);
          break;
        }}
      }}
      if (disc < effectiveMin) return false;
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
  function parseProducts(json) {{
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
            var fsp = v.pricing.finalPrice.value;
            var mrp = fsp;
            if (v.pricing.prices) {{
              var mrpObj = v.pricing.prices.find(function(x){{ return x.priceType === "MRP"; }});
              if (mrpObj) mrp = mrpObj.value;
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

            if (addProduct(title, fsp, mrp, disc, img, lnk, isOos)) count++;
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

                  var fsp = 0;
                  var l4 = snbText.label_4?.value;
                  var l4Val = (typeof l4 === "object") ? (l4.UNLOCKED?.value?.params?.defaultValue || l4.LOCKED?.value?.params?.defaultValue || l4.text || "") : String(l4 || "");
                  var matchFsp = l4Val.replace(/,/g, "").match(/\\d+/);
                  if (matchFsp) fsp = parseInt(matchFsp[0], 10);

                  var mrp = fsp;
                  var l3 = snbText.label_3?.value;
                  var l3Val = (typeof l3 === "object") ? (l3.params?.defaultValue || l3.text || "") : String(l3 || "");
                  var matchMrp = l3Val.replace(/,/g, "").match(/\\d+/);
                  if (matchMrp) mrp = parseInt(matchMrp[0], 10);

                  var disc = 0;
                  var l2 = snbText.label_2?.value;
                  var l2Val = (typeof l2 === "object") ? (l2.params?.defaultValue || l2.text || "") : String(l2 || "");
                  var matchDisc = l2Val.match(/(\\d+)%/);
                  if (matchDisc) {{
                    disc = parseInt(matchDisc[1], 10);
                  }} else if (mrp > fsp) {{
                    disc = Math.round(((mrp - fsp) / mrp) * 100);
                  }}

                  var stepper = cval.stepperData_0?.action || cval.snb_beauty_gmh_image_0?.value?.stepperData_0?.action;
                  if (!fsp && stepper?.tracking?.fsp) fsp = parseInt(String(stepper.tracking.fsp).replace(/,/g, ""), 10);
                  if (!fsp && stepper?.params?.price) fsp = parseInt(String(stepper.params.price).replace(/,/g, ""), 10);
                  if ((!mrp || mrp === fsp) && stepper?.tracking?.mrp) mrp = parseInt(String(stepper.tracking.mrp).replace(/,/g, ""), 10);

                  if (fsp && mrp && fsp > mrp) {{
                    var t = fsp; fsp = mrp; mrp = t;
                  }}
                  if (disc === 0 && mrp > fsp) {{
                    disc = Math.round(((mrp - fsp) / mrp) * 100);
                  }}

                  var isOos = (stepper?.tracking?.isAvailable === "false") || (stepper?.enabled === false) || (cval.action?.params?.isAvailable === false);

                  var img = cval.col_0?.action?.params?.imageUrl || stepper?.params?.productImage || "";
                  if (!img) {{
                    var imgObj = cval.image_0?.value || cval.snb_beauty_gmh_image_0?.value?.image_0?.value;
                    img = imgObj?.params?.defaultValue || imgObj?.imageHack || imgObj?.dynamicImageUrl || "";
                  }}
                  img = img.replace("{{@width}}", "200").replace("{{@height}}", "200").replace("?q={{@quality}}", "?q=80");

                  if (fsp && addProduct(title, fsp, mrp, disc, img, lnk, isOos)) count++;
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
                  var fsp = parseInt(String(stepperTracking.fsp || stepperAction.params?.price || "").replace(/,/g, ""), 10) || 0;
                  var mrp = parseInt(String(stepperTracking.mrp || "").replace(/,/g, ""), 10) || 0;

                  if (!fsp && pcard.label_5?.value) {{
                    var l5 = pcard.label_5.value;
                    var l5Str = (typeof l5 === "object") ? (l5.LOCKED?.value?.text || l5.UNLOCKED?.value?.text || "") : String(l5);
                    var match5 = l5Str.replace(/,/g, "").match(/\\d+/);
                    if (match5) fsp = parseInt(match5[0], 10);
                  }}

                  if (!mrp && pcard.label_4?.value) {{
                    var l4 = pcard.label_4.value;
                    var l4Str = (typeof l4 === "object") ? (l4.text || "") : String(l4);
                    var match4 = l4Str.replace(/,/g, "").match(/\\d+/);
                    if (match4) mrp = parseInt(match4[0], 10);
                  }}

                  if (fsp && mrp && fsp > mrp) {{
                    var t = fsp; fsp = mrp; mrp = t;
                  }}

                  var lnk = "";
                  var b5 = pcard.box_5?.action?.url || pcard.col_0?.action?.url || pcard.box_0?.action?.url || "";
                  if (b5) lnk = "https://www.flipkart.com" + b5;

                  var title = pcard.label_2?.value?.text || pcard.label_1?.value?.text || pcard.label_0?.value?.text || pcard.trackerData_0?.tracking?.contentTitle || extractTitleFromUrl(lnk) || "Product";

                  if (fsp) {{
                    var disc = 0;
                    if (pcard.label_15?.value) {{
                      var l15 = pcard.label_15.value;
                      var l15Str = (typeof l15 === "object") ? (l15.UNLOCKED?.value?.text || l15.LOCKED?.value?.text || "") : String(l15);
                      var discMatch = l15Str.match(/(\\d+)%/);
                      if (discMatch) disc = parseInt(discMatch[1], 10);
                    }}
                    var img = stepperAction.params?.productImage || "";
                    if (!img) {{
                      var imgObj = pcard.hp_reco_pmu_product-card_image_0?.value || {{}};
                      img = imgObj.image_0?.value?.dynamicImageUrl || imgObj.video_0?.value?.dynamicImageUrl || "";
                    }}
                    img = img.replace("{{@width}}", "200").replace("{{@height}}", "200").replace("?q={{@quality}}", "?q=80");

                    var isOos = (stepperAction.enabled === false) || (pcard.button_0?.value?.actionType === "NOTIFY_ME") || (pcard.button_0?.value?.text && /notify/i.test(pcard.button_0.value.text));
                    if (addProduct(title, fsp, mrp, disc, img, lnk, isOos)) count++;
                  }}
                }}
              }} catch (err) {{}}
            }});
          }}
        }}
      }}
    }});
    return count;
  }}

  /* Scrape items from DOM */
  function parseDomProducts(rootDoc) {{
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
    return count;
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
        credentials: "omit"
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
  function parseHtmlString(html) {{
    var count = 0;
    if (!html) return 0;
    try {{
      var json = extractStateJsonFromHtml(html);
      if (json) {{
        count += parseProducts(json);
      }}
    }} catch(e) {{}}

    try {{
      var parser = new DOMParser();
      var doc = parser.parseFromString(html, "text/html");
      count += parseDomProducts(doc);
    }} catch(e) {{}}

    return count;
  }}

  /* Unified page fetcher */
  async function fetchAndParsePage(uri) {{
    if (!uri) return {{ count: 0 }};
    // 1. HTML-first: Same-origin GET with session cookies (100% reliable, zero 403 errors)
    var html = await fetchCategoryHtml(uri);
    if (html) {{
      var c = parseHtmlString(html);
      if (c > 0) return {{ count: c, html: html }};
    }}
    // 2. Fallback: If HTML fetch returned 0 items, try Rome API
    var json = await fetchRomePage(uri);
    if (json) {{
      var c2 = parseProducts(json);
      if (c2 > 0) return {{ count: c2, json: json }};
    }}
    return {{ count: 0 }};
  }}

  /* Search Flipkart Minutes via Rome API */
  async function startSearch(query) {{
    if (!query || !query.trim()) {{
      setStatus("Enter search keyword");
      return;
    }}
    query = query.trim();
    st.searchQuery = query;
    window.fkDealsStop = false;
    st.mode = "RUN";
    if (btnSearch) {{
      btnSearch.textContent = "Stop ⏹";
      btnSearch.className = "fkd-pill fkd-pill-danger";
    }}

    st.items = [];
    st.seen.clear();
    renderGrid();

    setStatus(`Searching "${{query}}"...`);
    var sortParam = (st.sort === "discount") ? "&sort=discount" : "&sort=price_asc";
    var searchUri = "/hyperlocal/pr?q=" + encodeURIComponent(query) + "&marketplace=HYPERLOCAL&searchSourceContext=experience%3D&widgetUniqueId=1&sid=search.flipkart.com&as-show=on" + sortParam;

    await fetchAndParsePage(searchUri);
    renderGrid();

    if (st.mode === "RUN" && !window.fkDealsStop && st.items.length > 0) {{
      setStatus(`Loading more "${{query}}"...`);
      var p2Uri = searchUri + "&page=2";
      await fetchAndParsePage(p2Uri);
      renderGrid();
    }}

    stopAll();
    var finalIn = st.items.filter(function(x){{ return !x.oos; }}).length;
    setStatus(`Search done! ${{st.items.length}} items (${{finalIn}} in stock)`);
  }}

  /* Master Scan: Sequentially fetch Page 1 across all clean main category groups */
  async function startAllCategoriesFetch() {{
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

    setStatus(`Scanning ${{MAIN_GROUPS.length}} verified categories...`);

    for (var i = 0; i < MAIN_GROUPS.length; i++) {{
      if (st.mode !== "RUN" || window.fkDealsStop) break;
      var grp = MAIN_GROUPS[i];
      setStatus(`[${{i+1}}/${{MAIN_GROUPS.length}}] ${{grp.name.trim()}}...`);
      var pUri = grp.uri;
      if (!pUri.includes("sort=discount")) {{
        pUri += (pUri.includes("?") ? "&" : "?") + "sort=discount";
      }}
      var res = await fetchAndParsePage(pUri);
      renderGrid();

      /* If Page 1 has top deals (>=45%), fetch Page 2 as well */
      if (st.mode === "RUN" && !window.fkDealsStop && res && res.count >= 8 && st.items.some(function(x){{ return x.d >= 45; }})) {{
        var p2Uri = pUri + (pUri.includes("?") ? "&" : "?") + "page=2&sort=discount";
        await fetchAndParsePage(p2Uri);
        renderGrid();
      }}
      await new Promise(function(r){{ setTimeout(r, 280); }});
    }}

    stopAll();
    var finalIn = st.items.filter(function(x){{ return !x.oos; }}).length;
    setStatus(`Done! Found ${{st.items.length}} top deals (${{finalIn}} in stock)`);
  }}

  /* Fetch specific Category or Subcategory */
  async function startCategoryFetch() {{
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

    var item = st.selectedItem;
    var targetUri = item ? item.uri : "";
    if (!targetUri) {{
      startAllCategoriesFetch();
      return;
    }}

    setStatus(`Fetching ${{item.name.trim()}}...`);
    var p1Uri = targetUri;
    if (!p1Uri.includes("sort=discount")) {{
      p1Uri += (p1Uri.includes("?") ? "&" : "?") + "sort=discount";
    }}
    var res1 = await fetchAndParsePage(p1Uri);
    renderGrid();

    /* Multi-page fetching: fetch Page 2 and 3 if high deals present */
    var pageNum = 2;
    while (st.mode === "RUN" && !window.fkDealsStop && pageNum <= 3) {{
      if (res1 && res1.count < 6) break;
      setStatus(`Fetching ${{item.name.trim()}} Page ${{pageNum}}...`);
      var pUri = targetUri + (targetUri.includes("?") ? "&" : "?") + "page=" + pageNum + "&sort=discount";
      var pRes = await fetchAndParsePage(pUri);
      renderGrid();
      if (!pRes.count) break;
      pageNum++;
      await new Promise(function(r){{ setTimeout(r, 300); }});
    }}

    stopAll();
    var finalIn = st.items.filter(function(x){{ return !x.oos; }}).length;
    setStatus(`Done! Found ${{st.items.length}} items (${{finalIn}} in stock)`);
  }}

  /* Initialize */
  setStatus("Ready - Click Fetch ⚡ or select category");
}})();
"""

    with open("FKMinutes_Readable.js", "w", encoding="utf-8") as f:
        f.write(template)

    print("FKMinutes_Readable.js updated successfully!")
    print(f"Size of FKMinutes_Readable.js: {len(template)} characters")

    # Minify for compact bookmarklet
    # Clean whitespace and comments
    compact_code = template
    # encode for bookmarklet URL
    # Replace newlines
    compact_lines = [line.strip() for line in template.split("\n") if line.strip() and not line.strip().startswith("//")]
    minified_js = " ".join(compact_lines)
    
    with open("FKMinutes_Compact.txt", "w", encoding="utf-8") as f:
        f.write(minified_js)
    print(f"Size of FKMinutes_Compact.txt: {len(minified_js)} characters")

    with open("FKMinutes.txt", "w", encoding="utf-8") as f:
        f.write(template)
    print("FKMinutes.txt synced successfully!")

    clean_js = template
    if clean_js.startswith("javascript:"):
        clean_js = clean_js[len("javascript:"):]
    encoded_js = "javascript:" + urllib.parse.quote(clean_js)

    # Update Install_Bookmarklet.html and index.html
    for html_path in ["Install_Bookmarklet.html", "index.html"]:
        if os.path.exists(html_path):
            with open(html_path, "r", encoding="utf-8") as f:
                content = f.read()

            content = re.sub(
                r'(<summary>🛡️ Looking for the 100% Offline Standalone Version\?</summary>[\s\S]*?<a class="bookmarklet-btn" href=")(?:javascript:|javascript%3A)[^"]+(")',
                r'\g<1>' + encoded_js + r'\2',
                content
            )

            with open(html_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Updated bookmarklet link in {html_path} successfully!")

if __name__ == "__main__":
    build_bookmarklet()
