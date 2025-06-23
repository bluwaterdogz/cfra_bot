from app.trade.entities.signal import Signal, SignalAction


class TradeExecutor:
    def __init__(self, exchange_client, test_mode: bool = True):
        self.exchange = exchange_client
        self.test_mode = test_mode

    async def execute(self, signal: Signal):
        if signal.signal_action not in [SignalAction.BUY, SignalAction.SELL]:
            return

        if self.test_mode:
            print(f"[TEST] Would execute: {signal}")
        else:
            await self.exchange.place_order(signal)