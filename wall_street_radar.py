```python
import os
import requests

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

message = """
🚀 Wall Street Radar

Bot iniciado correctamente.

Si recibís este mensaje significa que:
✅ GitHub Actions funciona
✅ Telegram funciona
✅ Los Secrets están configurados
"""

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

requests.post(
    url,
    data={
        "chat_id": CHAT_ID,
        "text": message
    }
)
```

