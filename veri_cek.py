import json
import math
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

HEADERS = {
    "User-Agent": "BTC-Price-Panel/1.0",
    "Accept": "application/json",
}

KAYNAKLAR = [
    (
        "Coinbase",
        "https://api.coinbase.com/v2/prices/BTC-USD/spot",
        ["data", "amount"],
    ),
    (
        "Kraken",
        "https://api.kraken.com/0/public/Ticker?pair=XBTUSD",
        ["result", "XXBTZUSD", "c", 0],
    ),
    (
        "Blockchain.com",
        "https://blockchain.info/ticker",
        ["USD", "last"],
    ),
]


def fiyat_cek(url, yol):
    istek = urllib.request.Request(url, headers=HEADERS)

    with urllib.request.urlopen(istek, timeout=20) as yanit:
        veri = json.loads(yanit.read().decode("utf-8"))

    for anahtar in yol:
        veri = veri[anahtar]

    fiyat = float(veri)

    if not math.isfinite(fiyat) or fiyat <= 0:
        raise ValueError("Geçersiz fiyat değeri")

    return fiyat


fiyatlar = []
satirlar = []

for ad, url, yol in KAYNAKLAR:
    try:
        fiyat = fiyat_cek(url, yol)
        fiyatlar.append(fiyat)
        sonuc = f"${fiyat:,.2f}"
        print(f"{ad}: {sonuc}", flush=True)
    except Exception as hata:
        sonuc = "Erişilemedi"
        print(
            f"{ad}: {type(hata).__name__}: {hata}",
            flush=True,
        )

    satirlar.append(
        f'<div class="satir"><span>{ad}</span>'
        f"<strong>{sonuc}</strong></div>"
    )

# Hiç veri alınamadığında mevcut index.html dosyasını bozma.
if not fiyatlar:
    raise SystemExit(
        "Hiçbir kaynaktan fiyat alınamadı. "
        "Mevcut index.html değiştirilmedi."
    )

ortalama = sum(fiyatlar) / len(fiyatlar)

tr_saat = datetime.now(
    timezone(timedelta(hours=3))
).strftime("%d.%m.%Y %H:%M:%S")

kaynak_html = "\n".join(satirlar)

html_icerik = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>BTC/USD Fiyat Paneli</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background: #0f172a;
            color: #f8fafc;
            text-align: center;
            padding: 40px 20px;
        }}
        .kutu {{
            background: #1e293b;
            padding: 30px;
            border-radius: 16px;
            max-width: 440px;
            margin: auto;
            border: 1px solid #334155;
        }}
        .baslik {{
            color: #94a3b8;
            font-size: 18px;
        }}
        .ortalama {{
            font-size: 36px;
            font-weight: bold;
            color: #f59e0b;
            margin: 20px 0;
        }}
        .kaynaklar {{
            background: #0f172a;
            padding: 15px;
            border-radius: 10px;
        }}
        .satir {{
            display: flex;
            justify-content: space-between;
            gap: 12px;
            padding: 8px 0;
            border-bottom: 1px solid #1e293b;
        }}
        .tarih {{
            font-size: 12px;
            color: #94a3b8;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="kutu">
        <div class="baslik">BTC / USD Kaynak Ortalaması</div>
        <div class="ortalama">${ortalama:,.2f}</div>

        <div class="kaynaklar">
            {kaynak_html}
        </div>

        <div class="tarih">
            Başarılı kaynak: {len(fiyatlar)} / {len(KAYNAKLAR)}<br>
            Veri alınma zamanı: {tr_saat} (Türkiye)
        </div>
    </div>
</body>
</html>
"""

Path("index.html").write_text(html_icerik, encoding="utf-8")
print("index.html başarıyla oluşturuldu.", flush=True)
