import pytest
from unittest.mock import AsyncMock
from decimal import Decimal
import json

from mcp_tcmb_exchange.client import TCMBClient, ExchangeRate
from mcp_tcmb_exchange.server import call_tool

MOCK_XML = """<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="isokur.xsl"?>
<Tarih_Date Tarih="09.03.2026" Date="03/09/2026"  Bulten_No="2026/01">
    <Currency CrossOrder="0" Kod="USD" CurrencyCode="USD">
        <Unit>1</Unit>
        <Isim>ABD DOLARI</Isim>
        <CurrencyName>US DOLLAR</CurrencyName>
        <ForexBuying>32.5000</ForexBuying>
        <ForexSelling>32.5500</ForexSelling>
        <BanknoteBuying>32.4800</BanknoteBuying>
        <BanknoteSelling>32.5800</BanknoteSelling>
    </Currency>
    <Currency CrossOrder="1" Kod="EUR" CurrencyCode="EUR">
        <Unit>1</Unit>
        <Isim>EURO</Isim>
        <CurrencyName>EURO</CurrencyName>
        <ForexBuying>35.0000</ForexBuying>
        <ForexSelling>35.0500</ForexSelling>
        <BanknoteBuying>34.9500</BanknoteBuying>
        <BanknoteSelling>35.1000</BanknoteSelling>
    </Currency>
</Tarih_Date>
"""


@pytest.fixture
def tcmb_client_mock(monkeypatch):
    client = TCMBClient()
    client._fetch_xml = AsyncMock(return_value=MOCK_XML)
    return client


@pytest.fixture
def override_server_client(tcmb_client_mock, monkeypatch):
    import mcp_tcmb_exchange.server

    monkeypatch.setattr(mcp_tcmb_exchange.server, "tcmb_client", tcmb_client_mock)


@pytest.mark.asyncio
async def test_get_rate(tcmb_client_mock):
    rate = await tcmb_client_mock.get_rate("USD")
    assert rate is not None
    assert rate.code == "USD"
    assert rate.forex_buying == Decimal("32.5000")


@pytest.mark.asyncio
async def test_convert(tcmb_client_mock):
    # 100 USD -> TRY (100 * 32.5500 / 1.0) = 3255.0
    res = await tcmb_client_mock.convert(Decimal("100"), "USD", "TRY")
    assert res["result"] == "3255.0000"

    # 1000 TRY -> EUR (1000 * 1.0 / 35.0500) = 28.53067... -> 28.5307
    res2 = await tcmb_client_mock.convert(Decimal("1000"), "TRY", "EUR")
    assert res2["result"] == "28.5307"


@pytest.mark.asyncio
async def test_tool_get_exchange_rate(override_server_client):
    result = await call_tool("get_exchange_rate", {"currency_code": "USD"})
    assert not result.isError
    data = json.loads(result.content[0].text)
    assert data["code"] == "USD"
    assert data["forex_buying"] == "32.5000"


@pytest.mark.asyncio
async def test_tool_invalid_currency(override_server_client):
    result = await call_tool("get_exchange_rate", {"currency_code": "INVALID"})
    assert result.isError
    data = json.loads(result.content[0].text)
    assert "error" in data


@pytest.mark.asyncio
async def test_cache_hits_only_once(tcmb_client_mock):
    await tcmb_client_mock.get_all_rates()
    await tcmb_client_mock.get_all_rates()
    tcmb_client_mock._fetch_xml.assert_called_once()
