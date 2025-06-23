from app.trade.entities.signal import Signal
class RiskChecker:
    def __init__(self, max_trade_size: float = 50.0):
        self.max_trade_size = max_trade_size

    def allow(self, signal: Signal) -> bool:
        # Add cooldown, open position, exposure, etc.
        return signal.confidence >= 0.8