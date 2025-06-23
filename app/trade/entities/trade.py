from enum import Enum
from datetime import datetime


class TradeSide(Enum):
    BUY = "buy"
    SELL = "sell"


class Trade:
    def __init__(self, side: TradeSide, price: float, size: float, time: datetime = None):
        self.side = side
        self.price = price
        self.size = size
        self.time = time or datetime.utcnow()