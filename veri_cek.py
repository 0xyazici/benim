import urllib.request
import json
from datetime import datetime, timezone, timedelta

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
fiyatlar = []

def cek(url, yol):
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as res:
            data = json.loads(res.read().decode('utf-8'))
            for k in yol:
                data = data[k]
            fiyat = float(data)
            fiyatlar.append(fiyat)
            return f"${fiyat:,.2f}"
    except Exception:
        return "Erişilemedi"

# ABD ve Avrupa sunucularından %100 erişilebilen 3 Büyük Kaynak
coinbase = cek("https://coinbase.com", ["data", "amount"])
kraken = cek("https://kraken.com", ["result", "XXBTZUSD", "c", 0])
blockchain = cek("https://blockchain.info", ["USD", "last"])

ortalama = f"${sum(fiyatlar)/len(fiyatlar):,.2f}" if fiyatlar else "Veri Bekleniyor"
tr_saat = (datetime.now(timezone.utc) + timedelta(hours=3)).strftime('%d.%m.%Y %H:%M')

html_icerik = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Canlı BTC/USD Ortalama Paneli</title>
    <style>
        body {{ font-family: Arial, sans-serif; background-color: #0f172a; color: #f8fafc; text-align: center; padding: 40px 20px; }}
        .kutu {{ background: #1e293b; padding: 30px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.4); max-width: 440px; margin: auto; border: 1px solid #334155; }}
        .baslik {{ font-size: 18px; color: #94a3b8; margin-bottom: 10px; }}
        .ortalama {{ font-size: 36px; font-weight: bold; color: #f59e0b; margin: 20px 0; }}
        .kaynaklar {{ background: #0f172a; padding: 15px; border-radius: 10px; text-align: left; font-size: 15px; line-height: 1.8; }}
        .satir {{ display: flex; justify-content: space-between; border-bottom: 1px solid #1e293b; padding: 4px 0; }}
        .satir:last-child {{ border-bottom: none; }}
        .tarih {{ font-size: 12px; color: #64748b; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="kutu">
        <div class="baslik">BTC / USD Piyasa Ortalaması</div>
        <div class="ortalama">{ortalama}</div>
        
        <div class="kaynaklar">
            <div class="satir"><span>1. Coinbase:</span> <strong>{coinbase}</strong></div>
            <div class="satir"><span>2. Kraken:</span> <strong>{kraken}</strong></div>
            <div class="satir"><span>3. Blockchain.com:</span> <strong>{blockchain}</strong></div>
        </div>

        <div class="tarih">Son Güncelleme: {tr_saat}</div>
    </div>
</body>
</html>"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_icerik)
