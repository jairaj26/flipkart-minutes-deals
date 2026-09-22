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

class FlipkartScraper:
    def __init__(self, pincode=None):
        self.pincode = int(pincode or config.DEFAULT_PINCODE)
        self.session_cookies = {
            "snPincode": str(self.pincode),
            "deliveryPincode": str(self.pincode),
            "pincode": str(self.pincode)
        }
        if config.FLIPKART_COOKIE:
            for item in config.FLIPKART_COOKIE.split(";"):
                item = item.strip()
                if "=" in item:
                    k, v = item.split("=", 1)
                    self.session_cookies[k.strip()] = v.strip()

    def fetch_rome_page(self, page_uri, redirect_count=0):
        """Fetches a page from Rome API, automatically following 302 redirects."""
        if redirect_count > 3:
            return None

        # Clean uri
        clean_uri = page_uri
        if clean_uri.startswith("http"):
            parsed = urllib.parse.urlparse(clean_uri)
            clean_uri = parsed.path + ("?" + parsed.query if parsed.query else "")

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
                        lnk = ("https://www.flipkart.com" + base_url) if base_url else ""

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

            # Check dlsData (MRCSV / carousels / grids)
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
                                lnk = col0.get("url") or col0.get("originalUrl") or ""
                                if lnk and not lnk.startswith("http"):
                                    lnk = "https://www.flipkart.com" + lnk

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

                                stepper = cval.get("stepperData_0", {}).get("action", {})
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

    def fetch_category_deals(self, category_info):
        """Fetches and parses all deals for a single category."""
        uri = category_info.get("uri", "")
        cat_name = category_info.get("name", "Category")
        json_data = self.fetch_rome_page(uri)
        products = self.parse_products_from_json(json_data)
        for p in products:
            p["category"] = cat_name
        return products
