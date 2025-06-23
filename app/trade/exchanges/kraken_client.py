import httpx
from datetime import datetime, timezone
from typing import List

from app.trade.exchanges.exchange_client import ExchangeClient
from app.trade.entities.funding_rate import FundingRate
from app.trade.entities.order_book import OrderBook
from app.trade.entities.fees import Fees

DEFAULT_TAKER_FEE = 0.0004
DEFAULT_MAKER_FEE = 0.0002

class KrakenClient(ExchangeClient):
    def __init__(self):
        self.base_url = "https://futures.kraken.com/derivatives/api/v3"

    async def fetch_funding_rate(self, symbol: str) -> FundingRate:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{self.base_url}/tickers")
            r.raise_for_status()
            tickers = r.json()["tickers"]
            for t in tickers:
                if t["symbol"] == symbol:
                    return FundingRate(
                        symbol=symbol,
                        funding_rate=float(t["fundingRate"]),
                        timestamp=datetime.now(timezone.utc)
                    )
            raise ValueError(f"Symbol {symbol} not found in Kraken tickers.")

    async def fetch_order_book(self, symbol: str) -> OrderBook:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{self.base_url}/orderbook", params={"symbol": symbol})
            r.raise_for_status()
            data = r.json()
            order_book = data["orderBook"]
            bids = [(float(price), float(size)) for price, size in order_book["bids"][:20]]
            asks = [(float(price), float(size)) for price, size in order_book["asks"][:20]]
            return OrderBook(
                symbol=symbol,
                bids=bids,
                asks=asks,
                timestamp=datetime.now(timezone.utc)
            )

    async def fetch_fees(self, symbol: str) -> Fees:
        return Fees(maker=DEFAULT_MAKER_FEE, taker=DEFAULT_TAKER_FEE)

    async def fetch_tickers(self) -> List[str]:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{self.base_url}/tickers")
            r.raise_for_status()
            return [item["symbol"] for item in r.json()["tickers"]]