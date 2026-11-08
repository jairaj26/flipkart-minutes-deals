import html
import json
import time
import urllib.parse
import urllib.request
import ssl
import requests
from . import config

ctx = ssl.create_default_context()

class TelegramNotifier:
    def __init__(self, bot_token=None, chat_id=None):
        self.bot_token = (bot_token or config.TELEGRAM_BOT_TOKEN).strip()
        self.chat_id = (chat_id or config.TELEGRAM_CHAT_ID).strip()
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.session = requests.Session()

    @property
    def is_configured(self):
        return bool(self.bot_token and self.chat_id)

    def format_deal_entry(self, deal):
        """
        Formats an individual deal entry according to:
        Title
        🔥 {disc}% OFF | 💰 ₹{fsp} (MRP: ₹{mrp})
        Click here
        """
        title = html.escape(deal.get("title", "Product").strip())
        fsp = deal.get("fsp", 0)
        mrp = deal.get("mrp", fsp)
        disc = deal.get("discount", 0)
        link = deal.get("link", "https://www.flipkart.com")
        safe_link = html.escape(link, quote=True)
        mrp_str = f" (MRP: ₹{mrp})" if mrp > fsp else ""

        if deal.get("is_price_error") or (0 < fsp < 5) or (fsp == 5 and disc >= 80):
            disc_label = f"⚡ <b>PRICE ERROR / ₹{fsp} LOOT</b>"
            if disc > 0:
                disc_label += f" ({disc}% OFF)"
            return f"🚨 {disc_label}\n<b>{title}</b>\n💰 <b>Price: ₹{fsp}</b>{mrp_str}\n<a href=\"{safe_link}\">Click here</a>"

        return f"<b>{title}</b>\n🔥 <b>{disc}% OFF</b> | 💰 <b>₹{fsp}</b>{mrp_str}\n<a href=\"{safe_link}\">Click here</a>"

    def format_deal_message(self, deal):
        """Single deal format for backward compatibility."""
        return self.format_deal_entry(deal)

    def send_combined_deals(self, deals, max_chars_per_message=3800):
        """
        Combines multiple deals into a single message (or chunked messages if > 3800 chars).
        Returns the list of successfully sent deals.
        """
        if not self.is_configured:
            print("[Telegram] Not configured (missing bot token or chat ID). Skipping alert.")
            return []

        if not deals:
            return []

        successfully_sent = []
        chunks = []
        current_chunk_deals = []
        current_chunk_text = ""

        for deal in deals:
            entry_text = self.format_deal_entry(deal)
            tentative_len = len(current_chunk_text) + (2 if current_chunk_text else 0) + len(entry_text)
            if tentative_len > max_chars_per_message and current_chunk_deals:
                chunks.append((current_chunk_text, current_chunk_deals))
                current_chunk_text = entry_text
                current_chunk_deals = [deal]
            else:
                if current_chunk_text:
                    current_chunk_text += "\n\n" + entry_text
                else:
                    current_chunk_text = entry_text
                current_chunk_deals.append(deal)

        if current_chunk_deals:
            chunks.append((current_chunk_text, current_chunk_deals))

        for text, chunk_deals in chunks:
            success = self._send_text(text)
            if success:
                successfully_sent.extend(chunk_deals)
            time.sleep(1.0)

        return successfully_sent

    def send_deal(self, deal):
        """Sends a single deal alert (backward compatibility)."""
        res = self.send_combined_deals([deal])
        return len(res) > 0

    def _send_text(self, text):
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                res = self.session.post(url, json=payload, timeout=10)
                res_data = {}
                try:
                    res_data = res.json()
                except Exception:
                    pass

                if res.status_code == 200 and res_data.get("ok"):
                    return True

                if res.status_code == 429:
                    retry_after = res_data.get("parameters", {}).get("retry_after", 5)
                    print(f"[Telegram 429] Rate limited. Retrying after {retry_after}s (attempt {attempt + 1}/{max_retries + 1})...")
                    if attempt < max_retries:
                        time.sleep(retry_after)
                        continue

                error_desc = res_data.get("description") or res.text
                print(f"[Telegram Error HTTP {res.status_code}] {error_desc}")
                return False
            except Exception as e:
                print(f"[Telegram Error] {e}")
                if attempt < max_retries:
                    time.sleep(2)
                    continue
                return False
        return False
