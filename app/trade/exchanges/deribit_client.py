import httpx
from datetime import datetime, timezone
from typing import List, Dict, Optional
from app.trade.exchanges.exchange_client import ExchangeClient
from app.trade.entities.funding_rate import FundingRate
from app.trade.entities.order_book import OrderBook
from app.trade.entities.fees import Fees

class DeribitClient(ExchangeClient):
    BASE_URL = "https://www.deribit.com/api/v2"

    def __init__(self):
        self._symbol_map: Optional[Dict[str, str]] = None

    @property
    def symbol_map(self) -> dict:
        if self._symbol_map is None:
            return self.fetch_symbol_map()
        return self._symbol_map

    async def fetch_symbol_map(self):
        if self._symbol_map is not None:
            return

        async with httpx.AsyncClient() as client:
            res = await client.get(
                f"{self.BASE_URL}/public/get_instruments",
                params={"kind": "future", "expired": False}
            )
            res.raise_for_status()
            instruments = res.json()["result"]

            symbol_map = {}
            for inst in instruments:
                if inst.get("settlement_period") == "perpetual":
                    base = inst["base_currency"]
                    quote = inst["quote_currency"]
                    symbol = f"{base}{quote}"
                    symbol_map[symbol] = inst["instrument_name"]

            self._symbol_map = symbol_map
            return self._symbol_map

    async def fetch_funding_rate(self, symbol: str) -> FundingRate:
        await self.fetch_symbol_map()
        deribit_symbol = self._symbol_map.get(symbol)
        if not deribit_symbol:
            raise ValueError(f"No Deribit mapping for symbol {symbol}")

        now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)

        async with httpx.AsyncClient() as client:
            res = await client.get(
                f"{self.BASE_URL}/public/get_funding_rate_history",
                params={
                    "instrument_name": deribit_symbol,
                    "start_timestamp": 0,
                    "end_timestamp": now_ms,
                    "count": 1
                }
            )
            res.raise_for_status()
            items = res.json()["result"]
            if not items:
                raise ValueError(f"No funding rate data returned for {symbol}")

            data = items[0]
            return FundingRate(
                symbol=symbol,
                funding_rate=float(data["interest_1h"]),
                timestamp=datetime.fromtimestamp(data["timestamp"] / 1000)
            )

    async def fetch_order_book(self, symbol: str) -> OrderBook:
        await self.fetch_symbol_map()
        deribit_symbol = self._symbol_map.get(symbol)
        if not deribit_symbol:
            raise ValueError(f"No Deribit mapping for symbol {symbol}")

        async with httpx.AsyncClient() as client:
            res = await client.get(
                f"{self.BASE_URL}/public/get_order_book",
                params={"instrument_name": deribit_symbol}
            )
            res.raise_for_status()
            data = res.json()["result"]

            bids = [(float(price), float(amount)) for price, amount in data["bids"]]
            asks = [(float(price), float(amount)) for price, amount in data["asks"]]

            return OrderBook(
                symbol=symbol,
                bids=bids,
                asks=asks,
                timestamp=datetime.fromtimestamp(data["timestamp"] / 1000)
            )

    async def fetch_fees(self, symbol: str) -> Fees:
        # No official API for public fees; Deribit's taker/maker structure is static for perpetuals.
        return Fees(taker=0.0005, maker=0.0002)