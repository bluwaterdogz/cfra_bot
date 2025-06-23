import httpx
from datetime import datetime, timezone
from app.trade.exchanges.exchange_client import ExchangeClient
from app.trade.entities.funding_rate import FundingRate
from app.trade.entities.order_book import OrderBook
from app.trade.entities.fees import Fees

DEFAULT_MAKER_FEE = 0.0001
DEFAULT_TAKER_FEE = 0.0006

class BybitClient(ExchangeClient):
    BASE_URL = "https://api.bybit.com"

    async def fetch_funding_rate(self, symbol: str) -> FundingRate:
        async with httpx.AsyncClient() as client:
            res = await client.get(
                f"{self.BASE_URL}/v5/market/funding/prev-funding-rate",
                params={"category": "contract", "symbol": symbol}
            )
            # res = await client.get(f"{self.BASE_URL}/v2/public/funding/prev-funding-rate", params={"symbol": symbol})
            res.raise_for_status()
            data = res.json()["result"]
            return FundingRate(
                symbol=data["symbol"],
                funding_rate=float(data["fundingRate"]),
                timestamp=datetime.fromtimestamp(data["fundingTime"] / 1000)
            )

    async def fetch_order_book(self, symbol: str) -> OrderBook:
        async with httpx.AsyncClient() as client:
            res = await client.get(
                f"{self.BASE_URL}/v5/market/orderbook",
                params={"category": "linear", "symbol": symbol, "limit": 25}
            )
            res.raise_for_status()
            data = res.json()["result"]

            # Each entry is [price: str, size: str]
            bids = [(float(price), float(size)) for price, size in data["b"]]
            asks = [(float(price), float(size)) for price, size in data["a"]]

            return OrderBook(
                symbol=symbol,
                bids=bids,
                asks=asks,
                timestamp=datetime.now(timezone.utc)  # API does not provide timestamp
            )

    async def fetch_fees(self, symbol: str) -> Fees:
        # Bybit fees are usually static and may need to be hardcoded or scraped from docs if no endpoint is available.
        return Fees(taker=DEFAULT_TAKER_FEE, maker=DEFAULT_MAKER_FEE)