from datetime import datetime, timezone, timedelta

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
        <div class="kur" id="dolar">1 Dolar: Yükleniyor...</div>
        <div class="kur" id="euro">1 Euro: Yükleniyor...</div>
        <div class="tarih">Sistem Güncellemesi: {tr_saat}</div>
    </div>

    <script>
        fetch('https://er-api.com')
            .then(res => res.json())
            .then(data => {{
                const usd = data.rates.TRY;
                const eur = usd / data.rates.EUR;
                document.getElementById('dolar').innerText = '1 Dolar: ' + usd.toFixed(2) + ' TL';
                document.getElementById('euro').innerText = '1 Euro: ' + eur.toFixed(2) + ' TL';
            }})
            .catch(() => {{
                document.getElementById('dolar').innerText = 'Veri alınamadı';
            }});
    </script>
</body>
</html>"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_icerik)
