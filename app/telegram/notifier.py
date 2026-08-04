from __future__ import annotations
import requests
from app.core.config import settings


class TelegramNotifier:
    def __init__(self):
        self.token = settings.TELEGRAM_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID

    def send(self, text: str) -> None:
        if not self.token or not self.chat_id:
            # no-op if not configured
            return
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        try:
            requests.post(url, json={"chat_id": self.chat_id, "text": text}, timeout=5)
        except Exception:
            pass
