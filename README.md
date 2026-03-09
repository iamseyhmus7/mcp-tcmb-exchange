# 🏦 mcp-tcmb-exchange

[![PyPI Version](https://img.shields.io/pypi/v/mcp-tcmb-exchange.svg)](https://pypi.org/project/mcp-tcmb-exchange/)
[![Python Version](https://img.shields.io/pypi/pyversions/mcp-tcmb-exchange.svg)](https://pypi.org/project/mcp-tcmb-exchange/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

**TCMB (Türkiye Cumhuriyet Merkez Bankası)** resmi günlük döviz kurlarını **MCP (Model Context Protocol)** üzerinden AI asistanlarına (Claude, Cursor, Gemini vb.) sunan güçlü ve güvenilir bir Python sunucusudur.

---

## ✨ Özellikler

- **Gerçek Zamanlı Veri:** TCMB'nin güncel döviz kurlarına anında erişim.
- **Hassas Hesaplama:** Tamamı `Decimal` kullanılarak geliştirilmiş, yuvarlama hatalarından arındırılmış finansal hesaplamalar.
- **Geçmiş Tarih Desteği:** İstenilen tarihteki (YYYY-MM-DD) kurları sorgulayabilme.
- **Çoklu Çeviri:** Tek bir tutarı aynı anda birden fazla döviz cinsine çevirebilme.
- **Hızlı ve Asenkron:** `httpx` ve asenkron mimari ile gecikmesiz haberleşme.
- **Dahili Önbellekleme:** Gereksiz ağ isteklerini önlemek için 30 dakikalık memory cache.

## 🛠️ MCP Araçları (Tools)

Bu sunucu, AI asistanlarına aşağıdaki araçları sağlar:

| Araç Adı | Açıklama | Zorunlu Parametreler |
|----------|----------|----------------------|
| `get_exchange_rate` | Tek bir dövizin günlük TCMB kurunu getirir. | `currency_code` (Örn: USD, EUR) |
| `list_all_rates` | Tüm TCMB kurlarını detaylı olarak listeler. | *Yok* |
| `convert_currency` | TL↔Döviz veya Döviz↔Döviz arasında çeviri yapar. | `amount`, `from_currency`, `to_currency` |
| `convert_to_multiple` | Bir tutarı aynı anda birçok farklı dövize çevirir. | `amount`, `target_currencies` |

*Not: Tüm araçlar opsiyonel olarak `date` (YYYY-MM-DD) parametresi alabilir. Belirtilmezse o günkü güncel kur kullanılır.*

## 🚀 Çalıştırma Yöntemleri

Sunucuyu sisteminizde çalıştırmak için aşağıdaki yöntemlerden birini seçebilirsiniz (Python 3.10 veya üzeri gereklidir):

### 1. PyPI Üzerinden Pip Install Sonrası:
Eğer paketi global veya sanal ortama kurduysanız, terminalden direkt olarak komutu çağırabilirsiniz.
```bash
pip install mcp-tcmb-exchange
```

`mcp_config.json` dosyanıza şu şekilde ekleyebilirsiniz:
```json
{
  "mcpServers": {
    "mcp-tcmb-exchange": {
      "command": "mcp-tcmb-exchange"
    }
  }
}
```

### 2. UVX ile (Sıfır Kurulum, Anında Çalıştırma):
Sisteminizde `uv` yüklüyse, hiçbir kurulum yapmadan izole bir ortamda sunucuyu anında başlatabilirsiniz.

`mcp_config.json` dosyanıza şu şekilde ekleyebilirsiniz:
```json
{
  "mcpServers": {
    "mcp-tcmb-exchange": {
      "command": "uvx",
      "args": ["mcp-tcmb-exchange"]
    }
  }
}
```

### 3. GitHub Kaynak Kodundan Çalıştırma:
Projeyi klonlayıp kendi yerel ortamınızda geliştirmek veya çalıştırmak isterseniz:
```bash
git clone https://github.com/iamseyhmus7/mcp-tcmb-exchange.git
cd mcp-tcmb-exchange
pip install -e .
```

`mcp_config.json` dosyanıza şu şekilde ekleyebilirsiniz:
```json
{
  "mcpServers": {
    "mcp-tcmb-exchange": {
      "command": "python",
      "args": ["-m", "mcp_tcmb_exchange"]
    }
  }
}
```

## ⚠️ Önemli Uyarılar ve Kısıtlamalar

- **Güncelleme Saati:** TCMB kurları iş günlerinde saat **15:30** civarında güncellenmektedir.
- **Tatiller:** Hafta sonu ve resmi tatillerde yeni kur yayınlanmaz, bir önceki iş gününün kuru geçerli olur.
- **Yatırım Tavsiyesi Değildir:** Bu araç sadece bilgilendirme amaçlıdır. Herhangi bir yatırım tavsiyesi içermez.
- **Resmi Kaynak:** Kesin ve resmi işlemler için [tcmb.gov.tr](https://www.tcmb.gov.tr/) adresini referans alınız.

## 📄 Lisans

Bu proje [MIT](https://opensource.org/licenses/MIT) lisansı altında açık kaynak olarak paylaşılmıştır.

## 👨‍💻 Geliştirici
- [Şeyhmus OK](https://github.com/iamseyhmus7)
