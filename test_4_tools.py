import asyncio
import json
from src.mcp_tcmb_exchange.server import call_tool

async def test_tools_real_api():
    print("----- GERÇEK TCMB API İLE 4 TOOL'UN TESTİ -----\n")

    # 1. get_exchange_rate Tool
    print("🚀 TOOL 1: get_exchange_rate (Sadece EUR Kurunu Sorgulama)")
    result1 = await call_tool("get_exchange_rate", {"currency_code": "EUR"})
    if result1.isError:
        print(f"❌ HATA: {result1.content[0].text}")
    else:
        print(f"✅ BAŞARILI: {result1.content[0].text}\n")

    # 2. list_all_rates Tool
    print("🚀 TOOL 2: list_all_rates (Tüm TCMB Kurlarını Getirme)")
    result2 = await call_tool("list_all_rates", {})
    if result2.isError:
        print(f"❌ HATA: {result2.content[0].text}")
    else:
        # Çıktı çok uzun olmaması için sadece ilk yüz karakteri ve kaç adet kur geldiğini yazdıralım.
        data2 = json.loads(result2.content[0].text)
        print(f"✅ BAŞARILI: Toplam {len(data2)} para birimi çekildi. Örnek Anahtarlar: {list(data2.keys())[:5]}\n")

    # 3. convert_currency Tool
    print("🚀 TOOL 3: convert_currency (1000 USD'yi TRY'ye Çevirme)")
    result3 = await call_tool("convert_currency", {
        "amount": "1000",
        "from_currency": "USD",
        "to_currency": "TRY"
    })
    if result3.isError:
        print(f"❌ HATA: {result3.content[0].text}")
    else:
        print(f"✅ BAŞARILI: {result3.content[0].text}\n")

    # 4. convert_to_multiple Tool
    print("🚀 TOOL 4: convert_to_multiple (5000 TRY'yi USD ve EUR'ya Aynı Anda Çevirme)")
    result4 = await call_tool("convert_to_multiple", {
        "amount": "5000",
        "from_currency": "TRY",
        "target_currencies": ["USD", "EUR"]
    })
    if result4.isError:
        print(f"❌ HATA: {result4.content[0].text}")
    else:
        print(f"✅ BAŞARILI: {result4.content[0].text}\n")


if __name__ == "__main__":
    asyncio.run(test_tools_real_api())
