import json
import re
import urllib.parse
import urllib.request
import ssl
from . import config

ctx = ssl.create_default_context()

def extract_title_from_url(url):
    """Derives a capitalized product name from its URL slug."""
    if not url:
        return ""
    m = re.search(r"/([a-z0-9][a-z0-9-]+[a-z0-9])/p/(?:itm|[a-z0-9]+)", url, re.I)
    if m and m.group(1):
        slug = m.group(1).replace("-", " ").strip()
        if len(slug) > 3:
            return slug.title()
    return ""

def sanitize_page_uri(uri):
    """Encodes slashes inside the sid query parameter as %2F."""
    if not uri:
        return ""
    u = uri
    if u.startswith("http"):
        parsed = urllib.parse.urlparse(u)
        u = parsed.path + ("?" + parsed.query if parsed.query else "")
    return re.sub(r'([?&]sid=)([^&]+)', lambda m: m.group(1) + m.group(2).replace("/", "%2F"), u)

def build_product_link(base_lnk, cval=None, stepper_action=None):
    """
    Constructs a complete Flipkart Minutes product link.
    Ensures marketplace=HYPERLOCAL, lid (listingId), and shopId are attached
    so opening the link routes directly to Flipkart Minutes.
    """
    if not base_lnk:
        return ""
    if not base_lnk.startswith("http"):
        base_lnk = "https://www.flipkart.com" + base_lnk

    cval = cval or {}
    stepper_action = stepper_action or {}
    stepper_params = stepper_action.get("params", {})
    stepper_tracking = stepper_action.get("tracking", {})
    col0_params = cval.get("col_0", {}).get("action", {}).get("params", {})
    tracker_tracking = cval.get("trackerData_0", {}).get("tracking", {})

    lid = (stepper_params.get("listingId") or
           stepper_params.get("lid") or
           stepper_tracking.get("lid") or
           stepper_tracking.get("listingId") or
           col0_params.get("listingId") or
           col0_params.get("lid") or
           tracker_tracking.get("lid") or
           tracker_tracking.get("listingId") or "")

    shop_id = (stepper_params.get("shopId") or
               stepper_tracking.get("shopId") or
               col0_params.get("shopId") or
               tracker_tracking.get("shopId") or "")

    parsed = urllib.parse.urlparse(base_lnk)
    qs = urllib.parse.parse_qs(parsed.query)

    # Always ensure marketplace is HYPERLOCAL so the link opens in Minutes
    if "marketplace" not in qs:
        qs["marketplace"] = ["HYPERLOCAL"]

    if lid and "lid" not in qs:
        qs["lid"] = [lid]

    if shop_id and "shopId" not in qs:
        qs["shopId"] = [shop_id]

    new_query = urllib.parse.urlencode(qs, doseq=True)
    return urllib.parse.urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))

