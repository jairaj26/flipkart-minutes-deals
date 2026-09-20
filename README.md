# ⚡ Flipkart Minutes Deals Finder

A fast, lightweight, client-side browser bookmarklet that scans Flipkart Minutes hyperlocal departments in the background, extracts top deals with true selling prices and discounts, and renders a floating deal finder sidebar — **with zero manual page scrolling**.

Works smoothly on **PC, Mac, Android (Chrome/Edge), and iOS (Safari)**.

👉 **[Launch the Live Web Installer](https://jairaj26.github.io/flipkart-minutes-deals/)** for 1-click drag & drop installation on PC or 1-tap copy on mobile!

---

## ✨ Features

- 🛍️ **38+ Hyperlocal Departments**: Pre-configured with verified Flipkart Minutes categories (Fresh Fruits, Dairy & Bread, Snacks & Namkeen, Chocolates, Electronics, Kitchen Essentials, and more).
- ⚡ **Background Fetching**: Concurrently queries subcategories in the background — no need to scroll through endless pages.
- 💰 **Accurate Price & Discount Extraction**:
  - Distinguishes between discounted **Selling Price (FSP)** and strikethrough **MRP**.
  - Prevents concatenated number bugs (e.g. ₹750 MRP with 37% off correctly shows as ₹472 selling price, ₹750 MRP, 37% OFF).
- 📦 **In-Stock & Out-of-Stock Filter**: One-tap toggle to hide or view out-of-stock and "Currently unavailable" items.
- 🔍 **Real-Time Search**: Search products across the current department or active catalog with instant filtering.
- 📱 **Responsive & Mobile Compatible**: Designed for mobile and desktop screens with equal-sized controls and a non-intrusive collapsible pill.
- 🔄 **Always Up to Date**: The one-line loader pulls the latest updates directly from this GitHub repository.

---

## 🚀 Installation & Usage

### 💻 On PC / Mac / Desktop (Chrome, Edge, Brave, Firefox, Safari)

#### Option 1: 1-Click Drag & Drop (Recommended)
1. Open the **[⚡ Live Web Installer](https://jairaj26.github.io/flipkart-minutes-deals/)** in your browser *(or open `index.html` locally on your computer)*.
2. Ensure your Bookmarks Bar is visible:
   - **Windows / Linux**: Press <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>B</kbd>
   - **Mac**: Press <kbd>Cmd</kbd> + <kbd>Shift</kbd> + <kbd>B</kbd>
3. Drag the blue **⚡ Minutes Deals** button directly onto your Bookmarks Bar.
4. Visit [flipkart.com](https://www.flipkart.com) and click the bookmark!

#### Option 2: Direct Manual Bookmark Creation (Without opening installer)
1. In your browser, create a new bookmark (or right-click your bookmarks bar $\rightarrow$ **Add Page**).
2. Set the Name to: `⚡ Flipkart Deals`
3. Set the URL to the following one-line loader script:

```javascript
javascript:(function(){if(window.__FK_MINUTES_LOADING__)return;window.__FK_MINUTES_LOADING__=true;fetch('https://raw.githubusercontent.com/jairaj26/flipkart-minutes-deals/main/FKMinutes_Readable.js?t='+Date.now()).then(function(r){if(!r.ok)throw new Error('HTTP '+r.status);return r.text();}).then(function(c){window.__FK_MINUTES_LOADING__=false;(1,eval)(c);}).catch(function(e){window.__FK_MINUTES_LOADING__=false;alert('Flipkart Minutes Loader: Failed to load ('+e.message+')');});})();
```

---

### 📱 On Mobile (Android Chrome & iOS Safari)

Mobile browsers don't allow drag-and-drop bookmarks. You can add the bookmarklet in under 1 minute:

#### Step 1: Copy the One-Line Script
Visit the **[⚡ Mobile Installer Page](https://jairaj26.github.io/flipkart-minutes-deals/)** to copy with 1 tap, or copy the script below:

```javascript
javascript:(function(){if(window.__FK_MINUTES_LOADING__)return;window.__FK_MINUTES_LOADING__=true;fetch('https://raw.githubusercontent.com/jairaj26/flipkart-minutes-deals/main/FKMinutes_Readable.js?t='+Date.now()).then(function(r){if(!r.ok)throw new Error('HTTP '+r.status);return r.text();}).then(function(c){window.__FK_MINUTES_LOADING__=false;(1,eval)(c);}).catch(function(e){window.__FK_MINUTES_LOADING__=false;alert('Flipkart Minutes Loader: Failed to load ('+e.message+')');});})();
```

#### Step 2: Create the Bookmark
- **Chrome / Edge on Android**:
  1. Open any webpage (e.g., this GitHub page).
  2. Tap the three dots menu (<kbd>⋮</kbd>) $\rightarrow$ Tap the **Star icon (★)** to bookmark the page.
  3. Tap **Edit** at the bottom notification (or open Bookmarks $\rightarrow$ tap <kbd>⋮</kbd> on the bookmark $\rightarrow$ **Edit**).
  4. Change the Name to: `Minutes Deals` (or `fk`).
  5. Delete the entire URL field and **paste** the copied script.
  6. Tap Back to save.

- **Safari on iOS (iPhone / iPad)**:
  1. Open any webpage in Safari.
  2. Tap the **Share icon** (square with upward arrow) $\rightarrow$ Tap **Add Bookmark**.
  3. Change the Name to: `Minutes Deals` and tap **Save**.
  4. Open your Bookmarks (book icon) $\rightarrow$ Tap **Edit** at the bottom $\rightarrow$ Tap `Minutes Deals`.
  5. Delete the URL and **paste** the copied script. Tap **Done**.

#### Step 3: Run on Flipkart
1. Open [flipkart.com](https://www.flipkart.com) in your mobile browser.
2. *(Important)* Make sure your delivery pincode or location is set so Flipkart Minutes items are available in your area.
3. Tap the **address bar** (where the URL is shown).
4. Type `Minutes Deals` (or `fk`).
5. In the dropdown search results, tap the **bookmark suggestion** with the star/folder icon.
6. The deals sidebar will immediately slide in on your screen!

---

## 🎮 Controls & Interface

| Control | Description |
| :--- | :--- |
| **Category Dropdown** | Choose from 38+ verified Flipkart Minutes departments. Automatically resets sort to discount. |
| **🔍 Search Box** | Type any keyword (e.g. `milk`, `chocolate`, `bread`) and hit Enter or click Search. |
| **Sort ₹** | Sort items by lowest selling price first. |
| **Sort %** | Sort items by highest discount percentage first (default). |
| **In Stock / All Items** | Toggle to show only in-stock items or include out-of-stock / "Currently unavailable" items. |
| **Fetch ⚡ / Stop ⏹** | Start or stop background scanning of all subcategories. |
| **Minimize (_)** | Collapses the sidebar into a floating badge at the bottom-right corner showing deal counts. |

---

## 📂 Project Structure

```
├── index.html                # Live GitHub Pages installer with 1-click drag & drop and mobile copy box
├── Install_Bookmarklet.html  # Standalone installation page
├── FKMinutes_Readable.js     # Clean, unminified source code with detailed comments
├── FKMinutes.txt             # Pre-built self-contained bookmarklet
├── FKMinutes_Compact.txt     # Minified single-line bookmarklet
└── README.md                 # Project documentation and setup guide
```

---

## 🛡️ Technical & Security Details

- **Content Security Policy (CSP) & CORS**:
  - The dynamic loader uses `fetch()` to retrieve the raw JavaScript from GitHub.
  - GitHub raw URLs serve with `Access-Control-Allow-Origin: *` (CORS enabled).
  - Flipkart's CSP policy permits wildcard connections (`connect-src 'self' *`) and script execution (`script-src 'unsafe-eval'`), allowing the loader to cleanly execute without CORS or CSP blocks.
- **Privacy**: The bookmarklet executes 100% locally in your browser. It does not collect, log, or send any personal data or session cookies to any external server.
- **Offline / Standalone Alternative**: If you prefer not to depend on GitHub's network availability, the full script in [`FKMinutes.txt`](FKMinutes.txt) can be pasted directly as a standalone bookmark with zero external calls.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
