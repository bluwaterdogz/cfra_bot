from app.trade.entities.strategy import Strategy
from app.trade.entities.signal import Signal, SignalAction


class MovingAverageStrategy(Strategy):
    def __init__(self, short_window: int = 5, long_window: int = 20):
        self.short_window = short_window
        self.long_window = long_window

    async def generate_signal(self, market_data: dict):
        candles = market_data.get("candles", [])
        closes = [c["close"] for c in candles]

        if len(closes) < self.long_window:
            return None

        short_ma = sum(closes[-self.short_window:]) / self.short_window
        long_ma = sum(closes[-self.long_window:]) / self.long_window

        if short_ma > long_ma:
            return Signal(SignalAction.BUY, confidence=0.9)
        elif short_ma < long_ma:
            return Signal(SignalAction.SELL, confidence=0.9)
        else:
            return Signal(SignalAction.HOLD, confidence=0.5)

    async def evaluate(self, market_data: dict):
        candles = market_data.get("candles", [])
        closes = [c["close"] for c in candles]

        if len(closes) < self.long_window:
            return None

        short_ma = sum(closes[-self.short_window:]) / self.short_window
        long_ma = sum(closes[-self.long_window:]) / self.long_window

        return {
            "short_ma": short_ma,
            "long_ma": long_ma,
        }

    def name(self):
        return "MovingAverage"