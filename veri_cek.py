import urllib.request
import json
from datetime import datetime, timezone, timedelta

url = "https://jsdelivr.net"
req = urllib.request.urlopen(url, timeout=15)
data = json.loads(req.read().decode('utf-8'))

usd_try = data['usd']['try']
eur_usd = data['usd']['eur']
eur_try = usd_try / eur_usd

tr_saat = (datetime.now(timezone.utc) + timedelta(hours=3)).strftime('%d.%m.%Y %H:%M')

html_icerik = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Canlı Döviz Paneli</title>
    <style>
        body {{ font-family: Arial, sans-serif; background-color: #f4f7f6; text-align: center; padding: 50px; }}
        .kutu {{ background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); max-width: 400px; margin: auto; }}
        .kur {{ font-size: 24px; font-weight: bold; color: #2c3e50; margin: 15px 0; }}
        .tarih {{ font-size: 12px; color: #7f8c8d; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="kutu">
        <h2>Canlı Döviz Kurları</h2>
        <div class="kur">1 Dolar: {usd_try:.2f} TL</div>
        <div class="kur">1 Euro: {eur_try:.2f} TL</div>
        <div class="tarih">Son Güncelleme: {tr_saat}</div>
    </div>
</body>
</html>"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_icerik)
