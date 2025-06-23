
from abc import ABC, abstractmethod
from typing import Optional, Any, Dict
from app.trade.entities.signal import Signal


class Strategy(ABC):
    @abstractmethod
    async def generate_signal(self, market_data: dict) -> Signal:
        """
        Analyze market data and return a Signal (e.g., BUY, SELL, HOLD).
        """
        pass

    @abstractmethod
    def name(self) -> str:
        """
        Return the name of the strategy (for logging or metrics).
        """
        pass

    @abstractmethod
    async def evaluate(self, market_data: dict) -> Dict[str, Any]:
        """
        Return a structured evaluation of the opportunity (without making a decision).
        """
        pass