class FlipkartScraper:
    def __init__(self, pincode=None):
        self.pincode = int(pincode or config.DEFAULT_PINCODE)
        self.session_cookies = {
            "snPincode": str(self.pincode),
            "deliveryPincode": str(self.pincode),
            "pincode": str(self.pincode)
        }

        # Parse FLIPKART_COOKIE
        raw_cookie = (config.FLIPKART_COOKIE or "").strip()
        if raw_cookie.lower().startswith("cookie:"):
            raw_cookie = raw_cookie[7:].strip()
        raw_cookie = raw_cookie.strip(' "\'')

        if raw_cookie:
            for item in raw_cookie.split(";"):
                item = item.strip()
                if "=" in item:
                    k, v = item.split("=", 1)
                    self.session_cookies[k.strip()] = v.strip()

        # If cookie has a specific pincode set and caller used default, align pincode with cookie
        cookie_pc = self.session_cookies.get("snPincode") or self.session_cookies.get("deliveryPincode") or self.session_cookies.get("pincode")
        if cookie_pc and re.match(r"^\d{6}$", cookie_pc):
            if not pincode or str(pincode) == str(config.DEFAULT_PINCODE):
                self.pincode = int(cookie_pc)
                self.session_cookies["snPincode"] = cookie_pc
                self.session_cookies["deliveryPincode"] = cookie_pc
                self.session_cookies["pincode"] = cookie_pc

    def fetch_rome_page(self, page_uri, redirect_count=0):
        """Fetches a page from Rome API, automatically following 302 redirects."""
        if redirect_count > 3:
            return None

        clean_uri = sanitize_page_uri(page_uri)

        payload = {
            "pageUri": clean_uri,
            "pageContext": {
                "trackingContext": {
                    "context": {
                        "eVar51": "neo/merchandising",
                        "eVar61": "creative_card"
                    }
                },
                "networkSpeed": 1700
            },
            "requestContext": {
                "type": "BROWSE_PAGE"
            },
            "locationContext": {
                "pincode": self.pincode,
                "changed": False
            }
        }

        headers = dict(config.DEFAULT_HEADERS)
        if self.session_cookies:
            headers["cookie"] = "; ".join([f"{k}={v}" for k, v in self.session_cookies.items()])

        req = urllib.request.Request(
            config.ROME_API_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, context=ctx, timeout=12) as res:
                if res.status != 200:
                    return None
                data = res.read().decode("utf-8")
                parsed_json = json.loads(data)

                # Capture session tokens if returned
                session_info = parsed_json.get("SESSION", {})
                if session_info.get("sn"):
                    self.session_cookies["SN"] = session_info["sn"]
                if session_info.get("at"):
                    self.session_cookies["at"] = session_info["at"]

                # Handle internal 302 redirect
                slots = parsed_json.get("RESPONSE", {}).get("slots", [])
                redir = parsed_json.get("RESPONSE", {}).get("pageMeta", {}).get("redirectionObject", {})
                redir_url = redir.get("url")

                if (not slots or len(slots) == 0) and redir_url:
                    redir_parsed = urllib.parse.urlparse(redir_url)
                    target_path = redir_parsed.path + ("?" + redir_parsed.query if redir_parsed.query else "")
                    if target_path and target_path != clean_uri:
                        return self.fetch_rome_page(target_path, redirect_count + 1)

                return parsed_json
        except Exception:
            return None

    def parse_products_from_json(self, json_data):
        """Extracts products from Rome API JSON payload."""
        products = []
        seen_uids = set()

        if not json_data:
            return products

        resp = json_data.get("RESPONSE", {})
        slots = resp.get("slots", []) or json_data.get("slots", [])

        for s in slots:
            wdata = s.get("widget", {}).get("data", {})
            comps = wdata.get("products", []) or wdata.get("renderableComponents", [])

            for item in comps:
                try:
                    pinfo = item.get("productInfo", item)
                    v = pinfo.get("value", pinfo)
                    pricing = v.get("pricing", {})
                    final_price = pricing.get("finalPrice", {})

                    if final_price and final_price.get("value"):
                        fsp = int(final_price.get("value", 0))
                        mrp = fsp
                        prices = pricing.get("prices", [])
                        for p in prices:
                            if p.get("priceType") == "MRP":
                                mrp = int(p.get("value", fsp))
                                break

                        disc = pricing.get("totalDiscount", 0)
                        base_url = v.get("baseUrl") or v.get("smartUrl") or ""
                        raw_lnk = ("https://www.flipkart.com" + base_url) if base_url else ""
                        lnk = build_product_link(raw_lnk, cval={"trackerData_0": {"tracking": {"lid": v.get("listingId")}}})

                        titles = v.get("titles", {})
                        title = (titles.get("title") or titles.get("newTitle") or titles.get("superTitle") or
                                 v.get("productTitle") or extract_title_from_url(lnk) or "Product")

                        images = v.get("media", {}).get("images", []) or v.get("images", [])
                        img = images[0].get("url", "") if images else ""
                        img = img.replace("{@width}", "400").replace("{@height}", "400").replace("?q={@quality}", "?q=80")

                        is_oos = (v.get("availability", {}).get("displayState") == "OUT_OF_STOCK" or
                                  v.get("productAction", {}).get("value", {}).get("enabled") is False or
                                  v.get("productAction", {}).get("value", {}).get("actionType") == "NOTIFY_ME" or
                                  v.get("buyability", {}).get("intent") == "negative" or
                                  v.get("action", {}).get("params", {}).get("isAvailable") is False)

                        prod = self._normalize_product(title, fsp, mrp, disc, img, lnk, is_oos)
                        if prod and prod["id"] not in seen_uids:
                            seen_uids.add(prod["id"])
                            products.append(prod)
                except Exception:
                    continue

            # Check dlsData (MRCSV / carousels / grids) - Case A (snb_hl_text_0)
            dls = wdata.get("dlsData", {})
            for k, wrapper in dls.items():
                if any(x in k for x in ("MRCSV", "carouselData", "gridData", "horizontalListData")):
                    card_list = wrapper.get("value", [])
                    if not isinstance(card_list, list):
                        continue

                    for card_wrap in card_list:
                        try:
                            cval = card_wrap.get("value", {}) if isinstance(card_wrap, dict) else {}
                            snb_text = cval.get("snb_hl_text_0", {}).get("value")
                            if snb_text:
                                col0 = cval.get("col_0", {}).get("action", {})
                                raw_lnk = col0.get("url") or col0.get("originalUrl") or ""
                                stepper = cval.get("stepperData_0", {}).get("action", {})

                                # Build complete Minutes product link with HYPERLOCAL, lid, and shopId
                                lnk = build_product_link(raw_lnk, cval=cval, stepper_action=stepper)

                                title = (snb_text.get("label_0", {}).get("value", {}).get("text") or
                                         snb_text.get("label_1", {}).get("value", {}).get("text") or
                                         cval.get("trackerData_0", {}).get("tracking", {}).get("contentTitle") or
                                         extract_title_from_url(lnk) or "Product")

                                # Prices
                                fsp = 0
                                l4 = snb_text.get("label_4", {}).get("value", "")
                                l4_str = str(l4.get("UNLOCKED", {}).get("value", {}).get("params", {}).get("defaultValue") or l4.get("text", "") if isinstance(l4, dict) else l4)
                                m_fsp = re.search(r"\d+", l4_str)
                                if m_fsp:
                                    fsp = int(m_fsp.group(0))

                                mrp = fsp
                                l3 = snb_text.get("label_3", {}).get("value", "")
                                l3_str = str(l3.get("params", {}).get("defaultValue") or l3.get("text", "") if isinstance(l3, dict) else l3)
                                m_mrp = re.search(r"\d+", l3_str)
                                if m_mrp:
                                    mrp = int(m_mrp.group(0))

                                disc = 0
                                l2 = snb_text.get("label_2", {}).get("value", "")
                                l2_str = str(l2.get("params", {}).get("defaultValue") or l2.get("text", "") if isinstance(l2, dict) else l2)
                                m_disc = re.search(r"(\d+)%", l2_str)
                                if m_disc:
                                    disc = int(m_disc.group(1))

                                if not fsp and stepper.get("params", {}).get("price"):
                                    fsp = int(stepper["params"]["price"])
                                if not fsp and stepper.get("tracking", {}).get("fsp"):
                                    fsp = int(stepper["tracking"]["fsp"])
                                if stepper.get("tracking", {}).get("mrp"):
                                    mrp = int(stepper["tracking"]["mrp"])

                                is_oos = (stepper.get("tracking", {}).get("isAvailable") == "false" or
                                          stepper.get("enabled") is False or
                                          cval.get("action", {}).get("params", {}).get("isAvailable") is False)

                                img = col0.get("params", {}).get("imageUrl") or stepper.get("params", {}).get("productImage") or ""
                                img = img.replace("{@width}", "400").replace("{@height}", "400").replace("?q={@quality}", "?q=80")

                                prod = self._normalize_product(title, fsp, mrp, disc, img, lnk, is_oos)
                                if prod and prod["id"] not in seen_uids:
                                    seen_uids.add(prod["id"])
                                    products.append(prod)
                        except Exception:
                            continue
        return products

    def _normalize_product(self, title, fsp, mrp, disc, img, lnk, is_oos):
        """Validates, cleans up pricing bugs, and builds uniform product object."""
        if not fsp or fsp <= 0:
            return None

        title = title.strip()
        if not title or title == "Product":
            title = extract_title_from_url(lnk) or "Flipkart Minutes Item"

        if not mrp or mrp <= 0:
            mrp = fsp

        # If fsp > mrp, swap
        if fsp > mrp:
            fsp, mrp = mrp, fsp

        # If disc > 0 and fsp == mrp, derive fsp
        if 0 < disc < 100 and fsp == mrp:
            fsp = round(mrp * (1 - disc / 100))

        # Re-verify disc
        if not disc or disc <= 0 or disc >= 100:
            disc = round(((mrp - fsp) / mrp) * 100) if mrp > fsp else 0

        # Fix concatenated discount bug (e.g. mrp 75037 -> 750 with 37% disc)
        if mrp > fsp * 4 and disc > 0 and str(mrp).endswith(str(disc)):
            clean_mrp = int(str(mrp)[:-len(str(disc))])
            if clean_mrp >= fsp:
                mrp = clean_mrp
                disc = round(((mrp - fsp) / mrp) * 100)

        uid = f"{title}_{fsp}"
        return {
            "id": uid,
            "title": title,
            "fsp": fsp,
            "mrp": mrp,
            "discount": disc,
            "image": img,
            "link": lnk,
            "oos": bool(is_oos)
        }

    def extract_subcategories(self, json_data):
        """Extracts subcategories from navigation widgets in the Rome API JSON."""
        subcats = []
        seen = set()
        if not json_data:
            return subcats

        resp = json_data.get("RESPONSE", {})
        slots = resp.get("slots", []) or json_data.get("slots", [])

        clutter_terms = [
            "diaper", "baby", "mobile", "cable", "case", "cover", "earphone", "headphone",
            "speaker", "gadget", "appliance", "kitchen", "cookware", "toy", "stationery",
            "electrical", "tool", "bedding", "furnishing", "fashion"
        ]

        def is_clutter(name, url):
            text = (name + " " + url).lower()
            return any(t in text for t in clutter_terms)

        for s in slots:
            w = s.get("widget", {})
            wtype = w.get("type", "")
            view_type = w.get("viewType", "")
            wname = w.get("widgetName", "")
            wdata = w.get("data", {})

            # Format 1: STICKY_NAVIGATION_CARD_WIDGET
            if wtype == "STICKY_NAVIGATION_CARD_WIDGET" or view_type == "CATEGORY_FILTER_VIEW":
                comps = wdata.get("renderableComponents", [])
                for c in comps:
                    action = c.get("action", {})
                    url = action.get("url") or action.get("originalUrl") or ""
                    title = c.get("value", {}).get("contentTitle", {}).get("text") or action.get("tracking", {}).get("contentTitle") or ""
                    if url and not is_clutter(title, url):
                        s_url = sanitize_page_uri(url)
                        if s_url not in seen:
                            seen.add(s_url)
                            subcats.append({"name": title.strip() or "Subcategory", "uri": s_url})

            # Format 2: ATLAS_WIDGET with vertical-sticky-navigation-side-rail
            if view_type == "vertical-sticky-navigation-side-rail" or "CATEGORY_FILTER_VIEW" in wname:
                dls = wdata.get("dlsData", {})
                for k, val in dls.items():
                    if "scroll" in k or "horizontalListData" in k or "scrollToListData" in k:
                        card_list = val.get("value", []) if isinstance(val, dict) else []
                        if isinstance(card_list, list):
                            for card in card_list:
                                cval = card.get("value", {}) if isinstance(card, dict) else {}
                                action = (cval.get("SelectionViewData_0", {}).get("action") or
                                          cval.get("row_0", {}).get("action") or
                                          cval.get("col_0", {}).get("action") or {})
                                url = action.get("url") or action.get("originalUrl") or ""
                                title = (cval.get("label_0", {}).get("value", {}).get("text") or
                                         cval.get("trackerData_0", {}).get("tracking", {}).get("contentTitle") or
                                         cval.get("trackerData_0", {}).get("tracking", {}).get("widgetContent") or "")
                                if url and not is_clutter(title, url):
                                    s_url = sanitize_page_uri(url)
                                    if s_url not in seen:
                                        seen.add(s_url)
                                        subcats.append({"name": title.strip() or "Subcategory", "uri": s_url})

        return subcats

    def fetch_category_deals(self, category_info):
        """Fetches and parses Page 1 deals for a single category, and extracts side-rail subcategories."""
        uri = category_info.get("uri", "")
        cat_name = category_info.get("name", "Category")
        json_data = self.fetch_rome_page(uri)
        products = self.parse_products_from_json(json_data)
        for p in products:
            p["category"] = cat_name
        discovered_subcats = self.extract_subcategories(json_data)
        return products, discovered_subcats
