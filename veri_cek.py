import socket
import urllib.request
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta

# GitHub sunucularındaki IPv6 zaman aşımı sorununu çözen ayar
old_getaddrinfo = socket.getaddrinfo
def new_getaddrinfo(*args, **kwargs):
    responses = old_getaddrinfo(*args, **kwargs)
    return [response for response in responses if response[0] == socket.AF_INET]
socket.getaddrinfo = new_getaddrinfo

headers = {'User-Agent': 'Mozilla/5.0'}
usd_try, eur_try = 0.0, 0.0

# 1. Kaynak: TCMB (Türkiye Cumhuriyet Merkez Bankası) Resmi XML
try:
    req = urllib.request.Request("https://tcmb.gov.tr", headers=headers)
    with urllib.request.urlopen(req, timeout=10) as res:
        tree = ET.fromstring(res.read())
        for currency in tree.findall('Currency'):
            kod = currency.get('CurrencyCode')
            if kod == 'USD':
                usd_try = float(currency.find('ForexSelling').text)
            elif kod == 'EUR':
                eur_try = float(currency.find('ForexSelling').text)
except Exception:
    # 2. Yedek Kaynak: Avrupa Merkez Bankası (Frankfurter)
    req = urllib.request.Request("https://frankfurter.app", headers=headers)
    with urllib.request.urlopen(req, timeout=10) as res:
        data = json.loads(res.read().decode('utf-8'))
        usd_try = data['rates']['TRY']
        eur_try = usd_try / data['rates']['EUR']

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
        <h2>Canlı Döviz Kurları (TCMB)</h2>
        <div class="kur">1 Dolar: {usd_try:.2f} TL</div>
        <div class="kur">1 Euro: {eur_try:.2f} TL</div>
        <div class="tarih">Son Güncelleme: {tr_saat}</div>
    </div>
</body>
</html>"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_icerik)
