import httpx
from datetime import datetime
from app.trade.exchanges.exchange_client import ExchangeClient
from app.trade.entities.funding_rate import FundingRate
from app.trade.entities.order_book import OrderBook
from app.trade.entities.fees import Fees

DEFAULT_TAKER_FEE = 0.0004
DEFAULT_MAKER_FEE = 0.0002

class BinanceClient(ExchangeClient):
    def __init__(self):
        self.api_url = "https://fapi.binance.com/fapi/v1"
        self.funding_url = f"{self.api_url}/fundingRate"
        self.order_book_url = f"{self.api_url}/depth"

    async def fetch_funding_rate(self, symbol: str) -> FundingRate:
        async with httpx.AsyncClient() as client:
            r = await client.get(self.funding_url, params={"symbol": symbol, "limit": 1})
            r.raise_for_status()
            data = r.json()[0]
            return FundingRate(
                symbol=data["symbol"],
                funding_rate=float(data["fundingRate"]),
                timestamp=datetime.utcfromtimestamp(data["fundingTime"] / 1000)
            )

    async def fetch_order_book(self, symbol: str) -> OrderBook:
        async with httpx.AsyncClient() as client:
            r = await client.get(self.order_book_url, params={"symbol": symbol, "limit": 5})
            r.raise_for_status()
            data = r.json()
            return OrderBook(
                symbol=symbol,
                bids=[(float(price), float(qty)) for price, qty in data["bids"]],
                asks=[(float(price), float(qty)) for price, qty in data["asks"]],
                timestamp=datetime.utcnow()
            )
        

    async def fetch_fees(self, symbol: str) -> Fees:
        return Fees(maker=DEFAULT_MAKER_FEE, taker=DEFAULT_TAKER_FEE)
        # async with httpx.AsyncClient() as client:
        #     r = await client.get(self.url)
        #     r.raise_for_status()
        #     data = r.json()
        #     for sym in data.get("symbols", []):
        #         if sym["symbol"] == symbol:
        #             # You could extend this to parse more filters later
        #             return Fees(maker=DEFAULT_MAKER_FEE, taker=DEFAULT_TAKER_FEE)

        # return None  # Symbol not found
        

    # async def fetch_fees(self, symbol: str) -> Fees:from dataclasses import dataclass


    # async def fetch_fees(self, symbol: str) -> Fees:
    #     url = f"{self.base_url}/fapi/v2/account"

    #     headers = {
    #         "X-MBX-APIKEY": self.api_key
    #     }

    #     async with httpx.AsyncClient() as client:
    #         response = await client.get(url, headers=headers)
    #         response.raise_for_status()
    #         data = response.json()

    #         maker = float(data.get("makerCommission", 0)) / 10000
    #         taker = float(data.get("takerCommission", 0)) / 10000

    #         return Fees(maker=maker, taker=taker)