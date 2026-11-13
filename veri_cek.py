import json
import math
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path


HEADERS = {
    "User-Agent": "Price-Panel/1.0",
    "Accept": "application/json",
}

BTC_KAYNAKLARI = [
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

ALTIN_URL = "https://api.gold-api.com/price/XAU"


def json_cek(url):
    istek = urllib.request.Request(url, headers=HEADERS)

    with urllib.request.urlopen(istek, timeout=20) as yanit:
        return json.loads(yanit.read().decode("utf-8"))


def fiyat_dogrula(deger):
    fiyat = float(deger)

    if not math.isfinite(fiyat) or fiyat <= 0:
        raise ValueError("Geçersiz fiyat değeri")

    return fiyat


def btc_ortalama_cek():
    fiyatlar = []

    for kaynak in BTC_KAYNAKLARI:
        try:
            veri = json_cek(kaynak["url"])

            for anahtar in kaynak["yol"]:
                veri = veri[anahtar]

            fiyat = fiyat_dogrula(veri)
            fiyatlar.append(fiyat)

            print(
                f'BTC — {kaynak["ad"]}: ${fiyat:,.2f}',
                flush=True,
            )

        except Exception as hata:
            print(
                f'BTC — {kaynak["ad"]} verisi alınamadı: '
                f"{type(hata).__name__}: {hata}",
                flush=True,
            )

    if len(fiyatlar) != len(BTC_KAYNAKLARI):
        raise RuntimeError(
            "BTC için üç kaynağın tamamından veri alınamadı "
            f"({len(fiyatlar)}/{len(BTC_KAYNAKLARI)})."
        )

    return sum(fiyatlar) / len(fiyatlar)


def altin_fiyati_cek():
    veri = json_cek(ALTIN_URL)

    if veri.get("symbol") != "XAU":
        raise ValueError("Beklenmeyen altın sembolü")

    if veri.get("currency", "USD") != "USD":
        raise ValueError("Altın fiyatının para birimi USD değil")

    fiyat = fiyat_dogrula(veri["price"])

    print(
        f"ONS — Gold API: ${fiyat:,.2f}",
        flush=True,
    )

    print(
        "Altın kaynağı güncelleme zamanı: "
        f'{veri.get("updatedAt", "Belirtilmemiş")}',
        flush=True,
    )

    return fiyat


def main():
    try:
        btc_ortalama = btc_ortalama_cek()
        altin_fiyati = altin_fiyati_cek()

    except Exception as hata:
        raise SystemExit(
            f"Veriler tamamlanamadı: {hata}\n"
            "Mevcut index.html değiştirilmedi."
        )

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
        content="BTC/USD kaynak ortalaması ve ons altın/USD fiyatı."
    >

    <title>BTC ve Ons Altın / USD</title>

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
            --parite: #bdc3cc;
            --tarih: rgba(54, 57, 63, 0.54);
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
            padding: 40px 16px;
            overflow-x: hidden;
            font-family: Arial, Helvetica, sans-serif;
            background:
                radial-gradient(
                    ellipse at 24% 24%,
                    rgba(255, 255, 255, 0.98),
                    transparent 55%
                ),
                radial-gradient(
                    ellipse at 78% 76%,
                    rgba(190, 198, 209, 0.27),
                    transparent 56%
                ),
                var(--inci);
        }}

        .panel {{
            width: min(820px, 100%);
            display: flex;
            flex-direction: column;
            align-items: center;
        }}

        .cam-serit {{
            position: relative;
            isolation: isolate;
            overflow: hidden;
            display: flex;
            align-items: baseline;
            justify-content: space-between;
            gap: clamp(12px, 3vw, 32px);
            min-width: 0;
            white-space: nowrap;
            border: 1px solid rgba(255, 255, 255, 0.62);
            background:
                linear-gradient(
                    135deg,
                    rgba(83, 89, 98, 0.87),
                    rgba(40, 45, 53, 0.95)
                );
            -webkit-backdrop-filter: blur(20px);
            backdrop-filter: blur(20px);
            box-shadow:
                0 20px 48px rgba(35, 40, 48, 0.13),
                0 5px 14px rgba(35, 40, 48, 0.06),
                inset 0 1px 0 rgba(255, 255, 255, 0.25);
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
                    rgba(255, 255, 255, 0.15),
                    transparent 42%,
                    rgba(255, 255, 255, 0.025) 70%,
                    transparent
                );
        }}

        .btc {{
            width: 100%;
            padding:
                clamp(30px, 5vw, 48px)
                clamp(18px, 4vw, 44px);
            border-radius: 25px;
        }}

        .ons {{
            width: 88%;
            margin-top: 19px;
            padding:
                clamp(24px, 4vw, 35px)
                clamp(16px, 3.5vw, 35px);
            border-radius: 21px;
            background:
                linear-gradient(
                    135deg,
                    rgba(91, 97, 106, 0.84),
                    rgba(48, 53, 61, 0.93)
                );
            box-shadow:
                0 14px 35px rgba(35, 40, 48, 0.10),
                inset 0 1px 0 rgba(255, 255, 255, 0.22);
        }}

        .parite {{
            flex-shrink: 0;
            font-family: "Orbitron", "Courier New", monospace;
            font-weight: 500;
            letter-spacing: 0.035em;
            color: var(--parite);
        }}

        .btc .parite {{
            font-size: clamp(11px, 2.1vw, 20px);
        }}

        .ons .parite {{
            font-size: clamp(10px, 1.8vw, 17px);
        }}

        .fiyat {{
            min-width: 0;
            text-align: right;
            font-family: "Orbitron", "Courier New", monospace;
            font-weight: 600;
            font-variant-numeric: tabular-nums;
            letter-spacing: -0.025em;
            line-height: 1.2;
            color: var(--fiyat);
            text-shadow: 0 1px 8px rgba(255, 255, 255, 0.08);
        }}

        .btc .fiyat {{
            font-size: clamp(25px, 6vw, 60px);
        }}

        .ons .fiyat {{
            font-size: clamp(21px, 4.8vw, 46px);
        }}

        .tarih {{
            margin: 25px 0 0;
            text-align: center;
            font-family: "Orbitron", "Courier New", monospace;
            font-size: clamp(10px, 1.6vw, 12px);
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
            body {{
                padding-right: 12px;
                padding-left: 12px;
            }}

            .btc {{
                gap: 10px;
                padding: 28px 14px;
                border-radius: 20px;
            }}

            .ons {{
                width: 92%;
                gap: 10px;
                margin-top: 15px;
                padding: 23px 13px;
                border-radius: 18px;
            }}

            .btc .parite {{
                font-size: 10px;
            }}

            .ons .parite {{
                font-size: 9px;
            }}

            .btc .fiyat {{
                font-size: 23px;
            }}

            .ons .fiyat {{
                font-size: 20px;
            }}
        }}
    </style>
</head>

<body>
    <main class="panel" aria-label="Bitcoin ve ons altın dolar fiyatları">
        <section
            class="cam-serit btc"
            aria-label="Üç kaynaktan hesaplanan Bitcoin dolar ortalaması"
            title="Coinbase, Kraken ve Blockchain.com fiyatlarının ortalaması"
        >
            <span class="parite">BTC/USD</span>
            <span class="fiyat">${btc_ortalama:,.2f}</span>
        </section>

        <section
            class="cam-serit ons"
            aria-label="Bir troy ons altının ABD doları fiyatı"
            title="Kaynak: Gold API — USD / troy ons"
        >
            <span class="parite">ONS/USD</span>
            <span class="fiyat">${altin_fiyati:,.2f}</span>
        </section>

        <p class="tarih">
            <time
                datetime="{tarih_iso}"
                title="Verilerin alınma zamanı — Türkiye saati (UTC+3)"
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
        "index.html oluşturuldu.\n"
        f"BTC/USD ortalama: ${btc_ortalama:,.2f}\n"
        f"ONS/USD: ${altin_fiyati:,.2f}\n"
        f"Veri alınma zamanı: {tarih_yazisi} {saat_yazisi}",
        flush=True,
    )


if __name__ == "__main__":
    main()
