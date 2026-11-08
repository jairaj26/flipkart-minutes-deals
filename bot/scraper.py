import json
import re
import urllib.parse
import urllib.request
import ssl
import requests
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

def extract_price(val):
    """Safely extracts integer price from any Flipkart Rome label structure, dict, or string."""
    if not val:
        return 0
    if isinstance(val, (int, float)):
        return int(val)
    if isinstance(val, str):
        m = re.search(r"\d+", val.replace(",", ""))
        return int(m.group(0)) if m else 0
    if isinstance(val, dict):
        for k in ("text", "defaultValue"):
            if k in val and val[k] is not None:
                p = extract_price(val[k])
                if p > 0:
                    return p
        if "params" in val and isinstance(val["params"], dict):
            p = extract_price(val["params"].get("defaultValue") or val["params"].get("price"))
            if p > 0:
                return p
        if "value" in val:
            p = extract_price(val["value"])
            if p > 0:
                return p
        for state in ("UNLOCKED", "LOCKED"):
            if state in val:
                p = extract_price(val[state])
                if p > 0:
                    return p
        if "tracking" in val and isinstance(val["tracking"], dict):
            p = extract_price(val["tracking"].get("fsp") or val["tracking"].get("mrp"))
            if p > 0:
                return p
    return 0

def sanitize_page_uri(uri):
    """Encodes slashes inside the sid query parameter as %2F."""
    if not uri:
        return ""
    u = uri
    if u.startswith("http"):
        parsed = urllib.parse.urlparse(u)
        u = parsed.path + ("?" + parsed.query if parsed.query else "")
    return re.sub(r'([?&]sid=)([^&]+)', lambda m: m.group(1) + m.group(2).replace("/", "%2F"), u)

def build_page_uri(base_uri, page_num):
    """Appends or updates the 'page' query parameter in a Flipkart Minutes page URI."""
    if not base_uri:
        return ""
    parsed = urllib.parse.urlparse(base_uri)
    qs = urllib.parse.parse_qs(parsed.query)
    qs["page"] = [str(page_num)]
    if "marketplace" not in qs:
        qs["marketplace"] = ["HYPERLOCAL"]
    if "sort" not in qs:
        qs["sort"] = ["discount"]
    new_query = urllib.parse.urlencode(qs, doseq=True)
    res = urllib.parse.urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))
    return sanitize_page_uri(res)

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

