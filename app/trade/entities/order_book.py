from dataclasses import dataclass
from datetime import datetime

@dataclass
class OrderBook:
    symbol: str
    bids: list[tuple[float, float]]  # List of (price, quantity)
    asks: list[tuple[float, float]]
    timestamp: datetime