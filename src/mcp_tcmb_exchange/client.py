import datetime
import xmltodict
import httpx
from decimal import Decimal
from typing import Dict, Optional, List


class ExchangeRate:
    def __init__(
        self,
        code: str,
        name: str,
        forex_buying: Decimal,
        forex_selling: Decimal,
        banknote_buying: Decimal,
        banknote_selling: Decimal,
    ):
        self.code = code
        self.name = name
        self.forex_buying = forex_buying
        self.forex_selling = forex_selling
        self.banknote_buying = banknote_buying
        self.banknote_selling = banknote_selling

    def to_dict(self):
        return {
            "code": self.code,
            "name": self.name,
            "forex_buying": str(self.forex_buying) if self.forex_buying else None,
            "forex_selling": str(self.forex_selling) if self.forex_selling else None,
            "banknote_buying": str(self.banknote_buying) if self.banknote_buying else None,
            "banknote_selling": str(self.banknote_selling) if self.banknote_selling else None,
        }


class TCMBClient:
    def __init__(self):
        self._cache: Dict[str, Dict[str, ExchangeRate]] = {}
        self._cache_time: Dict[str, datetime.datetime] = {}

    async def _fetch_xml(self, date: Optional[str] = None) -> str:
        if date:
            # Format: YYYY-MM-DD convert to YYYYMM/DDMMYYYY.xml
            dt = datetime.datetime.strptime(date, "%Y-%m-%d")
            url = (
                f"https://www.tcmb.gov.tr/kurlar/{dt.strftime('%Y%m')}/{dt.strftime('%d%m%Y')}.xml"
            )
        else:
            url = "https://www.tcmb.gov.tr/kurlar/today.xml"

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.content.decode("iso-8859-9", errors="replace")

    async def get_all_rates(self, date: Optional[str] = None) -> Dict[str, ExchangeRate]:
        cache_key = date or "today"
        now = datetime.datetime.now()

        if cache_key in self._cache and cache_key in self._cache_time:
            if (now - self._cache_time[cache_key]).total_seconds() < 1800:  # 30 dk
                return self._cache[cache_key]

        xml_data = await self._fetch_xml(date)
        data = xmltodict.parse(xml_data)

        rates = {}
        # TRY is the base currency
        rates["TRY"] = ExchangeRate(
            "TRY", "TÜRK LİRASI", Decimal("1.0"), Decimal("1.0"), Decimal("1.0"), Decimal("1.0")
        )

        for currency in data["Tarih_Date"]["Currency"]:
            code = currency.get("@CurrencyCode")
            name = currency.get("Isim")
            try:
                forex_buying = (
                    Decimal(currency.get("ForexBuying")) if currency.get("ForexBuying") else None
                )
                forex_selling = (
                    Decimal(currency.get("ForexSelling")) if currency.get("ForexSelling") else None
                )
                banknote_buying = (
                    Decimal(currency.get("BanknoteBuying"))
                    if currency.get("BanknoteBuying")
                    else None
                )
                banknote_selling = (
                    Decimal(currency.get("BanknoteSelling"))
                    if currency.get("BanknoteSelling")
                    else None
                )

                if forex_buying or forex_selling:
                    rates[code] = ExchangeRate(
                        code, name, forex_buying, forex_selling, banknote_buying, banknote_selling
                    )
            except Exception:
                pass

        self._cache[cache_key] = rates
        self._cache_time[cache_key] = now
        return rates

    async def get_rate(
        self, currency_code: str, date: Optional[str] = None
    ) -> Optional[ExchangeRate]:
        rates = await self.get_all_rates(date)
        return rates.get(currency_code.upper())

    async def convert(
        self, amount: Decimal, from_currency: str, to_currency: str, date: Optional[str] = None
    ) -> Dict:
        rates = await self.get_all_rates(date)
        from_curr = from_currency.upper()
        to_curr = to_currency.upper()

        if from_curr not in rates:
            raise ValueError(f"Currency {from_curr} not found")
        if to_curr not in rates:
            raise ValueError(f"Currency {to_curr} not found")

        from_rate = rates[from_curr].forex_selling or rates[from_curr].forex_buying
        to_rate = rates[to_curr].forex_selling or rates[to_curr].forex_buying

        if not from_rate or not to_rate:
            raise ValueError("Exchange rate is missing for calculation")

        value_in_try = amount * from_rate
        result = value_in_try / to_rate

        return {
            "amount": str(amount),
            "from_currency": from_curr,
            "to_currency": to_curr,
            "result": str(result.quantize(Decimal("0.0001"))),
            "date": date or "today",
        }