def extract_product_uid(lnk, title, fsp):
    """
    Extracts a robust unique product identifier from the deal link or fallback title+price.
    Checks for pid, itm, or lid in URL, and normalizes title.
    """
    if lnk:
        m_pid = re.search(r"[?&]pid=([a-zA-Z0-9_-]+)", lnk, re.I)
        if m_pid and m_pid.group(1):
            return f"pid_{m_pid.group(1)}"
        m_itm = re.search(r"/p/(itm[a-zA-Z0-9_-]+)", lnk, re.I)
        if m_itm and m_itm.group(1):
            return f"pid_{m_itm.group(1)}"
        m_lid = re.search(r"[?&]lid=([a-zA-Z0-9_-]+)", lnk, re.I)
        if m_lid and m_lid.group(1):
            return f"lid_{m_lid.group(1)}"
    norm_title = re.sub(r"\s+", " ", (title or "").lower()).strip()
    return f"{norm_title}_{fsp}"

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

        self.session = requests.Session()
        self.session.headers.update(config.DEFAULT_HEADERS)
        self.session.cookies.update(self.session_cookies)

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

        self.session.cookies.update(self.session_cookies)

        try:
            res = self.session.post(
                config.ROME_API_URL,
                json=payload,
                timeout=12
            )
            if res.status_code != 200:
                return None
            parsed_json = res.json()

            # Capture session tokens if returned
            session_info = parsed_json.get("SESSION", {})
            if session_info.get("sn"):
                self.session_cookies["SN"] = session_info["sn"]
                self.session.cookies.set("SN", session_info["sn"])
            if session_info.get("at"):
                self.session_cookies["at"] = session_info["at"]
                self.session.cookies.set("at", session_info["at"])

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
        """Extracts products from Rome API JSON payload or HTML state."""
        products = []
        seen_uids = set()

        if isinstance(json_data, str):
            idx = json_data.find("window.__INITIAL_STATE__")
            if idx != -1:
                j_start = json_data.find("{", idx)
                s_end = json_data.find("</script>", j_start)
                j_end = json_data.rfind("}", j_start, s_end)
                try:
                    json_data = json.loads(json_data[j_start:j_end+1])
                except Exception:
                    pass

        if not json_data or not isinstance(json_data, dict):
            return products

        resp = json_data.get("RESPONSE", {})
        slots = (resp.get("slots", []) or
                 json_data.get("slots", []) or
                 json_data.get("multiWidgetState", {}).get("widgetsData", {}).get("slots", []) or
                 json_data.get("multiWidgetState", {}).get("pageDataResponse", {}).get("slots", []))

        for raw_s in slots:
            s = raw_s.get("slotData", raw_s) if isinstance(raw_s, dict) else {}
            wdata = s.get("widget", {}).get("data", {})
            comps = wdata.get("products", []) or wdata.get("renderableComponents", [])

            for item in comps:
                try:
                    pinfo = item.get("productInfo", item)
                    v = pinfo.get("value", pinfo)
                    pricing = v.get("pricing", {})
                    final_price = pricing.get("finalPrice", {})

                    fsp = extract_price(final_price.get("value")) if final_price else 0
                    if fsp > 0:
                        mrp = fsp
                        prices = pricing.get("prices", [])
                        for p in prices:
                            ptype = str(p.get("priceType", "")).upper()
                            if ptype in ("MRP", "MAXIMUM_RETAIL_PRICE", "LIST_PRICE", "STRIKE_OFF", "STRIKEOFF") and p.get("value"):
                                p_val = extract_price(p.get("value"))
                                if p_val > 0:
                                    mrp = p_val
                                    break

                        if mrp == fsp and pricing.get("mrp"):
                            mrp = extract_price(pricing.get("mrp")) or mrp

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

                        disp_state = v.get("availability", {}).get("displayState")
                        is_oos = (disp_state not in (None, "", "IN_STOCK") or
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

            # Check dlsData (MRCSV / carousels / grids) - Case A (snb_hl_text_0) & Case B (product-card)
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
                                stepper = (cval.get("stepperData_0", {}).get("action", {}) or
                                           cval.get("snb_beauty_gmh_image_0", {}).get("value", {}).get("stepperData_0", {}).get("action", {}))

                                # Build complete Minutes product link with HYPERLOCAL, lid, and shopId
                                lnk = build_product_link(raw_lnk, cval=cval, stepper_action=stepper)

                                title = (snb_text.get("label_0", {}).get("value", {}).get("text") or
                                         snb_text.get("label_1", {}).get("value", {}).get("text") or
                                         cval.get("trackerData_0", {}).get("tracking", {}).get("contentTitle") or
                                         extract_title_from_url(lnk) or "Product")

                                # Prices with robust recursive extraction
                                p1 = extract_price(snb_text.get("label_4"))
                                p2 = extract_price(snb_text.get("label_3"))
                                if not p1 and stepper:
                                    p1 = extract_price(stepper.get("params", {}).get("price") or stepper.get("tracking", {}).get("fsp"))
                                if not p2 and stepper:
                                    p2 = extract_price(stepper.get("tracking", {}).get("mrp"))

                                if p1 and p2:
                                    fsp = min(p1, p2)
                                    mrp = max(p1, p2)
                                else:
                                    fsp = p1 or p2 or 0
                                    mrp = fsp

                                disc = 0
                                l2 = snb_text.get("label_2", {}).get("value", "")
                                l2_str = str(l2.get("params", {}).get("defaultValue") or l2.get("text", "") if isinstance(l2, dict) else l2)
                                m_disc = re.search(r"(\d+)%", l2_str)
                                if m_disc:
                                    disc = int(m_disc.group(1))
                                elif mrp > fsp:
                                    disc = round(((mrp - fsp) / mrp) * 100)

                                is_oos = (stepper.get("tracking", {}).get("isAvailable") == "false" or
                                          stepper.get("enabled") is False or
                                          cval.get("action", {}).get("params", {}).get("isAvailable") is False)

                                img = col0.get("params", {}).get("imageUrl") or stepper.get("params", {}).get("productImage") or ""
                                if not img:
                                    img_obj = cval.get("image_0", {}).get("value") or cval.get("snb_beauty_gmh_image_0", {}).get("value", {}).get("image_0", {}).get("value") or {}
                                    if isinstance(img_obj, dict):
                                        img = img_obj.get("params", {}).get("defaultValue") or img_obj.get("dynamicImageUrl") or img_obj.get("imageHack") or ""
                                img = img.replace("{@width}", "400").replace("{@height}", "400").replace("?q={@quality}", "?q=80")

                                prod = self._normalize_product(title, fsp, mrp, disc, img, lnk, is_oos)
                                if prod and prod["id"] not in seen_uids:
                                    seen_uids.add(prod["id"])
                                    products.append(prod)

                                # Parse embedded multi-variant swatches (scrollToListData_0)
                                swatch_list = (stepper.get("params", {}).get("widgetData", {}).get("data", {}).get("dlsData", {}).get("swatch_list_0_0", {}).get("value", {}).get("scrollToListData_0", {}).get("value")
                                               if isinstance(stepper, dict) else None)
                                if isinstance(swatch_list, list):
                                    for sw in swatch_list:
                                        try:
                                            sv = sw.get("value", {}) if isinstance(sw, dict) else {}
                                            sw_action = sv.get("stepperData_0", {}).get("action", {})
                                            sw_params = sw_action.get("params", {})
                                            sw_fsp = extract_price(sw_params.get("fspUnlocked") or sw_params.get("fspLocked") or sv.get("label_3") or sw_params.get("price"))
                                            sw_mrp = extract_price(sw_params.get("mrp") or sv.get("label_2")) or sw_fsp
                                            sw_disc_str = str(sw_params.get("discountPercentage") or "")
                                            sw_disc_m = re.search(r"(\d+)%", sw_disc_str)
                                            sw_disc = int(sw_disc_m.group(1)) if sw_disc_m else 0
                                            sw_attr = sw_params.get("attributeValue") or sv.get("label_0", {}).get("value", {}).get("text") or ""
                                            sw_pid = sw_params.get("productId") or ""
                                            sw_lid = sw_params.get("listingId") or ""
                                            sw_title = f"{title} ({sw_attr})" if sw_attr else title
                                            sw_img = (sw_params.get("imageUrl") or sw_params.get("productImage") or img or "")
                                            sw_img = sw_img.replace("{@width}", "400").replace("{@height}", "400").replace("?q={@quality}", "?q=80")
                                            sw_lnk = lnk
                                            if sw_lnk and sw_pid:
                                                sw_lnk = re.sub(r"([?&]pid=)[^&]+", r"\g<1>" + sw_pid, sw_lnk)
                                                if sw_lid:
                                                    sw_lnk = re.sub(r"([?&]lid=)[^&]+", r"\g<1>" + sw_lid, sw_lnk)
                                            sw_oos = (sw_action.get("enabled") is False or sw_action.get("tracking", {}).get("isAvailable") == "false")
                                            if sw_fsp:
                                                sw_prod = self._normalize_product(sw_title, sw_fsp, sw_mrp, sw_disc, sw_img, sw_lnk, sw_oos)
                                                if sw_prod and sw_prod["id"] not in seen_uids:
                                                    seen_uids.add(sw_prod["id"])
                                                    products.append(sw_prod)
                                        except Exception:
                                            continue
                                continue

                            # Case B: MRCSV / Product Cards (product-card / productCard / hp_reco_pmu_product-card)
                            pcard = None
                            for pk, pv in cval.items():
                                if "product-card" in pk or "productCard" in pk:
                                    pcard = pv.get("value", {}) if isinstance(pv, dict) else {}
                                    break

                            if pcard:
                                stepper_action = pcard.get("stepperData_0", {}).get("action", {})
                                stepper_tracking = stepper_action.get("tracking", {})

                                stepper_fsp = extract_price(stepper_action.get("params", {}).get("price") or stepper_tracking.get("fsp"))
                                stepper_mrp = extract_price(stepper_tracking.get("mrp"))
                                l5_val = extract_price(pcard.get("label_5"))
                                l4_val = extract_price(pcard.get("label_4"))

                                p_sell = stepper_fsp or l5_val or 0
                                p_mrp = stepper_mrp or l4_val or 0

                                if p_sell and p_mrp:
                                    fsp = min(p_sell, p_mrp)
                                    mrp = max(p_sell, p_mrp)
                                else:
                                    fsp = p_sell or p_mrp or 0
                                    mrp = fsp

                                disc = 0
                                if pcard.get("label_15", {}).get("value"):
                                    l15 = pcard["label_15"]["value"]
                                    l15_str = str(l15.get("UNLOCKED", {}).get("value", {}).get("text") or l15.get("LOCKED", {}).get("value", {}).get("text") or l15.get("text", "") if isinstance(l15, dict) else l15)
                                    m_disc = re.search(r"(\d+)%", l15_str)
                                    if m_disc:
                                        disc = int(m_disc.group(1))
                                elif mrp > fsp:
                                    disc = round(((mrp - fsp) / mrp) * 100)

                                raw_lnk = (pcard.get("box_5", {}).get("action", {}).get("url") or
                                           pcard.get("col_0", {}).get("action", {}).get("url") or
                                           pcard.get("box_0", {}).get("action", {}).get("url") or "")
                                lnk = build_product_link(raw_lnk, cval=pcard, stepper_action=stepper_action)

                                title = (pcard.get("label_2", {}).get("value", {}).get("text") or
                                         pcard.get("label_1", {}).get("value", {}).get("text") or
                                         pcard.get("label_0", {}).get("value", {}).get("text") or
                                         pcard.get("trackerData_0", {}).get("tracking", {}).get("contentTitle") or
                                         extract_title_from_url(lnk) or "Product")

                                img = stepper_action.get("params", {}).get("productImage") or ""
                                if not img:
                                    img_obj = pcard.get("hp_reco_pmu_product-card_image_0", {}).get("value", {})
                                    img = (img_obj.get("image_0", {}).get("value", {}).get("dynamicImageUrl") or
                                           img_obj.get("video_0", {}).get("value", {}).get("dynamicImageUrl") or "")
                                img = img.replace("{@width}", "400").replace("{@height}", "400").replace("?q={@quality}", "?q=80")

                                btn_text = pcard.get("button_0", {}).get("value", {}).get("text", "")
                                is_oos = (stepper_action.get("enabled") is False or
                                          pcard.get("button_0", {}).get("value", {}).get("actionType") == "NOTIFY_ME" or
                                          (isinstance(btn_text, str) and "notify" in btn_text.lower()))

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

        # If discount is present but MRP was not found (or mrp == fsp), derive MRP from selling price!
        # NEVER discount fsp a second time! fsp is what the customer actually pays!
        if 0 < disc < 100 and mrp == fsp:
            mrp = round(fsp / (1 - disc / 100))

        # Re-verify disc
        if not disc or disc <= 0 or disc >= 100:
            disc = round(((mrp - fsp) / mrp) * 100) if mrp > fsp else 0

        # Fix concatenated discount bug (only if current MRP does not match discount, and clean_mrp does match discount)
        if mrp > fsp and disc > 0 and str(mrp).endswith(str(disc)):
            current_math_disc = round(((mrp - fsp) / mrp) * 100)
            if abs(current_math_disc - disc) > 2:
                clean_mrp = int(str(mrp)[:-len(str(disc))])
                if clean_mrp > fsp:
                    clean_math_disc = round(((clean_mrp - fsp) / clean_mrp) * 100)
                    if abs(clean_math_disc - disc) <= 2:
                        mrp = clean_mrp
                        disc = clean_math_disc

        uid = extract_product_uid(lnk, title, fsp)
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
            "speaker", "gadget", "toy", "stationery",
            "electrical", "tool", "bedding", "furnishing", "fashion"
        ]

        def is_clutter(name, url):
            text = (name + " " + url).lower()
            return any(t in text for t in clutter_terms)

        for raw_s in slots:
            s = raw_s.get("slotData", raw_s) if isinstance(raw_s, dict) else {}
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

    def fetch_category_deals(self, category_info, min_discount=None, max_pages=None):
        """
        Fetches and parses deals for a category across pages.
        Uses smart discount-aware pagination:
        If Page 1 contains qualifying deals (min discount on page 1 is >= min_discount,
        or >= 12 items on page with >= min_discount), it automatically fetches Page 2 (and Page 3
        if still qualifying), guaranteeing that items at 70%-74% discount pushed past Page 1
        are never missed.
        """
        min_disc = int(min_discount if min_discount is not None else config.MIN_DISCOUNT)
        uri = category_info.get("uri", "")
        cat_name = category_info.get("name", "Category")

        # Fetch Page 1
        json_data = self.fetch_rome_page(uri)
        products = self.parse_products_from_json(json_data)
        discovered_subcats = self.extract_subcategories(json_data)

        seen_uids = {p["id"] for p in products}

        # Smart multi-page pagination (max_pages defaults to config.DEFAULT_MAX_PAGES)
        limit_pages = max_pages if max_pages is not None else getattr(config, "DEFAULT_MAX_PAGES", 2)
        is_phone_case_cat = any(x in cat_name.lower() for x in ("case", "cover", "pouch"))
        effective_max_pages = min(2, limit_pages) if is_phone_case_cat else limit_pages
        curr_page = 1
        page_prods = products
        is_glitch_scan = bool(category_info.get("is_price_error_scan") or "price_asc" in uri)
        while curr_page < effective_max_pages and page_prods:
            if len(page_prods) < 6:
                break

            if is_glitch_scan:
                max_fsp_found = max(p.get("fsp", 999) for p in page_prods)
                glitch_thresh = getattr(config, "PRICE_ERROR_MAX_FSP", 4)
                if max_fsp_found > glitch_thresh:
                    break
            else:
                min_disc_found = min(p.get("discount", 0) for p in page_prods)
                qualifying = [p for p in page_prods if p.get("discount", 0) >= min_disc]
                if min_disc_found < min_disc and len(qualifying) < 12:
                    break

            next_page = curr_page + 1
            next_uri = build_page_uri(uri, next_page)
            next_json = self.fetch_rome_page(next_uri)
            if not next_json:
                break

            next_prods = self.parse_products_from_json(next_json)
            if not next_prods:
                break

            new_count = 0
            for p in next_prods:
                if p["id"] not in seen_uids:
                    seen_uids.add(p["id"])
                    products.append(p)
                    new_count += 1

            if new_count == 0:
                break

            page_prods = next_prods
            curr_page = next_page

        for p in products:
            p["category"] = cat_name
        return products, discovered_subcats
