import json
import asyncio
from decimal import Decimal
from typing import Any
from mcp.server.models import InitializationOptions
from mcp.server import Server, NotificationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, CallToolResult

from .client import TCMBClient

server = Server("mcp_tcmb_exchange")
tcmb_client = TCMBClient()


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_exchange_rate",
            description="Tek dövizin günlük TCMB kurunu getirir",
            inputSchema={
                "type": "object",
                "properties": {
                    "currency_code": {
                        "type": "string",
                        "description": "Currency code like USD, EUR",
                    },
                    "date": {"type": "string", "description": "YYYY-MM-DD format (optional)"},
                },
                "required": ["currency_code"],
            },
        ),
        Tool(
            name="list_all_rates",
            description="Tüm TCMB kurlarını listeler",
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "YYYY-MM-DD format (optional)"}
                },
            },
        ),
        Tool(
            name="convert_currency",
            description="TL↔Döviz veya Döviz↔Döviz çevirimi",
            inputSchema={
                "type": "object",
                "properties": {
                    "amount": {"type": "string", "description": "Amount to convert"},
                    "from_currency": {
                        "type": "string",
                        "description": "Source currency code (e.g. USD, TRY)",
                    },
                    "to_currency": {
                        "type": "string",
                        "description": "Target currency code (e.g. TRY, EUR)",
                    },
                    "date": {"type": "string", "description": "YYYY-MM-DD format (optional)"},
                },
                "required": ["amount", "from_currency", "to_currency"],
            },
        ),
        Tool(
            name="convert_to_multiple",
            description="Bir tutarı aynı anda birçok dövize çevirir",
            inputSchema={
                "type": "object",
                "properties": {
                    "amount": {"type": "string", "description": "Amount to convert"},
                    "target_currencies": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of target currency codes",
                    },
                    "from_currency": {
                        "type": "string",
                        "description": "Source currency code (default: TRY)",
                    },
                    "date": {"type": "string", "description": "YYYY-MM-DD format (optional)"},
                },
                "required": ["amount", "target_currencies"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> CallToolResult:
    try:
        if name == "get_exchange_rate":
            code = arguments["currency_code"]
            date = arguments.get("date")
            rate = await tcmb_client.get_rate(code, date)
            if not rate:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=json.dumps(
                                {"error": f"Currency {code} not found"}, ensure_ascii=False
                            ),
                        )
                    ],
                    isError=True,
                )
            return CallToolResult(
                content=[
                    TextContent(
                        type="text", text=json.dumps(rate.to_dict(), ensure_ascii=False, indent=2)
                    )
                ]
            )

        elif name == "list_all_rates":
            date = arguments.get("date")
            rates = await tcmb_client.get_all_rates(date)
            result_dict = {k: v.to_dict() for k, v in rates.items()}
            return CallToolResult(
                content=[
                    TextContent(
                        type="text", text=json.dumps(result_dict, ensure_ascii=False, indent=2)
                    )
                ]
            )

        elif name == "convert_currency":
            amount = Decimal(arguments["amount"])
            from_currency = arguments["from_currency"]
            to_currency = arguments["to_currency"]
            date = arguments.get("date")
            result = await tcmb_client.convert(amount, from_currency, to_currency, date)
            return CallToolResult(
                content=[
                    TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))
                ]
            )

        elif name == "convert_to_multiple":
            amount = Decimal(arguments["amount"])
            from_currency = arguments.get("from_currency", "TRY")
            targets = arguments["target_currencies"]
            date = arguments.get("date")
            results = {}
            for target in targets:
                try:
                    res = await tcmb_client.convert(amount, from_currency, target, date)
                    results[target] = res["result"]
                except Exception as e:
                    results[target] = {"error": str(e)}
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {
                                "amount": str(amount),
                                "from": from_currency,
                                "results": results,
                                "date": date or "today",
                            },
                            ensure_ascii=False,
                            indent=2,
                        ),
                    )
                ]
            )

        else:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps({"error": f"Tool {name} not known"}, ensure_ascii=False),
                    )
                ],
                isError=True,
            )
    except Exception as e:
        return CallToolResult(
            content=[
                TextContent(type="text", text=json.dumps({"error": str(e)}, ensure_ascii=False))
            ],
            isError=True,
        )


def main():
    async def run():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="mcp_tcmb_exchange",
                    server_version="0.1.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )

    asyncio.run(run())
