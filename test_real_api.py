import asyncio
import json
from decimal import Decimal
from src.mcp_tcmb_exchange.client import TCMBClient

async def test_real_api():
    client = TCMBClient()
    
    print("----- GERÇEK TCMB API TESTİ -----")
    
    print("\n1. USD Güncel Kuru Çekiliyor...")
    usd_rate = await client.get_rate("USD")
    if usd_rate:
        print(f"USD Alış: {usd_rate.forex_buying} TRY | USD Satış: {usd_rate.forex_selling} TRY")
    else:
        print("USD Kuru Bulunamadı!")

    print("\n2. EUR Güncel Kuru Çekiliyor...")
    eur_rate = await client.get_rate("EUR")
    if eur_rate:
        print(f"EUR Alış: {eur_rate.forex_buying} TRY | EUR Satış: {eur_rate.forex_selling} TRY")
    else:
        print("EUR Kuru Bulunamadı!")

    print("\n3. Çeviri Testi (100 USD -> TRY)")
    try:
        convert_to_try = await client.convert(Decimal("100"), "USD", "TRY")
        print(f"Sonuç: 100 USD = {convert_to_try['result']} TRY")
    except Exception as e:
        print(f"Hata: {e}")
        
    print("\n4. Çeviri Testi (1000 TRY -> EUR)")
    try:
        convert_to_eur = await client.convert(Decimal("1000"), "TRY", "EUR")
        print(f"Sonuç: 1000 TRY = {convert_to_eur['result']} EUR")
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    asyncio.run(test_real_api())
