# AGENTS.md — mcp-tcmb-exchange

## 🎯 Proje Amacı

Bu proje **TCMB (Türkiye Cumhuriyet Merkez Bankası)** resmi günlük döviz kurlarını
**MCP (Model Context Protocol)** üzerinden AI asistanlarına sunan bir Python server'dır.

Claude, Gemini, Cursor veya MCP destekleyen herhangi bir AI aracı bu server'a bağlanarak
gerçek zamanlı TCMB kur verisi alabilir, döviz çevirimi yapabilir ve kur geçmişini sorgulayabilir.

---

## 🏗️ Mimari Genel Bakış

```
AI Asistan (Claude / Gemini / Cursor)
        │
        │  MCP Protokolü (JSON-RPC 2.0 over stdio)
        ▼
┌─────────────────────────────────┐
│         server.py               │
│  ┌─────────────┐                │
│  │ list_tools()│ ← Araç listesi │
│  └─────────────┘                │
│  ┌─────────────┐                │
│  │ call_tool() │ ← Araç çalıştır│
│  └──────┬──────┘                │
└─────────┼───────────────────────┘
          │
          ▼
┌─────────────────────────────────┐
│         client.py               │
│  ┌──────────────────────┐       │
│  │    TCMBClient        │       │
│  │  - get_rate()        │       │
│  │  - get_all_rates()   │       │
│  │  - convert()         │       │
│  │  - _cache (30 dk)    │       │
│  └──────────┬───────────┘       │
└─────────────┼───────────────────┘
              │  HTTP (httpx)
              ▼
   https://www.tcmb.gov.tr
   /kurlar/today.xml   (ISO-8859-9 encoding)
```

---

## 📦 Teknoloji Yığını

| Katman | Teknoloji | Versiyon | Neden? |
|--------|-----------|----------|--------|
| MCP Protokolü | `mcp` | ≥1.19.0 | Resmi Python SDK |
| HTTP İstemci | `httpx` | ≥0.28.0 | Async desteği, `requests` yerine |
| XML Parse | `xmltodict` | ≥0.13.0 | TCMB XML → dict dönüşümü |
| Paketleme | `hatchling` | latest | Modern pyproject.toml build backend |
| Test | `pytest` + `pytest-asyncio` | ≥8.3.0 | Async test desteği |
| Linter | `ruff` | ≥0.8.0 | Hızlı Python linter |

---

## 📁 Klasör Yapısı

```
mcp-tcmb-exchange/
├── AGENTS.md                          ← Bu dosya (Antigravity okur)
├── README.md                          ← Kullanıcı dokümantasyonu
├── PUBLISHING.md                      ← PyPI yayın rehberi
├── pyproject.toml                     ← Paket tanımı + bağımlılıklar
│
├── src/
│   └── mcp_tcmb_exchange/
│       ├── __init__.py                ← Sadece __version__ = "0.1.0"
│       ├── __main__.py                ← `python -m mcp_tcmb_exchange` girişi
│       ├── client.py                  ← TCMB iş mantığı (ExchangeRate + TCMBClient)
│       └── server.py                  ← MCP araçları (list_tools + call_tool)
│
├── tests/
│   └── test_server.py                 ← Pytest testleri (AsyncMock kullanır)
│
└── .agent/
    ├── rules/
    │   ├── python-style.md            ← Kod stili kuralları
    │   └── mcp-protocol.md            ← MCP araç ekleme kuralları
    ├── workflows/
    │   ├── add-tool.md                ← /add-tool komutu
    │   └── publish-to-pypi.md         ← /publish komutu
    └── skills/
        └── mcp-server/
            └── SKILL.md               ← MCP geliştirme rehberi
```

---

## 🛠️ Mevcut MCP Araçları

| Araç | Açıklama | Zorunlu Parametre |
|------|----------|-------------------|
| `get_exchange_rate` | Tek dövizin günlük TCMB kurunu getirir | `currency_code` (USD, EUR...) |
| `list_all_rates` | Tüm TCMB kurlarını listeler | — |
| `convert_currency` | TL↔Döviz veya Döviz↔Döviz çevirimi | `amount`, `from_currency`, `to_currency` |
| `convert_to_multiple` | Bir tutarı aynı anda birçok dövize çevirir | `amount`, `target_currencies` |

Tüm araçlar opsiyonel `date` (YYYY-MM-DD) parametresi alır.
Tarih girilmezse bugünkü TCMB kuru kullanılır.

---

## 🔑 Değişmez Kod Kuralları

### Parasal Hesaplar
```python
# ✅ DOĞRU
from decimal import Decimal
amount = Decimal("1000.50")
result = amount * Decimal("32.70")

# ❌ YANLIŞ — float kullanma
amount = 1000.50
result = amount * 32.70
```

### HTTP İstekleri
```python
# ✅ DOĞRU
import httpx
async with httpx.AsyncClient(timeout=10.0) as client:
    resp = await client.get(url)

# ❌ YANLIŞ
import requests
resp = requests.get(url)
```

