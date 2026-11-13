import json
import math
import urllib.request
from pathlib import Path

HEADERS = {
    "User-Agent": "BTC-Price-Panel/1.0",
    "Accept": "application/json",
}

KAYNAKLAR = [
    {
        "ad": "Coinbase",
        "url": "https://api.coinbase.com/v2/prices/BTC-USD/spot",
        "yol": ["data", "amount"],
    },
    {
        "ad": "Kraken",
        "url": "https://api.kraken.com/0/public/Ticker?pair=XBTUSD",
        "yol": ["result", "XXBTZUSD", "c", 0],
    },
    {
        "ad": "Blockchain.com",
        "url": "https://blockchain.info/ticker",
        "yol": ["USD", "last"],
    },
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


def main():
    fiyatlar = []

    for kaynak in KAYNAKLAR:
        try:
            fiyat = fiyat_cek(kaynak["url"], kaynak["yol"])
            fiyatlar.append(fiyat)

            print(
                f'{kaynak["ad"]}: ${fiyat:,.2f}',
                flush=True,
            )

        except Exception as hata:
            print(
                f'{kaynak["ad"]} verisi alınamadı: '
                f"{type(hata).__name__}: {hata}",
                flush=True,
            )

    if len(fiyatlar) != len(KAYNAKLAR):
        raise SystemExit(
            f"Üç kaynağın tamamından veri alınamadı "
            f"({len(fiyatlar)}/{len(KAYNAKLAR)}). "
            "Mevcut index.html değiştirilmedi."
        )

    ortalama = sum(fiyatlar) / len(fiyatlar)

    html_icerik = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>BTC/USD Ortalama</title>
    <style>
        body {{
            margin: 0;
            padding: 12px;
            background: #ffffff;
            color: #000000;
            font-family: Arial, sans-serif;
            font-size: 20px;
        }}

        .fiyat {{
            white-space: nowrap;
        }}
    </style>
</head>
<body>
    <div class="fiyat">BTC/USD: ${ortalama:,.2f}</div>
</body>
</html>
"""

    Path("index.html").write_text(
        html_icerik,
        encoding="utf-8",
    )

    print(
        f"index.html oluşturuldu. Ortalama: ${ortalama:,.2f}",
        flush=True,
    )


if __name__ == "__main__":
    main()
