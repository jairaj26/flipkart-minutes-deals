import html
import json
import time
import urllib.parse
import urllib.request
import ssl
from . import config

ctx = ssl.create_default_context()

class TelegramNotifier:
    def __init__(self, bot_token=None, chat_id=None):
        self.bot_token = (bot_token or config.TELEGRAM_BOT_TOKEN).strip()
        self.chat_id = (chat_id or config.TELEGRAM_CHAT_ID).strip()
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

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
        mrp_str = f" (MRP: ₹{mrp})" if mrp > fsp else ""

        return f"<b>{title}</b>\n🔥 <b>{disc}% OFF</b> | 💰 <b>₹{fsp}</b>{mrp_str}\n<a href=\"{link}\">Click here</a>"

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
        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, context=ctx, timeout=10) as res:
                res_data = json.loads(res.read().decode("utf-8"))
                return res_data.get("ok", False)
        except Exception as e:
            print(f"[Telegram Error] {e}")
            return False
