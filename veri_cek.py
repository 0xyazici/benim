<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Canlı BTC/USD Ortalama Paneli</title>
<style>
  body {
    font-family: Arial, sans-serif;
    background: #0f172a;
    color: #f8fafc;
    text-align: center;
    padding: 40px 20px;
  }
  .kutu {
    background: #1e293b;
    padding: 30px;
    border-radius: 16px;
    max-width: 440px;
    margin: auto;
    border: 1px solid #334155;
  }
  .ortalama {
    font-size: 36px;
    font-weight: bold;
    color: #f59e0b;
    margin: 20px 0;
  }
  .kaynaklar {
    background: #0f172a;
    padding: 15px;
    border-radius: 10px;
    text-align: left;
  }
  .satir {
    display: flex;
    justify-content: space-between;
    padding: 6px 0;
    border-bottom: 1px solid #1e293b;
  }
  .hata { color: #f87171; }
  .tarih { font-size: 12px; color: #64748b; margin-top: 20px; }
</style>
</head>
<body>
<div class="kutu">
  <div class="baslik">BTC / USD Piyasa Ortalaması</div>
  <div class="ortalama" id="ortalama">Veri Bekleniyor</div>

  <div class="kaynaklar">
    <div class="satir"><span>Coinbase:</span> <strong id="coinbase">Yükleniyor...</strong></div>
    <div class="satir"><span>Kraken:</span> <strong id="kraken">Yükleniyor...</strong></div>
    <div class="satir"><span>Blockchain.com:</span> <strong id="blockchain">Yükleniyor...</strong></div>
  </div>

  <div class="tarih" id="tarih"></div>
</div>

<script>
const fiyatlar = {};

function para(fiyat) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD"
  }).format(fiyat);
}

async function veriAl(url) {
  const cevap = await fetch(url);

  if (!cevap.ok) {
    throw new Error("HTTP " + cevap.status);
  }

  return cevap.json();
}

async function coinbaseCek() {
  const data = await veriAl(
    "https://api.coinbase.com/v2/prices/BTC-USD/spot"
  );

  const fiyat = parseFloat(data.data.amount);
  fiyatlar.coinbase = fiyat;
  document.getElementById("coinbase").textContent = para(fiyat);
}

async function krakenCek() {
  const data = await veriAl(
    "https://api.kraken.com/0/public/Ticker?pair=XBTUSD"
  );

  const fiyat = parseFloat(data.result.XXBTZUSD.c[0]);
  fiyatlar.kraken = fiyat;
  document.getElementById("kraken").textContent = para(fiyat);
}

async function blockchainCek() {
  const data = await veriAl(
    "https://blockchain.info/ticker?cors=true"
  );

  const fiyat = parseFloat(data.USD.last);
  fiyatlar.blockchain = fiyat;
  document.getElementById("blockchain").textContent = para(fiyat);
}

function ortalamayiGuncelle() {
  const degerler = Object.values(fiyatlar);

  if (degerler.length === 0) {
    document.getElementById("ortalama").textContent = "Veri Alınamadı";
    return;
  }

  const ortalama = degerler.reduce((a, b) => a + b, 0) / degerler.length;
  document.getElementById("ortalama").textContent = para(ortalama);
}

async function tumunuCek() {
  const istekler = [
    coinbaseCek().catch(() => {
      document.getElementById("coinbase").textContent = "Erişilemedi";
      document.getElementById("coinbase").classList.add("hata");
    }),
    krakenCek().catch(() => {
      document.getElementById("kraken").textContent = "Erişilemedi";
      document.getElementById("kraken").classList.add("hata");
    }),
    blockchainCek().catch(() => {
      document.getElementById("blockchain").textContent = "Erişilemedi";
      document.getElementById("blockchain").classList.add("hata");
    })
  ];

  await Promise.allSettled(istekler);
  ortalamayiGuncelle();

  document.getElementById("tarih").textContent =
    "Son güncelleme: " +
    new Date().toLocaleString("tr-TR", { timeZone: "Europe/Istanbul" });
}

tumunuCek();
setInterval(tumunuCek, 30000);
</script>
</body>
</html>
