import httpx
from datetime import datetime
from app.trade.exchanges.exchange_client import ExchangeClient
from app.trade.entities.funding_rate import FundingRate
from app.trade.entities.order_book import OrderBook
from app.trade.entities.fees import Fees

class OKXClient(ExchangeClient):
    BASE_URL = "https://www.okx.com"

    async def fetch_funding_rate(self, symbol: str) -> FundingRate:
        inst_id = f"{symbol[:symbol.index('USDT')]}-USDT-SWAP"
        async with httpx.AsyncClient() as client:
            res = await client.get(
                f"{self.BASE_URL}/api/v5/public/funding-rate",
                params={"instId": inst_id}
            )
            res.raise_for_status()
            data = res.json()["data"][0]

        return FundingRate(
            symbol=symbol,
            funding_rate=float(data["fundingRate"]),
            timestamp=datetime.fromtimestamp(int(data["fundingTime"]) / 1000)
        )

    async def fetch_order_book(self, symbol: str) -> OrderBook:
        inst_id = f"{symbol[:symbol.index('USDT')]}-USDT-SWAP"
        async with httpx.AsyncClient() as client:
            res = await client.get(
                f"{self.BASE_URL}/api/v5/market/books",
                params={"instId": inst_id, "sz": "20"}
            )
            res.raise_for_status()
            data = res.json()["data"][0]

        bids = [(float(b[0]), float(b[1])) for b in data["bids"]]
        asks = [(float(a[0]), float(a[1])) for a in data["asks"]]

        return OrderBook(
            symbol=symbol,
            bids=bids,
            asks=asks,
            timestamp=datetime.fromtimestamp(int(data["ts"]) / 1000)
        )

    async def fetch_fees(self, symbol: str) -> Fees:
        return Fees(taker=0.0005, maker=0.0002)