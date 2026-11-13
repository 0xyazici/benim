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

    veri_zamani = datetime.now(timezone(timedelta(hours=3)))
    tarih_yazisi = veri_zamani.strftime("%d.%m.%Y")
    saat_yazisi = veri_zamani.strftime("%H:%M")
    tarih_iso = veri_zamani.isoformat(timespec="seconds")

    html_icerik = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="theme-color" content="#f5f3ee">
    <meta
        name="description"
        content="Üç veri kaynağından hesaplanan BTC/USD fiyat ortalaması."
    >

    <title>BTC/USD Ortalama</title>

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link
        rel="preconnect"
        href="https://fonts.gstatic.com"
        crossorigin
    >
    <link
        href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;600;700&display=swap"
        rel="stylesheet"
    >

    <style>
        :root {{
            color-scheme: light;
            --inci: #f5f3ee;
            --fiyat: #faf9f6;
            --parite: #c9cdd3;
            --tarih: rgba(54, 57, 63, 0.56);
        }}

        * {{
            box-sizing: border-box;
        }}

        html {{
            min-height: 100%;
            background: var(--inci);
        }}

        body {{
            margin: 0;
            min-height: 100vh;
            min-height: 100svh;
            display: grid;
            place-items: center;
            padding: 24px 16px;
            overflow-x: hidden;
            font-family: Arial, Helvetica, sans-serif;
            background:
                radial-gradient(
                    ellipse at 25% 25%,
                    rgba(255, 255, 255, 0.95),
                    transparent 55%
                ),
                radial-gradient(
                    ellipse at 75% 75%,
                    rgba(196, 201, 207, 0.27),
                    transparent 55%
                ),
                var(--inci);
        }}

        .gosterge {{
            position: relative;
            width: min(820px, 100%);
        }}

        .cam-serit {{
            position: relative;
            isolation: isolate;
            overflow: hidden;
            display: flex;
            align-items: baseline;
            justify-content: center;
            gap: clamp(12px, 3vw, 32px);
            width: 100%;
            padding: clamp(28px, 5vw, 48px)
                     clamp(14px, 4vw, 42px);
            border: 1px solid rgba(255, 255, 255, 0.60);
            border-radius: 24px;
            background:
                linear-gradient(
                    135deg,
                    rgba(83, 89, 98, 0.87),
                    rgba(40, 45, 53, 0.95)
                );
            -webkit-backdrop-filter: blur(20px);
            backdrop-filter: blur(20px);
            box-shadow:
                0 22px 55px rgba(35, 40, 48, 0.16),
                0 5px 14px rgba(35, 40, 48, 0.08),
                inset 0 1px 0 rgba(255, 255, 255, 0.25);
            white-space: nowrap;
        }}

        .cam-serit::before {{
            content: "";
            position: absolute;
            z-index: -1;
            inset: 0;
            pointer-events: none;
            background:
                linear-gradient(
                    115deg,
                    rgba(255, 255, 255, 0.14),
                    transparent 42%,
                    rgba(255, 255, 255, 0.025) 70%,
                    transparent
                );
        }}

        .parite {{
            flex-shrink: 0;
            font-family: "Orbitron", "Courier New", monospace;
            font-size: clamp(13px, 2.8vw, 27px);
            font-weight: 500;
            letter-spacing: 0.04em;
            color: var(--parite);
        }}

        .fiyat {{
            font-family: "Orbitron", "Courier New", monospace;
            font-size: clamp(23px, 5.4vw, 56px);
            font-weight: 600;
            font-variant-numeric: tabular-nums;
            letter-spacing: -0.025em;
            line-height: 1.2;
            color: var(--fiyat);
            text-shadow: 0 1px 8px rgba(255, 255, 255, 0.08);
        }}

        .tarih {{
            position: absolute;
            top: calc(100% + 22px);
            left: 0;
            width: 100%;
            margin: 0;
            text-align: center;
            font-family: "Orbitron", "Courier New", monospace;
            font-size: clamp(10px, 1.7vw, 12px);
            font-weight: 500;
            letter-spacing: 0.10em;
            color: var(--tarih);
        }}

        .ayirici {{
            display: inline-block;
            margin: 0 9px;
            opacity: 0.65;
        }}

        ::selection {{
            background: #d5d9df;
            color: #252a32;
        }}

        @media (max-width: 380px) {{
            .cam-serit {{
                gap: 10px;
                padding: 28px 10px;
                border-radius: 18px;
            }}

            .parite {{
                font-size: 11px;
            }}

            .fiyat {{
                font-size: 21px;
            }}
        }}
    </style>
</head>

<body>
    <main class="gosterge" aria-label="Bitcoin dolar fiyat ortalaması">
        <div
            class="cam-serit"
            aria-label="Üç veri kaynağından hesaplanan BTC/USD ortalaması"
        >
            <span class="parite">BTC/USD</span>
            <span class="fiyat">${ortalama:,.2f}</span>
        </div>

        <p class="tarih">
            <time
                datetime="{tarih_iso}"
                title="Veri alınma zamanı — Türkiye saati (UTC+3)"
            >{tarih_yazisi}<span class="ayirici">·</span>{saat_yazisi}</time>
        </p>
    </main>
</body>
</html>
"""

    Path("index.html").write_text(
        html_icerik,
        encoding="utf-8",
    )

    print(
        f"index.html oluşturuldu. "
        f"Ortalama: ${ortalama:,.2f} | "
        f"Türkiye saati: {tarih_yazisi} {saat_yazisi}",
        flush=True,
    )


if __name__ == "__main__":
    main()
