
from enum import Enum


class SignalAction(Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    NONE = "none"


class Signal:
    def __init__(self, symbol: str, action: SignalAction, confidence: float = 1.0, metadata: dict = None):
        self.symbol = symbol
        self.action = action
        self.confidence = confidence
        self.metadata = metadata or {}

    def __repr__(self):
        return f"<Signal {self.action.value} ({self.confidence:.2f})>"