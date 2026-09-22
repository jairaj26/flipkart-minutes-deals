javascript:(function(){
  /* Clean up existing instances */
  ['fk-deals-sidebar', 'fk-deals-pill', 'fk-deals-styles'].forEach(function(id){
    var el = document.getElementById(id);
    if (el) el.remove();
  });

  var THEME = "#2563eb";
  var THEME_DARK = "#1d4ed8";
  var d = document;

  /* Flipkart Minutes Verified Category Catalog (Direct Flat List) */
  var CATEGORIES = [
    { name: "🍎 Fresh Fruits", uri: "/hyperlocal/Fruits/pr?sid=hloc%2F0071&marketplace=HYPERLOCAL", catId: "hloc/0071" },
    { name: "🥕 Fresh Vegetables", uri: "/hyperlocal/Vegetables/pr?sid=hloc%2F0072&marketplace=HYPERLOCAL", catId: "hloc/0072" },
    { name: "🌾 Atta, Rice & Dal", uri: "/hyperlocal/Atta-Rice-Dal/pr?sid=hloc%2F0003&marketplace=HYPERLOCAL", catId: "hloc/0003" },
    { name: "🍳 Oil, Ghee & Masalas", uri: "/hyperlocal/Oil-Ghee-Masala/pr?sid=hloc%2F0009&marketplace=HYPERLOCAL", catId: "hloc/0009" },
    { name: "🥛 Dairy, Bread & Eggs", uri: "/hyperlocal/hloc/3002/pr?sid=hloc%2F0030%2F3002&marketplace=HYPERLOCAL", catId: "hloc/0030" },
    { name: "🍗 Chicken, Meat & Fish", uri: "/hyperlocal/Chicken-Meat-Fish/pr?sid=hloc%2F0031&marketplace=HYPERLOCAL", catId: "hloc/0031" },
    { name: "🍟 Chips, Crisps & Namkeen", uri: "/hyperlocal/Chips-Namkeen/pr?sid=hloc%2F0010&marketplace=HYPERLOCAL", catId: "hloc/0010" },
    { name: "🥤 Cold Drinks & Juices", uri: "/hyperlocal/ColdDrinks-Juices/pr?sid=hloc%2F0007&marketplace=HYPERLOCAL", catId: "hloc/0007" },
    { name: "🍪 Bakery & Biscuits", uri: "/hyperlocal/Bakery-Biscuits/pr?sid=hloc%2F0006&marketplace=HYPERLOCAL", catId: "hloc/0006" },
    { name: "☕ Tea, Coffee & Milk Drinks", uri: "/hyperlocal/Tea-Coffee-Milk-Drinks/pr?sid=hloc%2F0011&marketplace=HYPERLOCAL", catId: "hloc/0011" },
    { name: "🥣 Cereals & Dry Fruits", uri: "/hyperlocal/Cereals-DryFruits/pr?sid=hloc%2F0019&marketplace=HYPERLOCAL", catId: "hloc/0019" },
    { name: "🍝 Instant & Frozen Food", uri: "/hyperlocal/Instant-FrozenFood/pr?sid=hloc%2F0020&marketplace=HYPERLOCAL", catId: "hloc/0020" },
    { name: "🥫 Sauces & Spreads", uri: "/hyperlocal/Sauces-Spreads/pr?sid=hloc%2F0021&marketplace=HYPERLOCAL", catId: "hloc/0021" },
    { name: "🍫 Chocolates & Candies", uri: "/hyperlocal/hloc/6501/pr?sid=hloc%2F0065%2F6501&marketplace=HYPERLOCAL", catId: "hloc/0065" },
    { name: "🍨 Ice Cream & Desserts", uri: "/hyperlocal/IceCream-Desserts/pr?sid=hloc%2F0034&marketplace=HYPERLOCAL", catId: "hloc/0034" },
    { name: "🍬 Sweets & Mithai", uri: "/hyperlocal/hloc/0806/pr?sid=hloc%2F0081%2F0806&marketplace=HYPERLOCAL", catId: "hloc/0081/0806" },
    { name: "🌿 Paan Corner & Refreshments", uri: "/hyperlocal/hloc/4904/pr?sid=hloc%2F0049%2F4904&marketplace=HYPERLOCAL", catId: "hloc/0049/4904" },
    { name: "🧼 Bath & Grooming / Soaps", uri: "/hyperlocal/Bath-Grooming/pr?sid=hloc%2F0013&marketplace=HYPERLOCAL", catId: "hloc/0013" },
    { name: "💇 Hair Care & Shampoos", uri: "/hyperlocal/Hair-Care/pr?sid=hloc%2F0044&marketplace=HYPERLOCAL", catId: "hloc/0044" },
    { name: "💄 Beauty & Fragrances", uri: "/hyperlocal/Beauty-Fragrances/pr?sid=hloc%2F0041&marketplace=HYPERLOCAL", catId: "hloc/0041" },
    { name: "👶 Baby Care & Diapers", uri: "/hyperlocal/Baby-Care/pr?sid=hloc%2F0001%2F0110&marketplace=HYPERLOCAL", catId: "hloc/0001" },
    { name: "💊 Health & Pharma", uri: "/hyperlocal/Health-Pharma/pr?sid=hloc%2F0015&marketplace=HYPERLOCAL", catId: "hloc/0015" },
    { name: "🌸 Feminine Hygiene", uri: "/hyperlocal/hloc/qbq2/pr?sid=hloc%2Fqbq2&marketplace=HYPERLOCAL", catId: "hloc/qbq2" },
    { name: "🛡️ Sexual Wellness", uri: "/hyperlocal/hloc/zgt0/pr?sid=hloc%2Fzgt0&marketplace=HYPERLOCAL", catId: "hloc/zgt0" },
    { name: "🧹 Cleaning Essentials & Detergents", uri: "/hyperlocal/Cleaning-Essentials/pr?sid=hloc%2F0025&marketplace=HYPERLOCAL", catId: "hloc/0025" },
    { name: "🍳 Kitchen & Dining Essentials", uri: "/hyperlocal/Kitchen/pr?sid=hloc%2F0048&marketplace=HYPERLOCAL", catId: "hloc/0048" },
    { name: "🛏️ Home Furnishing & Bedding", uri: "/hyperlocal/hloc/4701/pr?sid=hloc%2F0047%2F4701&marketplace=HYPERLOCAL", catId: "hloc/0047" },
    { name: "📚 School Supplies & Stationery", uri: "/hyperlocal/School-Supplies/pr?sid=hloc%2F0016&marketplace=HYPERLOCAL", catId: "hloc/0016" },
    { name: "🪛 Electricals & Tools", uri: "/hyperlocal/Electircals-Tools/pr?sid=hloc%2F0043&marketplace=HYPERLOCAL", catId: "hloc/0043" },
    { name: "🪔 Pooja Needs & Agarbatti", uri: "/hyperlocal/hloc/8201/pr?sid=hloc%2F0082%2F8201&marketplace=HYPERLOCAL", catId: "hloc/0082" },
    { name: "🐕 Pet Care & Pet Food", uri: "/hyperlocal/PetCare/pr?sid=hloc%2F0029&marketplace=HYPERLOCAL", catId: "hloc/0029" },
    { name: "🧸 Toys & Games", uri: "/hyperlocal/Toys-Games/pr?sid=hloc%2F0028&marketplace=HYPERLOCAL", catId: "hloc/0028" },
    { name: "🏸 Sports & Fitness", uri: "/hyperlocal/Sports-Fitness/pr?sid=hloc%2F0036&marketplace=HYPERLOCAL", catId: "hloc/0036" },
    { name: "👜 Fashion Accessories", uri: "/hyperlocal/Fashion-Accessories/pr?sid=hloc%2F0026&marketplace=HYPERLOCAL", catId: "hloc/0026" },
    { name: "📱 Mobiles & Accessories", uri: "/hyperlocal/Mobiles/pr?sid=hloc%2F0002&marketplace=HYPERLOCAL", catId: "hloc/0002" },
    { name: "🎧 Speakers & Earphones", uri: "/hyperlocal/Speakers-Earphone/pr?sid=hloc%2F0039&marketplace=HYPERLOCAL", catId: "hloc/0039" },
    { name: "🔌 Electronics & Gadgets", uri: "/hyperlocal/Electronics%20and%20Gadgets/pr?sid=hloc%2F0038&marketplace=HYPERLOCAL", catId: "hloc/0038" },
    { name: "🔌 Home Appliances", uri: "/hyperlocal/hloc/4002/pr?sid=hloc%2F0040%2F4002&marketplace=HYPERLOCAL", catId: "hloc/0040/4002" }
  ];

  /* Pre-mapped verified subcategories for instant reliable looping */
  var PRESET_SUBCATS = {
    "hloc/0006": [
      { title: "Biscuits & Cookies", url: "/hyperlocal/hloc/0613/pr?sid=hloc%2F0006%2F0613&marketplace=HYPERLOCAL" },
      { title: "Breads & Buns", url: "/hyperlocal/hloc/0601/pr?sid=hloc%2F0006%2F0601&marketplace=HYPERLOCAL" },
      { title: "Rusk & Khari", url: "/hyperlocal/hloc/0603/pr?sid=hloc%2F0006%2F0603&marketplace=HYPERLOCAL" },
      { title: "Cakes & Muffins", url: "/hyperlocal/hloc/0604/pr?sid=hloc%2F0006%2F0604&marketplace=HYPERLOCAL" },
      { title: "Bakery Snacks", url: "/hyperlocal/hloc/0602/pr?sid=hloc%2F0006%2F0602&marketplace=HYPERLOCAL" }
    ],
    "hloc/0010": [
      { title: "Chips", url: "/hyperlocal/hloc/1001/pr?sid=hloc%2F0010%2F1001&marketplace=HYPERLOCAL" },
      { title: "Bhujia & Mixture", url: "/hyperlocal/hloc/bbvr/pr?sid=hloc%2F0010%2Fbbvr&marketplace=HYPERLOCAL" },
      { title: "Wafers", url: "/hyperlocal/hloc/sotw/pr?sid=hloc%2F0010%2Fsotw&marketplace=HYPERLOCAL" },
      { title: "Namkeens", url: "/hyperlocal/hloc/1002/pr?sid=hloc%2F0010%2F1002&marketplace=HYPERLOCAL" },
      { title: "Indian snacks", url: "/hyperlocal/hloc/qeby/pr?sid=hloc%2F0010%2Fqeby&marketplace=HYPERLOCAL" },
      { title: "Roasted Nuts", url: "/hyperlocal/hloc/1004/pr?sid=hloc%2F0010%2F1004&marketplace=HYPERLOCAL" },
      { title: "Nachos", url: "/hyperlocal/hloc/1003/pr?sid=hloc%2F0010%2F1003&marketplace=HYPERLOCAL" },
      { title: "Healthy Snacks", url: "/hyperlocal/hloc/rzhh/pr?sid=hloc%2F0010%2Frzhh&marketplace=HYPERLOCAL" },
      { title: "Popcorn", url: "/hyperlocal/hloc/1005/pr?sid=hloc%2F0010%2F1005&marketplace=HYPERLOCAL" },
      { title: "Papads & Fryums", url: "/hyperlocal/hloc/1006/pr?sid=hloc%2F0010%2F1006&marketplace=HYPERLOCAL" },
      { title: "Premium & Gourmet", url: "/hyperlocal/hloc/nokv/pr?sid=hloc%2F0010%2Fnokv&marketplace=HYPERLOCAL" }
    ],
    "hloc/0065": [
      { title: "Chocolates", url: "/hyperlocal/hloc/6501/pr?sid=hloc%2F0065%2F6501&marketplace=HYPERLOCAL" },
      { title: "Chocolate Packs", url: "/hyperlocal/hloc/gwcg/pr?sid=hloc%2F0065%2Fgwcg&marketplace=HYPERLOCAL" },
      { title: "Protein & Energy Bars", url: "/hyperlocal/hloc/6505/pr?sid=hloc%2F0065%2F6505&marketplace=HYPERLOCAL" },
      { title: "Wafers and Waffle", url: "/hyperlocal/hloc/6504/pr?sid=hloc%2F0065%2F6504&marketplace=HYPERLOCAL" },
      { title: "Candies & Lollipops", url: "/hyperlocal/hloc/6502/pr?sid=hloc%2F0065%2F6502&marketplace=HYPERLOCAL" },
      { title: "Mouth Freshener & Gum", url: "/hyperlocal/hloc/6503/pr?sid=hloc%2F0065%2F6503&marketplace=HYPERLOCAL" },
      { title: "Dark Chocolate", url: "/hyperlocal/hloc/tczo/pr?sid=hloc%2F0065%2Ftczo&marketplace=HYPERLOCAL" },
      { title: "Milk chocolate", url: "/hyperlocal/hloc/rzod/pr?sid=hloc%2F0065%2Frzod&marketplace=HYPERLOCAL" },
      { title: "Syrups & Spreads", url: "/hyperlocal/hloc/ayvh/pr?sid=hloc%2F0065%2Fayvh&marketplace=HYPERLOCAL" },
      { title: "Shared Packs", url: "/hyperlocal/hloc/evew/pr?sid=hloc%2F0065%2Fevew&marketplace=HYPERLOCAL" },
      { title: "Fruit & Nut Chocolates", url: "/hyperlocal/hloc/skjg/pr?sid=hloc%2F0065%2Fskjg&marketplace=HYPERLOCAL" },
      { title: "Brownies & Muffins", url: "/hyperlocal/hloc/flxv/pr?sid=hloc%2F0065%2Fflxv&marketplace=HYPERLOCAL" },
      { title: "Premium & Imported", url: "/hyperlocal/hloc/ztyr/pr?sid=hloc%2F0065%2Fztyr&marketplace=HYPERLOCAL" }
    ],
    "hloc/0011": [
      { title: "Tea", url: "/hyperlocal/hloc/1101/pr?sid=hloc%2F0011%2F1101&marketplace=HYPERLOCAL" },
      { title: "Coffee", url: "/hyperlocal/hloc/1102/pr?sid=hloc%2F0011%2F1102&marketplace=HYPERLOCAL" },
      { title: "Health & Nutrition Drinks", url: "/hyperlocal/hloc/1103/pr?sid=hloc%2F0011%2F1103&marketplace=HYPERLOCAL" },
      { title: "Green & Herbal Tea", url: "/hyperlocal/hloc/1104/pr?sid=hloc%2F0011%2F1104&marketplace=HYPERLOCAL" }
    ],
    "hloc/0003": [
      { title: "Atta & Flours", url: "/hyperlocal/hloc/0301/pr?sid=hloc%2F0003%2F0301&marketplace=HYPERLOCAL" },
      { title: "Rice & Rice Products", url: "/hyperlocal/hloc/0302/pr?sid=hloc%2F0003%2F0302&marketplace=HYPERLOCAL" },
      { title: "Dals & Pulses", url: "/hyperlocal/hloc/0303/pr?sid=hloc%2F0003%2F0303&marketplace=HYPERLOCAL" }
    ],
    "hloc/0007": [
      { title: "Soft Drinks & Soda", url: "/hyperlocal/hloc/0701/pr?sid=hloc%2F0007%2F0701&marketplace=HYPERLOCAL" },
      { title: "Fruit Juices", url: "/hyperlocal/hloc/0702/pr?sid=hloc%2F0007%2F0702&marketplace=HYPERLOCAL" },
      { title: "Energy & Sports Drinks", url: "/hyperlocal/hloc/0703/pr?sid=hloc%2F0007%2F0703&marketplace=HYPERLOCAL" }
    ],
    "hloc/0009": [
      { title: "Edible Oils", url: "/hyperlocal/hloc/0901/pr?sid=hloc%2F0009%2F0901&marketplace=HYPERLOCAL" },
      { title: "Ghee & Vanaspati", url: "/hyperlocal/hloc/0902/pr?sid=hloc%2F0009%2F0902&marketplace=HYPERLOCAL" },
      { title: "Spices & Masalas", url: "/hyperlocal/hloc/0903/pr?sid=hloc%2F0009%2F0903&marketplace=HYPERLOCAL" }
    ]
  };

  /* Auto-detect active category if user is already browsing a Flipkart Minutes category */
  var initialIdx = 0;
  try {
    var curUrl = window.location.href;
    var sidMatch = curUrl.match(/sid=([^&]+)/i);
    if (sidMatch) {
      var decodedSid = decodeURIComponent(sidMatch[1]);
      var matchIdx = CATEGORIES.findIndex(function(c){
        return c.catId && (decodedSid === c.catId || decodedSid.startsWith(c.catId + "/") || c.catId.startsWith(decodedSid));
      });
      if (matchIdx !== -1) initialIdx = matchIdx;
    }
  } catch(e) {}

  var st = {
    mode: "IDLE",
    sort: "discount",
    searchQuery: "",
    items: [],
    seen: new Set(),
    selectedMode: CATEGORIES[initialIdx].uri,
    selectedCatId: CATEGORIES[initialIdx].catId,
    hideOos: true,
    isCollapsed: false
  };

  window.fkDealsStop = false;

  /* Helper function: Extract human-friendly product title from Flipkart canonical URL slug */
  function extractTitleFromUrl(url) {
    try {
      if (!url) return "";
      var m = url.match(/\/([a-z0-9][a-z0-9-]+[a-z0-9])\/p\/(?:itm|[a-z0-9]+)/i);
      if (m && m[1]) {
        var slug = m[1].replace(/-/g, " ").trim();
        if (slug.length > 3) {
          return slug.replace(/\b[a-z]/g, function(c){ return c.toUpperCase(); });
        }
      }
    } catch(e) {}
    return "";
  }

  /* Inject Sidebar Styles */
  var style = d.createElement("style");
  style.id = "fk-deals-styles";
  style.textContent = `
    #fk-deals-sidebar {
      position: fixed;
      top: 0;
      right: 0;
      width: 395px;
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
    }
    #fk-deals-sidebar.collapsed {
      transform: translateX(105%);
      pointer-events: none;
    }
    #fk-deals-pill {
      position: fixed;
      bottom: 24px;
      right: 18px;
      z-index: 2147483647;
      background: ${THEME};
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
    }
    #fk-deals-pill:hover {
      transform: scale(1.05);
      background: ${THEME_DARK};
    }
    #fk-deals-pill.hidden {
      display: none;
    }
    .fkd-badge {
      background: #fde047;
      color: #0f172a;
      font-size: 11px;
      font-weight: 800;
      padding: 2px 8px;
      border-radius: 12px;
    }
    .fkd-header {
      background: linear-gradient(135deg, ${THEME_DARK} 0%, ${THEME} 100%);
      color: #ffffff;
      padding: 14px 14px 12px 14px;
      display: flex;
      flex-direction: column;
      gap: 9px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.08);
      position: relative;
    }
    .fkd-top-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .fkd-title {
      font-size: 15px;
      font-weight: 800;
      display: flex;
      align-items: center;
      gap: 6px;
      letter-spacing: -0.2px;
    }
    .fkd-controls {
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .fkd-icon-btn {
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
    }
    .fkd-icon-btn:hover {
      background: rgba(255,255,255,0.35);
    }
    .fkd-search-row {
      display: flex;
      gap: 6px;
      align-items: center;
    }
    .fkd-input {
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
    }
    .fkd-input:focus {
      box-shadow: 0 0 0 2px rgba(255,255,255,0.8), 0 1px 4px rgba(0,0,0,0.2);
    }
    .fkd-row-2 {
      position: relative;
      width: 100%;
    }
    .fkd-cat-toggle {
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
    }
    .fkd-cat-toggle:hover {
      background: #f8fafc;
      box-shadow: 0 2px 6px rgba(0,0,0,0.18);
    }
    .fkd-cat-toggle-text {
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      flex: 1;
    }
    .fkd-caret {
      font-size: 10px;
      color: #64748b;
      transition: transform 0.2s ease;
    }
    .fkd-cat-drawer {
      position: absolute;
      top: calc(100% + 4px);
      left: 0;
      right: 0;
      background: #ffffff;
      border-radius: 10px;
      border: none;
      box-shadow: 0 10px 30px rgba(0,0,0,0.22), 0 2px 8px rgba(0,0,0,0.08);
      max-height: 290px;
      overflow-y: auto;
      z-index: 50;
      padding: 6px;
      display: flex;
      flex-direction: column;
      gap: 2px;
    }
    .fkd-cat-drawer.hidden {
      display: none;
    }
    .fkd-cat-item {
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
    }
    .fkd-cat-item:hover {
      background: #eff6ff;
      color: #1d4ed8;
    }
    .fkd-cat-item.active {
      background: #dbeafe;
      color: #1e40af;
      font-weight: 800;
    }
    /* Toolbar: Exact Equal-Sized Pills (flex: 1 1 0) */
    .fkd-toolbar {
      display: flex;
      gap: 6px;
      align-items: center;
      width: 100%;
    }
    .fkd-pill {
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
    }
    .fkd-pill:hover {
      background: rgba(255, 255, 255, 0.28);
    }
    .fkd-pill.active {
      background: #ffffff;
      color: ${THEME_DARK};
      border-color: #ffffff;
      box-shadow: 0 1px 3px rgba(0,0,0,0.12);
    }
    .fkd-pill-action {
      background: #fde047;
      color: #0f172a;
      border-color: #fde047;
      font-weight: 800;
    }
    .fkd-pill-action:hover {
      background: #facc15;
    }
    .fkd-pill-danger {
      background: #ef4444 !important;
      color: #ffffff !important;
      border-color: #ef4444 !important;
      font-weight: 800;
    }
    /* Dedicated Full-Width Status Bar to avoid pill resizing */
    .fkd-status-bar {
      display: flex;
      align-items: center;
      gap: 6px;
      padding-top: 2px;
      min-height: 16px;
    }
    .fkd-status-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: #38bdf8;
      flex-shrink: 0;
    }
    .fkd-status-text {
      font-size: 11px;
      color: #e0e7ff;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      flex: 1;
      font-weight: 500;
    }
    .fkd-grid {
      flex: 1;
      overflow-y: auto;
      padding: 12px;
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 10px;
      align-content: start;
    }
    .fkd-card {
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
    }
    .fkd-card:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 16px -2px rgba(0,0,0,0.08), 0 4px 6px -2px rgba(0,0,0,0.04);
    }
    .fkd-card.oos {
      opacity: 0.62;
      background: #f8fafc;
      box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    .fkd-img-box {
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
    }
    .fkd-img {
      max-width: 100%;
      max-height: 100%;
      object-fit: contain;
    }
    .fkd-disc-tag {
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
    }
    .fkd-oos-tag {
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
    }
    .fkd-card-title {
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
    }
    .fkd-price-row {
      margin-top: auto;
      display: flex;
      align-items: baseline;
      gap: 6px;
    }
    .fkd-price {
      font-size: 14px;
      font-weight: 800;
      color: #0f172a;
    }
    .fkd-mrp {
      font-size: 11px;
      color: #94a3b8;
      text-decoration: line-through;
      font-weight: 500;
    }
    .fkd-empty {
      grid-column: 1 / -1;
      text-align: center;
      padding: 40px 15px;
      color: #64748b;
      font-size: 13px;
      line-height: 1.6;
    }
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
        <input type="text" class="fkd-input" id="fkd-input-search" placeholder="🔍 Search e.g. cake, milk, chips..." style="flex:1" title="Type keyword and press Enter or click Search">
        <button class="fkd-pill fkd-pill-action" id="fkd-btn-search" style="flex:none;width:68px">Search</button>
      </div>
      <div class="fkd-row-2">
        <button class="fkd-cat-toggle" id="fkd-cat-toggle" type="button" title="Browse & select Flipkart Minutes categories">
          <span class="fkd-cat-toggle-text" id="fkd-selected-cat-name">${CATEGORIES[initialIdx].name}</span>
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
      <div class="fkd-empty">Select a category and click <b>Fetch ⚡</b>, or search above to find top deals.</div>
    </div>
  `;
  d.body.appendChild(sb);

  /* Element References */
  var catToggle = d.getElementById("fkd-cat-toggle");
  var catNameDisplay = d.getElementById("fkd-selected-cat-name");
  var catCaret = d.getElementById("fkd-cat-caret");
  var catDrawer = d.getElementById("fkd-cat-drawer");

  function closeCatDrawer() {
    if (catDrawer && !catDrawer.classList.contains("hidden")) {
      catDrawer.classList.add("hidden");
      if (catCaret) catCaret.textContent = "▾";
    }
  }

  function toggleCatDrawer() {
    if (!catDrawer) return;
    if (catDrawer.classList.contains("hidden")) {
      catDrawer.classList.remove("hidden");
      if (catCaret) catCaret.textContent = "▴";
    } else {
      closeCatDrawer();
    }
  }

  catToggle.onclick = function(e) {
    e.stopPropagation();
    toggleCatDrawer();
  };

  /* Render direct flat list of all verified categories inside drawer */
  CATEGORIES.forEach(function(item, idx){
    var itemEl = d.createElement("div");
    itemEl.className = "fkd-cat-item" + (idx === initialIdx ? " active" : "");
    itemEl.textContent = item.name;

    itemEl.onclick = function(e) {
      e.stopPropagation();
      d.querySelectorAll(".fkd-cat-item").forEach(function(el){ el.classList.remove("active"); });
      itemEl.classList.add("active");
      st.selectedMode = item.uri;
      st.selectedCatId = item.catId;
      catNameDisplay.textContent = item.name;
      if (inputSearch) inputSearch.value = "";
      st.searchQuery = "";

      /* User Requirement: Default option should be sort by discount on choosing category */
      st.sort = "discount";
      btnSortDisc.classList.add("active");
      btnSortPrice.classList.remove("active");

      closeCatDrawer();
      setStatus("Selected: " + item.name);
    };
    catDrawer.appendChild(itemEl);
  });

  /* Close drawer when clicking outside inside sidebar */
  sb.addEventListener("click", function(e){
    if (catDrawer && !catDrawer.contains(e.target) && !catToggle.contains(e.target)) {
      closeCatDrawer();
    }
  });

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

  function setStatus(txt) {
    if (statusMsg) statusMsg.textContent = txt;
  }

  function toggleCollapse(collapsed) {
    st.isCollapsed = collapsed;
    if (collapsed) {
      sb.classList.add("collapsed");
      pill.classList.remove("hidden");
    } else {
      sb.classList.remove("collapsed");
      pill.classList.add("hidden");
    }
  }

  function stopAll() {
    window.fkDealsStop = true;
    st.mode = "STOPPED";
    btnFetch.textContent = "Fetch ⚡";
    btnFetch.className = "fkd-pill fkd-pill-action";
    if (btnSearch) {
      btnSearch.textContent = "Search";
      btnSearch.className = "fkd-pill fkd-pill-action";
    }
  }

  btnSearch.onclick = function() {
    if (st.mode === "RUN") {
      stopAll();
      setStatus("Stopped (" + st.items.length + " items)");
    } else {
      startSearch(inputSearch.value);
    }
  };

  inputSearch.onkeydown = function(e) {
    if (e.key === "Enter") {
      if (st.mode === "RUN") {
        stopAll();
      }
      startSearch(inputSearch.value);
    }
  };

  btnMin.onclick = function() { toggleCollapse(true); };
  pill.onclick = function() { toggleCollapse(false); };

  btnClose.onclick = function() {
    stopAll();
    sb.remove();
    pill.remove();
    style.remove();
  };

  btnSortPrice.onclick = function() {
    st.sort = "price_asc";
    btnSortPrice.classList.add("active");
    btnSortDisc.classList.remove("active");
    renderGrid();
  };

  btnSortDisc.onclick = function() {
    st.sort = "discount";
    btnSortDisc.classList.add("active");
    btnSortPrice.classList.remove("active");
    renderGrid();
  };

  btnToggleOos.onclick = function() {
    st.hideOos = !st.hideOos;
    if (st.hideOos) {
      btnToggleOos.classList.add("active");
      btnToggleOos.textContent = "In Stock";
    } else {
      btnToggleOos.classList.remove("active");
      btnToggleOos.textContent = "All Items";
    }
    renderGrid();
  };

  btnFetch.onclick = function() {
    closeCatDrawer();
    if (st.mode === "RUN") {
      stopAll();
      setStatus("Stopped (" + st.items.length + " items)");
    } else {
      btnFetch.textContent = "Stop ⏹";
      btnFetch.className = "fkd-pill fkd-pill-danger";
      startCategoryFetch();
    }
  };

  function renderGrid() {
    grid.innerHTML = "";
    var filtered = st.items.filter(function(it){
      if (st.hideOos && it.oos) return false;
      return true;
    });

    if (st.sort === "discount") {
      filtered.sort(function(a, b){ return b.d - a.d; });
    } else {
      filtered.sort(function(a, b){ return a.f - b.f; });
    }

    var inStockCount = filtered.filter(function(x){ return !x.oos; }).length;
    var oosCount = filtered.length - inStockCount;
    headCount.textContent = st.hideOos
      ? `${filtered.length} Deals (${inStockCount} In Stock)`
      : `${filtered.length} Deals (${inStockCount} In Stock, ${oosCount} OOS)`;
    pillCount.textContent = filtered.length;

    if (!filtered.length) {
      grid.innerHTML = `<div class="fkd-empty">${st.items.length ? 'No items match current criteria.<br><br>(Total scanned: ' + st.items.length + (st.hideOos ? ', Out of stock hidden' : '') + ')' : 'No deals loaded yet. Select a category or search above.'}</div>`;
      return;
    }

    filtered.forEach(function(it){
      var card = d.createElement("div");
      card.className = "fkd-card" + (it.oos ? " oos" : "");
      card.innerHTML = `
        <div class="fkd-img-box">
          <img src="${it.i}" class="fkd-img" loading="lazy" onerror="this.src='https://rukminim1.flixcart.com/flap/200/200/image/placeholder.png'">
          ${it.d > 0 ? `<div class="fkd-disc-tag">${it.d}% OFF</div>` : ''}
          ${it.oos ? `<div class="fkd-oos-tag">OUT OF STOCK</div>` : ''}
        </div>
        <div class="fkd-card-title" title="${it.t.replace(/"/g, '&quot;')}">${it.t}</div>
        <div class="fkd-price-row">
          <span class="fkd-price">₹${it.f}</span>
          ${it.m > it.f ? `<span class="fkd-mrp">₹${it.m}</span>` : ''}
        </div>
      `;
      card.onclick = function() {
        if (it.l) window.open(it.l, "_blank");
      };
      grid.appendChild(card);
    });
  }

  function addProduct(title, fsp, mrp, disc, img, lnk, isOos) {
    if (!fsp) return false;
    fsp = parseInt(fsp, 10);
    if (isNaN(fsp) || fsp <= 0) return false;

    /* Clean fallback for generic or missing title */
    if (!title || title === "Product" || title.length < 3) {
      var urlTitle = extractTitleFromUrl(lnk);
      title = urlTitle || title || "Product";
    }

    mrp = mrp ? parseInt(mrp, 10) : fsp;
    if (isNaN(mrp) || mrp <= 0) mrp = fsp;

    /* Selling price is ALWAYS <= MRP. If swapped, correct them */
    if (fsp > mrp) {
      var tmp = fsp;
      fsp = mrp;
      mrp = tmp;
    }

    /* If discount is present but fsp == mrp, compute selling price from discount */
    if (disc > 0 && disc < 100 && fsp === mrp) {
      fsp = Math.round(mrp * (1 - disc / 100));
    }

    /* Normalize discount percentage (0 to 99) */
    if (disc === undefined || isNaN(disc) || disc > 99 || disc < 0) {
      disc = (mrp > fsp) ? Math.round(((mrp - fsp) / mrp) * 100) : 0;
    }

    /* Bug Fix: Concatenated MRP and Discount (e.g. 750 MRP + 37% off = 75037) */
    if (mrp > fsp * 4 && disc > 0 && String(mrp).endsWith(String(disc))) {
      var cleanMrp = parseInt(String(mrp).slice(0, -String(disc).length), 10);
      if (cleanMrp >= fsp) {
        mrp = cleanMrp;
        disc = Math.round(((mrp - fsp) / mrp) * 100);
      }
    }

    /* Ensure deal links open directly in Flipkart Minutes */
    if (lnk && !lnk.includes("marketplace=HYPERLOCAL")) {
      lnk += (lnk.includes("?") ? "&" : "?") + "marketplace=HYPERLOCAL";
    }

    var uid = title + "_" + fsp;
    if (!st.seen.has(uid)) {
      st.seen.add(uid);
      st.items.push({ t: title, f: fsp, m: mrp, d: disc, i: img, l: lnk, oos: !!isOos });
      return true;
    }
    return false;
  }

  /* Parse products from Rome API JSON structure */
  function parseProducts(json) {
    var count = 0;
    if (!json) return count;
    var slots = json.RESPONSE?.slots || json.slots || json.pageData?.slots || json.multiWidgetState?.widgetsData?.slots || json.multiWidgetState?.pageDataResponse?.slots || [];
    slots.forEach(function(s){
      var w = s.widget || {};
      var wdata = w.data || {};

      /* 1. Standard Product Summaries */
      var comps = wdata.products || wdata.renderableComponents || [];
      comps.forEach(function(item){
        try {
          var pinfo = item.productInfo || item;
          var v = pinfo.value || pinfo;
          if (v && v.pricing && v.pricing.finalPrice) {
            var fsp = v.pricing.finalPrice.value;
            var mrp = fsp;
            if (v.pricing.prices) {
              var mrpObj = v.pricing.prices.find(function(x){ return x.priceType === "MRP"; });
              if (mrpObj) mrp = mrpObj.value;
            }
            if (fsp && mrp && fsp > mrp) {
              var t = fsp; fsp = mrp; mrp = t;
            }
            var disc = v.pricing.totalDiscount;
            var lnk = v.baseUrl ? ("https://www.flipkart.com" + v.baseUrl) : (v.smartUrl ? ("https://www.flipkart.com" + v.smartUrl) : "");
            var title = v.titles?.title || v.titles?.newTitle || v.titles?.superTitle || v.productTitle || extractTitleFromUrl(lnk) || "Product";
            var img = v.media?.images?.[0]?.url || v.images?.[0]?.url || "";
            img = img.replace("{@width}", "200").replace("{@height}", "200").replace("?q={@quality}", "?q=80");

            /* Determine Out of Stock status */
            var isOos = (v.availability?.displayState === "OUT_OF_STOCK") ||
                        (v.productAction?.value?.enabled === false) ||
                        (v.productAction?.value?.actionType === "NOTIFY_ME") ||
                        (v.buyability?.intent === "negative") ||
                        (v.action?.params?.isAvailable === false) ||
                        (v.availability && v.availability.displayState && v.availability.displayState !== "IN_STOCK");

            if (addProduct(title, fsp, mrp, disc, img, lnk, isOos)) count++;
          }
        } catch (e) {}
      });

      /* 2. DLS / Atlas Recommendation & Search Grid Widgets */
      var dls = wdata.dlsData || {};
      for (var k in dls) {
        if (k.indexOf("MRCSV") !== -1 || k.indexOf("carouselData") !== -1 || k.indexOf("gridData") !== -1 || k.indexOf("horizontalListData") !== -1) {
          var cardList = dls[k]?.value || [];
          if (Array.isArray(cardList)) {
            cardList.forEach(function(cardWrapper){
              try {
                var cval = cardWrapper?.value || {};

                /* Case A: ATLAS Search & Grid Cards (snb_hl_text_0) */
                if (cval.snb_hl_text_0?.value) {
                  var snbText = cval.snb_hl_text_0.value;
                  var lnk = cval.col_0?.action?.url || cval.col_0?.action?.originalUrl || "";
                  if (lnk && !lnk.startsWith("http")) lnk = "https://www.flipkart.com" + lnk;

                  var title = snbText.label_0?.value?.text || snbText.label_1?.value?.text || cval.trackerData_0?.tracking?.contentTitle || extractTitleFromUrl(lnk) || "Product";

                  var fsp = 0;
                  var l4 = snbText.label_4?.value;
                  var l4Val = (typeof l4 === "object") ? (l4.UNLOCKED?.value?.params?.defaultValue || l4.LOCKED?.value?.params?.defaultValue || l4.text || "") : String(l4 || "");
                  var matchFsp = l4Val.match(/\d+/);
                  if (matchFsp) fsp = parseInt(matchFsp[0], 10);

                  var mrp = fsp;
                  var l3 = snbText.label_3?.value;
                  var l3Val = (typeof l3 === "object") ? (l3.params?.defaultValue || l3.text || "") : String(l3 || "");
                  var matchMrp = l3Val.match(/\d+/);
                  if (matchMrp) mrp = parseInt(matchMrp[0], 10);

                  var disc = 0;
                  var l2 = snbText.label_2?.value;
                  var l2Val = (typeof l2 === "object") ? (l2.params?.defaultValue || l2.text || "") : String(l2 || "");
                  var matchDisc = l2Val.match(/(\d+)%/);
                  if (matchDisc) {
                    disc = parseInt(matchDisc[1], 10);
                  } else if (mrp > fsp) {
                    disc = Math.round(((mrp - fsp) / mrp) * 100);
                  }

                  var stepper = cval.stepperData_0?.action || cval.snb_beauty_gmh_image_0?.value?.stepperData_0?.action;
                  if (!fsp && stepper?.params?.price) fsp = parseInt(stepper.params.price, 10);
                  if (!fsp && stepper?.tracking?.fsp) fsp = parseInt(stepper.tracking.fsp, 10);
                  if (stepper?.tracking?.mrp) mrp = parseInt(stepper.tracking.mrp, 10);

                  if (fsp && mrp && fsp > mrp) {
                    var t = fsp; fsp = mrp; mrp = t;
                  }

                  var isOos = (stepper?.tracking?.isAvailable === "false") || (stepper?.enabled === false) || (cval.action?.params?.isAvailable === false);

                  var img = cval.col_0?.action?.params?.imageUrl || stepper?.params?.productImage || "";
                  if (!img) {
                    var imgObj = cval.image_0?.value || cval.snb_beauty_gmh_image_0?.value?.image_0?.value;
                    img = imgObj?.params?.defaultValue || imgObj?.imageHack || imgObj?.dynamicImageUrl || "";
                  }
                  img = img.replace("{@width}", "200").replace("{@height}", "200").replace("?q={@quality}", "?q=80");

                  if (fsp && addProduct(title, fsp, mrp, disc, img, lnk, isOos)) count++;
                  return;
                }

                /* Case B: MRCSV / Product Cards */
                var pcard = null;
                for (var pk in cval) {
                  if (pk.indexOf("product-card") !== -1 || pk.indexOf("productCard") !== -1) {
                    pcard = cval[pk]?.value || {};
                    break;
                  }
                }
                if (pcard) {
                  var stepperAction = pcard.stepperData_0?.action || {};
                  var stepperTracking = stepperAction.tracking || {};
                  var fsp = stepperTracking.fsp || stepperAction.params?.price;
                  var mrp = stepperTracking.mrp;

                  if (!fsp && pcard.label_5?.value) {
                    var l5 = pcard.label_5.value;
                    var l5Str = (typeof l5 === "object") ? (l5.LOCKED?.value?.text || l5.UNLOCKED?.value?.text || "") : String(l5);
                    var match5 = l5Str.match(/\d+/);
                    if (match5) fsp = parseInt(match5[0], 10);
                  }

                  if (!mrp && pcard.label_4?.value) {
                    var l4 = pcard.label_4.value;
                    var l4Str = (typeof l4 === "object") ? (l4.text || "") : String(l4);
                    var match4 = l4Str.match(/\d+/);
                    if (match4) mrp = parseInt(match4[0], 10);
                  }

                  if (fsp && mrp && fsp > mrp) {
                    var t = fsp; fsp = mrp; mrp = t;
                  }

                  var lnk = "";
                  var b5 = pcard.box_5?.action?.url || pcard.col_0?.action?.url || pcard.box_0?.action?.url || "";
                  if (b5) lnk = "https://www.flipkart.com" + b5;

                  var title = pcard.label_2?.value?.text || pcard.label_1?.value?.text || pcard.label_0?.value?.text || pcard.trackerData_0?.tracking?.contentTitle || extractTitleFromUrl(lnk) || "Product";

                  if (fsp) {
                    var disc = 0;
                    if (pcard.label_15?.value) {
                      var l15 = pcard.label_15.value;
                      var l15Str = (typeof l15 === "object") ? (l15.UNLOCKED?.value?.text || l15.LOCKED?.value?.text || "") : String(l15);
                      var discMatch = l15Str.match(/(\d+)%/);
                      if (discMatch) disc = parseInt(discMatch[1], 10);
                    }
                    var img = stepperAction.params?.productImage || "";
                    if (!img) {
                      var imgObj = pcard.hp_reco_pmu_product-card_image_0?.value || {};
                      img = imgObj.image_0?.value?.dynamicImageUrl || imgObj.video_0?.value?.dynamicImageUrl || "";
                    }
                    img = img.replace("{@width}", "200").replace("{@height}", "200").replace("?q={@quality}", "?q=80");

                    var isOos = (stepperAction.enabled === false) || (pcard.button_0?.value?.actionType === "NOTIFY_ME") || (pcard.button_0?.value?.text && /notify/i.test(pcard.button_0.value.text));
                    if (addProduct(title, fsp, mrp, disc, img, lnk, isOos)) count++;
                  }
                }
              } catch (err) {}
            });
          }
        }
      }
    });
    return count;
  }

  /* Scrape items from DOM (WITHOUT SCROLLING) */
  function parseDomProducts(rootDoc) {
    var doc = rootDoc || document;
    var count = 0;
    var anchors = doc.querySelectorAll('a[href*="/p/itm"], a[href*="/p/"], a[href*="pid="]');
    var processedCards = new Set();

    anchors.forEach(function(a){
      try {
        var href = a.getAttribute("href") || "";
        if (!href || href.includes("javascript:") || href.length < 5) return;
        if (!href.startsWith("http")) href = "https://www.flipkart.com" + href;

        /* Find outer card container */
        var card = a.closest('[data-id], [class*="card" i], [class*="product" i], [class*="grid" i], [class*="_1AtVbE"]') || a.parentElement;
        var cardKey = (card && card.getAttribute && card.getAttribute("data-id")) || href.split("?")[0];
        if (cardKey && processedCards.has(cardKey)) return;
        if (cardKey) processedCards.add(cardKey);

        /* Extract price elements specifically if present */
        var fsp = 0;
        var mrp = 0;
        var disc = 0;

        var fspEl = (card || a).querySelector('.hZ3P6w, ._30jeq3, .Nx9bqj');
        var mrpEl = (card || a).querySelector('.kRYCnD, ._3I9_wc, .yRaY8j');
        var discEl = (card || a).querySelector('.HQe8jr, ._3Ay6Sb');

        if (fspEl) {
          var m1 = fspEl.innerText.replace(/[^\d]/g, "");
          if (m1) fsp = parseInt(m1, 10);
        }
        if (mrpEl) {
          var m2 = mrpEl.innerText.replace(/[^\d]/g, "");
          if (m2) mrp = parseInt(m2, 10);
        }
        if (discEl) {
          var m3 = discEl.innerText.match(/\b([1-9][0-9]?)\s*%/);
          if (m3) disc = parseInt(m3[1], 10);
        }

        /* Fallback to text matching if specific classes were not found */
        if (!fsp) {
          var text = (card ? card.innerText : a.innerText) || "";

          /* Remove promotional "save extra ₹20" to avoid picking offer amounts as product price */
          text = text.replace(/save\s*(?:extra\s*)?(?:₹|\u20b9)\s*\d+/gi, "")
                     .replace(/buy\s*\d+\s*(?:items|get|for)[^₹\n]*(?:₹|\u20b9)\s*\d+/gi, "");

          /* Pre-normalize text to separate adjacent price and discount digits */
          text = text.replace(/(?:₹|\u20b9)\s*([0-9,]+?)(\d{1,2})%\s*off/gi, "₹$1 $2% off")
                     .replace(/([0-9])([0-9]{2}%)/g, "$1 $2")
                     .replace(/(?:₹|\u20b9)\s*([0-9,]+)(?=[0-9]{2}%)/g, "₹$1 ");

          var priceMatches = text.match(/(?:₹|\u20b9)\s*([0-9,]+)/g);
          if (!priceMatches || !priceMatches.length) return;

          var prices = priceMatches.map(function(p){
            return parseInt(p.replace(/[^\d]/g, ""), 10);
          }).filter(function(n){ return !isNaN(n) && n > 0; });

          if (!prices.length) return;

          if (prices.length === 1) {
            fsp = prices[0];
            mrp = fsp;
          } else {
            fsp = Math.min(prices[0], prices[1]);
            mrp = Math.max(prices[0], prices[1]);
          }

          if (!disc) {
            var discMatch = text.match(/\b([1-9][0-9]?)\s*%\s*off/i);
            if (discMatch) disc = parseInt(discMatch[1], 10);
          }
        }

        /* Image extraction */
        var imgEl = (card || a).querySelector('img[src*="rukminim"], img[src*="flixcart"], img');
        var img = imgEl ? (imgEl.src || imgEl.getAttribute("src") || "") : "";

        /* Multi-strategy Title Extraction */
        var title = "";
        var titleEl = (card || a).querySelector('[class*="title" i], [class*="name" i], [class*="pIpigb"], [class*="wjcEIp"], [class*="s1Q9rs"], [class*="_4rR01T"], [class*="_2Wk75y"]');
        if (titleEl && titleEl.innerText && titleEl.innerText.trim().length > 3) {
          title = titleEl.innerText.trim();
        }
        if (!title && a.getAttribute("title")) {
          title = a.getAttribute("title").trim();
        }
        if (!title) {
          var anyTitleA = (card || a).querySelector("a[title]");
          if (anyTitleA && anyTitleA.getAttribute("title")) {
            title = anyTitleA.getAttribute("title").trim();
          }
        }
        if (!title && imgEl && imgEl.alt && imgEl.alt.length > 3) {
          title = imgEl.alt.trim();
        }
        if (!title) {
          var cardText = (card ? card.innerText : a.innerText) || "";
          var lines = cardText.split("\n").map(function(s){ return s.trim(); }).filter(Boolean);
          for (var i = 0; i < lines.length; i++) {
            if (!lines[i].includes("₹") && !lines[i].includes("\u20b9") && !lines[i].includes("%") && lines[i].length > 3) {
              title = lines[i];
              break;
            }
          }
        }
        if (!title || title === "Product") {
          title = extractTitleFromUrl(href) || "Product";
        }

        /* Comprehensive Out-of-Stock Detection ("Currently unavailable", "Notify Me", etc.) */
        var isOos = /currently\s*unavailable|unavailable|out\s*of\s*stock|sold\s*out|notify\s*me/i.test((card ? card.innerText : a.innerText) || "") ||
                    !!(card && card.querySelector('button[disabled], [class*="unavailable" i], [class*="outOfStock" i], [class*="notify" i], [aria-label*="notify" i]'));

        if (addProduct(title, fsp, mrp, disc, img, href, isOos)) count++;
      } catch (e) {}
    });
    return count;
  }

  /* Safe URI sanitizer ensuring sid query parameter slashes are encoded as %2F */
  function sanitizePageUri(uri) {
    if (!uri) return "";
    var u = uri.startsWith("http") ? uri.replace(/^https?:\/\/[^\/]+/, "") : uri;
    return u.replace(/([?&]sid=)([^&]+)/gi, function(match, prefix, val) {
      return prefix + val.replace(/\//g, "%2F");
    });
  }

  /* Get user agent header with required mobile token for Rome API WAF */
  function getXUserAgent() {
    var ua = navigator.userAgent || "";
    if (ua.includes("FKUA/msite")) return ua;
    return ua + " FKUA/msite/0.0.4/msite/Mobile";
  }

  /* Get active pincode dynamically from session state, cookies, or storage */
  function getActivePincode() {
    try {
      if (window.__INITIAL_STATE__) {
        var s = window.__INITIAL_STATE__;
        var pc = s.multiWidgetState?.pincode?.pincode || 
                 s.multiWidgetState?.pincode?.systemPincode ||
                 s.multiWidgetState?.appContext?.meta?.pc ||
                 s.pageDataResponse?.pageData?.pageContext?.pincode ||
                 s.pageData?.pageContext?.pincode;
        if (pc && /^[0-9]{6}$/.test(String(pc))) return parseInt(pc, 10);
      }
    } catch(e) {}
    try {
      var m = document.cookie.match(/(?:^|;\s*)(?:pincode|snPincode|deliveryPincode)=([0-9]{6})/i);
      if (m) return parseInt(m[1], 10);
    } catch(e) {}
    try {
      var stored = localStorage.getItem("pincode") || sessionStorage.getItem("pincode");
      if (stored && /^[0-9]{6}$/.test(stored)) return parseInt(stored, 10);
    } catch(e) {}
    return 560032;
  }

  /* Extract active session & query context for Rome API */
  function getRequestContext() {
    var ctx = { type: "BROWSE_PAGE" };
    try {
      if (window.__INITIAL_STATE__) {
        var s = window.__INITIAL_STATE__;
        var rc = s.multiWidgetState?.pageDataResponse?.requestContext || 
                 s.pageDataResponse?.requestContext || 
                 s.requestContext;
        if (rc?.ssid) ctx.ssid = rc.ssid;
        if (rc?.sqid) ctx.sqid = rc.sqid;
      }
    } catch(e) {}
    return ctx;
  }

  /* Fetch page data using Flipkart Rome API with automatic 302 redirection resolution */
  async function fetchRomePage(pageUri, redirectCount) {
    if (!pageUri) return null;
    redirectCount = redirectCount || 0;
    if (redirectCount > 2) return null;

    var cleanUri = sanitizePageUri(pageUri);
    var bodyPayload = {
      pageUri: cleanUri,
      pageContext: {
        trackingContext: {
          context: {
            eVar51: "neo/merchandising",
            eVar61: "creative_card"
          }
        },
        networkSpeed: 1700
      },
      requestContext: getRequestContext(),
      locationContext: {
        pincode: getActivePincode(),
        changed: false
      }
    };

    try {
      var resp = await fetch("https://1.rome.api.flipkart.com/api/4/page/fetch?cacheFirst=false", {
        headers: {
          "accept": "*/*",
          "accept-language": "en-US,en;q=0.9",
          "content-type": "application/json",
          "flipkart_secure": "true",
          "x-user-agent": getXUserAgent()
        },
        body: JSON.stringify(bodyPayload),
        method: "POST",
        mode: "cors",
        credentials: "omit"
      });
      if (resp.ok) {
        var json = await resp.json();
        /* Handle internal 302 redirection (e.g. to /hyperlocal-preview-page) */
        var slots = json.RESPONSE?.slots || json.slots || [];
        var redir = json.RESPONSE?.pageMeta?.redirectionObject || json.pageMeta?.redirectionObject;
        if ((!slots || slots.length === 0) && redir && redir.url) {
          var targetPath = redir.url;
          if (targetPath.startsWith("http")) {
            try {
              var parsedUrl = new URL(targetPath);
              targetPath = parsedUrl.pathname + parsedUrl.search;
            } catch(e) {
              targetPath = targetPath.replace(/^https?:\/\/[^\/]+/, "");
            }
          }
          if (targetPath && targetPath !== cleanUri) {
            var redirectedJson = await fetchRomePage(targetPath, redirectCount + 1);
            if (redirectedJson) return redirectedJson;
          }
        }
        return json;
      }
    } catch(e) {}
    return null;
  }

  /* Fetch full HTML of any Flipkart page with session cookies (fallback) */
  async function fetchCategoryHtml(uri) {
    var cleanUri = sanitizePageUri(uri);
    var url = cleanUri.startsWith("http") ? cleanUri : ("https://www.flipkart.com" + cleanUri);
    try {
      var resp = await fetch(url, {
        method: "GET",
        credentials: "include"
      });
      if (!resp.ok) return null;
      return await resp.text();
    } catch(e) {
      return null;
    }
  }

  /* Extract __INITIAL_STATE__ JSON reliably without regex backtracking */
  function extractStateJsonFromHtml(html) {
    if (!html) return null;
    var startIdx = html.indexOf("window.__INITIAL_STATE__");
    if (startIdx === -1) return null;
    var jsonStart = html.indexOf("{", startIdx);
    if (jsonStart === -1) return null;
    var scriptEnd = html.indexOf("</script>", jsonStart);
    if (scriptEnd === -1) return null;
    var jsonEnd = html.lastIndexOf("}", scriptEnd);
    if (jsonEnd <= jsonStart) return null;
    try {
      return JSON.parse(html.substring(jsonStart, jsonEnd + 1));
    } catch(e) {
      return null;
    }
  }

  /* Parse products from raw HTML text (via __INITIAL_STATE__ + DOMParser) */
  function parseHtmlString(html) {
    var count = 0;
    if (!html) return 0;

    /* 1. Extract window.__INITIAL_STATE__ safely */
    try {
      var json = extractStateJsonFromHtml(html);
      if (json) {
        var pData = json.multiWidgetState?.pageDataResponse || json.multiWidgetState || json.pageDataResponse || json;
        count += parseProducts(pData);
      }
    } catch(e) {}

    /* 2. Also parse DOM with DOMParser as guaranteed fallback */
    try {
      var parser = new DOMParser();
      var doc = parser.parseFromString(html, "text/html");
      count += parseDomProducts(doc);
    } catch(e) {}

    return count;
  }

  /* Unified page fetcher: Attempts Rome API first, with fallback to HTML if needed */
  async function fetchAndParsePage(uri) {
    if (!uri) return { count: 0 };
    var json = await fetchRomePage(uri);
    if (json) {
      var c = parseProducts(json);
      if (c > 0) return { count: c, json: json };
    }
    /* Fallback to HTML if API returned 0 deals */
    var html = await fetchCategoryHtml(uri);
    if (html) {
      var c2 = parseHtmlString(html);
      return { count: c2, html: html, json: json };
    }
    return { count: 0, json: json };
  }

  /* Extract subcategory links from Rome API JSON slots */
  function extractSubcategoriesFromJson(json) {
    var subcats = [];
    var seen = new Set();
    if (!json) return subcats;
    var slots = json.RESPONSE?.slots || json.slots || json.pageData?.slots || json.multiWidgetState?.widgetsData?.slots || json.multiWidgetState?.pageDataResponse?.slots || [];
    slots.forEach(function(s){
      var w = s.widget || {};
      var wdata = w.data || {};

      /* Format 1: STICKY_NAVIGATION_CARD_WIDGET */
      if (w.type === "STICKY_NAVIGATION_CARD_WIDGET" || w.viewType === "CATEGORY_FILTER_VIEW") {
        var comps = wdata.renderableComponents || [];
        comps.forEach(function(c){
          var url = c.action?.url || c.action?.originalUrl || "";
          var title = c.value?.contentTitle?.text || c.action?.tracking?.contentTitle || "";
          if (url) {
            var sUrl = sanitizePageUri(url);
            if (!seen.has(sUrl)) {
              seen.add(sUrl);
              subcats.push({ title: title.trim() || "Subcategory", url: sUrl });
            }
          }
        });
      }

      /* Format 2: ATLAS_WIDGET with vertical-sticky-navigation-side-rail */
      if (w.viewType === "vertical-sticky-navigation-side-rail" || w.widgetName?.includes("CATEGORY_FILTER_VIEW") || w.widgetType?.includes("CATEGORY_FILTER_VIEW")) {
        var dls = wdata.dlsData || {};
        for (var k in dls) {
          if (k.indexOf("scrollToListData") !== -1 || k.indexOf("scroll") !== -1 || k.indexOf("horizontalListData") !== -1) {
            var list = dls[k]?.value || [];
            if (Array.isArray(list)) {
              list.forEach(function(card){
                var cval = card?.value || {};
                var action = cval.SelectionViewData_0?.action || cval.row_0?.action || cval.col_0?.action || {};
                var url = action.url || action.originalUrl || "";
                var title = cval.label_0?.value?.text || cval.trackerData_0?.tracking?.contentTitle || cval.trackerData_0?.tracking?.widgetContent || "";
                if (url) {
                  var sUrl = sanitizePageUri(url);
                  if (!seen.has(sUrl)) {
                    seen.add(sUrl);
                    subcats.push({ title: title.trim() || "Subcategory", url: sUrl });
                  }
                }
              });
            }
          }
        }
      }
    });
    return subcats;
  }

  /* Extract subcategory links from category HTML (via __INITIAL_STATE__ + DOMParser + Regex) */
  function extractSubcategoriesFromHtml(html) {
    var subcats = [];
    var seen = new Set();
    if (!html) return subcats;

    /* A. Search inside window.__INITIAL_STATE__ JSON for navigation widgets */
    try {
      var json = extractStateJsonFromHtml(html);
      if (json) {
        var pData = json.multiWidgetState?.pageDataResponse || json.multiWidgetState || json.pageDataResponse || json;
        subcats = extractSubcategoriesFromJson(pData);
        if (subcats.length > 0) return subcats;
      }
    } catch(e) {}

    /* B. Search via DOMParser */
    try {
      var parser = new DOMParser();
      var doc = parser.parseFromString(html, "text/html");
      doc.querySelectorAll('a[href*="/hyperlocal/hloc/"], a[href*="sid=hloc"]').forEach(function(a){
        var href = a.getAttribute("href") || "";
        var title = a.innerText.trim();
        if (href && title && href.includes("/pr?")) {
          var sUrl = sanitizePageUri(href);
          if (!seen.has(sUrl)) {
            seen.add(sUrl);
            subcats.push({ title: title, url: sUrl });
          }
        }
      });
    } catch(e) {}

    /* C. Search via Regex for subcategory patterns */
    try {
      var urlMatches = html.matchAll(/\/hyperlocal\/hloc\/[a-z0-9]+\/pr\?sid=[^"&'\s]+/gi);
      for (var match of urlMatches) {
        var u = sanitizePageUri(match[0]);
        if (!seen.has(u)) {
          seen.add(u);
          subcats.push({ title: "Subcategory", url: u });
        }
      }
    } catch(e) {}

    return subcats;
  }

  /* Search Flipkart Minutes via Rome API */
  async function startSearch(query) {
    if (!query || !query.trim()) {
      setStatus("Enter search keyword");
      return;
    }
    query = query.trim();
    st.searchQuery = query;
    window.fkDealsStop = false;
    st.mode = "RUN";
    if (btnSearch) {
      btnSearch.textContent = "Stop ⏹";
      btnSearch.className = "fkd-pill fkd-pill-danger";
    }

    st.items = [];
    st.seen.clear();
    renderGrid();

    setStatus(`Searching "${query}"...`);
    var sortParam = (st.sort === "discount") ? "&sort=discount" : "&sort=price_asc";
    var searchUri = "/hyperlocal/pr?q=" + encodeURIComponent(query) + "&marketplace=HYPERLOCAL&searchSourceContext=experience%3D&widgetUniqueId=1&sid=search.flipkart.com&as-show=on" + sortParam;

    await fetchAndParsePage(searchUri);
    renderGrid();

    /* Try Page 2 if still running and found items */
    if (st.mode === "RUN" && !window.fkDealsStop && st.items.length > 0) {
      setStatus(`Loading more "${query}"...`);
      var p2Uri = searchUri + "&page=2";
      await fetchAndParsePage(p2Uri);
      renderGrid();
    }

    stopAll();
    var finalIn = st.items.filter(function(x){ return !x.oos; }).length;
    setStatus(`Search done! ${st.items.length} items (${finalIn} in stock)`);
  }

  /* Main Category & Subcategory Looping Engine (ZERO AUTO-SCROLL) */
  async function startCategoryFetch() {
    closeCatDrawer();
    window.fkDealsStop = false;
    st.mode = "RUN";
    btnFetch.textContent = "Stop ⏹";
    btnFetch.className = "fkd-pill fkd-pill-danger";

    /* 1. Clear items on new fetch so we don't display items from previous page */
    st.items = [];
    st.seen.clear();
    renderGrid();

    var targetUri = st.selectedMode;
    var catId = st.selectedCatId;

    /* Mode: Selected Category */
    setStatus("Loading category deals...");

    /* 2. Check pre-mapped subcategories first */
    var subcategories = [];
    if (PRESET_SUBCATS[catId]) {
      subcategories = PRESET_SUBCATS[catId].slice();
    }

    /* 3. If not pre-mapped, fetch category page to discover subcategories and parse Page 1 deals */
    if (!subcategories.length) {
      setStatus("Discovering deals & subcategories...");
      var p1Uri = targetUri + (targetUri.includes("?") ? "&" : "?") + "sort=discount";
      var pageRes = await fetchAndParsePage(p1Uri);
      renderGrid();
      if (pageRes.json) {
        subcategories = extractSubcategoriesFromJson(pageRes.json);
      }
      if (!subcategories.length && pageRes.html) {
        subcategories = extractSubcategoriesFromHtml(pageRes.html);
      }
    }

    /* 4. If subcategories available, loop Page 1 for each */
    if (subcategories.length > 0) {
      setStatus(`Scanning ${subcategories.length} subcategories...`);
      for (var idx = 0; idx < subcategories.length; idx++) {
        if (st.mode !== "RUN" || window.fkDealsStop) break;
        var sub = subcategories[idx];
        var subUri = sub.url;
        if (!subUri.includes("sort=discount")) {
          subUri += (subUri.includes("?") ? "&" : "?") + "sort=discount";
        }
        setStatus(`[${idx+1}/${subcategories.length}] ${sub.title}...`);
        await fetchAndParsePage(subUri);
        renderGrid();
        await new Promise(function(r){ setTimeout(r, 350); });
      }
    }

    /* 5. Multi-page: If no subcategories exist OR subcategories yielded 0 items, fetch pages of targetUri */
    if (st.items.length === 0 || subcategories.length === 0) {
      if (PRESET_SUBCATS[catId]) {
        setStatus("Fetching category deals...");
        var p1 = targetUri + (targetUri.includes("?") ? "&" : "?") + "sort=discount";
        await fetchAndParsePage(p1);
        renderGrid();
      }

      var pageNum = 2;
      while (st.mode === "RUN" && !window.fkDealsStop && pageNum <= 4) {
        setStatus(`Fetching Page ${pageNum} deals...`);
        var pUri = targetUri + (targetUri.includes("?") ? "&" : "?") + "sort=discount&page=" + pageNum;
        var pRes = await fetchAndParsePage(pUri);
        renderGrid();
        if (!pRes.count && !pRes.json?.RESPONSE?.pageData?.hasMorePages) break;
        pageNum++;
        await new Promise(function(r){ setTimeout(r, 350); });
      }
    }

    stopAll();
    var finalIn = st.items.filter(function(x){ return !x.oos; }).length;
    setStatus(`Done! Found ${st.items.length} (${finalIn} in stock)`);
  }

  /* Initialize */
  setStatus("Ready - Select a category or search");
})();
