
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from app.trade.entities.order_book import OrderBook
from app.trade.entities.funding_rate import FundingRate
from app.trade.entities.fees import Fees

class ExchangeClient(ABC):
    @abstractmethod
    async def fetch_funding_rate(self, symbol: str) -> FundingRate:
        """
        Fetch the latest funding rate and relevant metadata for a given symbol.
        Should return a dict like:
        {
            "symbol": str,
            "funding_rate": float,
            "timestamp": datetime,
            ...
        }
        """
        pass

    @abstractmethod
    async def fetch_order_book(self, symbol: str) -> OrderBook:
        """
        Fetch bid/ask depth for slippage estimation.
        Should return:
        {
            "symbol": str,
            "bids": List[Tuple[price, quantity]],
            "asks": List[Tuple[price, quantity]],
            ...
        }
        """
        pass

    @abstractmethod
    async def fetch_fees(self, symbol: str) -> Fees:
        """
        Fetch the fees for a given symbol.
        Should return:
        {
            "taker": float,
            "maker": float,
        }
        """
        pass

    @property
    def symbol_map(self) -> Optional[Dict[str, str]]:
        return None