### MCP Araç Çıktısı
```python
# ✅ Başarılı sonuç
return CallToolResult(
    content=[TextContent(type="text", text=json.dumps(data, ensure_ascii=False, indent=2))]
)

# ✅ Hata sonucu
return CallToolResult(
    content=[TextContent(type="text", text=json.dumps({"error": msg}, ensure_ascii=False))],
    isError=True,
)
```

### TCMB XML Encoding
```python
# TCMB, ISO-8859-9 (Latin-5/Türkçe) encoding kullanır
content = resp.content.decode("iso-8859-9", errors="replace")
```

---

## 🧪 Test Kuralları

- Testlerde **asla** gerçek TCMB API'ye istek atılmaz → `AsyncMock` kullan
- Her araç için minimum: temel kullanım + geçersiz girdi + edge case testleri
- `pytest-asyncio` ile async test: `@pytest.mark.asyncio`
- Önbellekleme testi: `_fetch_xml` sadece 1 kez çağrılmalı

```python
# Test fixture şablonu
@pytest.fixture
def client_with_mock():
    c = TCMBClient()
    c.get_all_rates = AsyncMock(return_value=MOCK_RATES)
    return c
```

---

## 🚀 Yayın Bilgileri

- **PyPI paketi:** `mcp-tcmb-exchange`
- **Çalıştırma komutu:** `mcp-tcmb-exchange` (pip install sonrası)
- **uvx ile:** `uvx mcp-tcmb-exchange` (kurulum gerekmez)
- **Versiyon yönetimi:** `pyproject.toml` → GitHub Release → otomatik PyPI

---

## 🌍 Toplulukla Paylaşım

Proje tamamlandıktan sonra aşağıdaki platformlara eklenmesi gerekir.
README.md oluştururken bu platformlar için gerekli başlık, açıklama ve
kurulum talimatlarının eksiksiz olmasına dikkat et.

### 1. Smithery.ai — MCP Server Dizini
**URL:** https://smithery.ai

Smithery, MCP server'larının keşfedildiği ana platformdur.
Buraya eklenmek için `smithery.yaml` dosyası gerekir:

```yaml
# smithery.yaml — projenin köküne ekle
name: mcp-tcmb-exchange
description: TCMB (Turkish Central Bank) daily exchange rates via MCP
categories:
  - finance
  - currency
  - turkey
license: MIT
startCommand:
  type: stdio
  command: mcp-tcmb-exchange
  # veya kurulum gerekmeden:
  # command: uvx
  # args: ["mcp-tcmb-exchange"]
```

Smithery'ye ekleme: https://smithery.ai/submit adresinden form doldurulur.

---

### 2. GitHub — Topluluk MCP Listeleri

Aşağıdaki repolara PR açılarak server duyurulur:

**a) punkpeye/awesome-mcp-servers** ⭐ En popüler liste
```
Repo: https://github.com/punkpeye/awesome-mcp-servers
Eklenecek bölüm: Finance
Eklenecek satır:
- [mcp-tcmb-exchange](https://github.com/KULLANICI_ADIN/mcp-tcmb-exchange) -
  TCMB (Turkish Central Bank) daily exchange rates for currency conversion. (Python)
```

**b) modelcontextprotocol/servers** — Resmi MCP repo'su
```
Repo: https://github.com/modelcontextprotocol/servers
Eklenecek bölüm: Community Servers
```

---

### 3. PyPI — Python Paket İndeksi
**URL:** https://pypi.org/project/mcp-tcmb-exchange

GitHub Release oluşturulunca `.github/workflows/publish.yml`
aracılığıyla otomatik olarak yayınlanır. Manuel adım gerekmez.

---

### Yayın Sırası

```
1. GitHub repo oluştur ve push et
2. pyproject.toml'daki KULLANICI_ADIN'ı gerçek GitHub adıyla değiştir
3. smithery.yaml dosyasını oluştur
4. GitHub'da v0.1.0 Release oluştur → PyPI'ya otomatik gider
5. smithery.ai/submit adresine başvur
6. punkpeye/awesome-mcp-servers reposuna PR aç
7. modelcontextprotocol/servers reposuna PR aç
```

---

## ⚠️ Önemli Kısıtlar

- TCMB kurları **iş günlerinde ~15:30'da** güncellenir
- Hafta sonu ve resmi tatillerde yeni kur yayınlanmaz
- Bu araç **yatırım tavsiyesi vermez**
- Resmi işlemler için [tcmb.gov.tr](https://www.tcmb.gov.tr) kullanılmalıdır
- `.env` dosyası veya API key **asla commit'e dahil edilmez**

---

## 📝 Git Commit Kuralları

```
feat: yeni araç veya özellik eklendi
fix: hata düzeltildi
test: test eklendi veya güncellendi
docs: README veya dokümantasyon güncellendi
chore: bağımlılık güncellemesi veya versiyon değişikliği
refactor: davranış değiştirmeyen kod düzenlemesi
```