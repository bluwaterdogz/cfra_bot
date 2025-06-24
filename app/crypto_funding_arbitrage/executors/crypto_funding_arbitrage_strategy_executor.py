from typing import Callable
from app.trade.entities.strategy import Strategy
from app.trade.entities.signal import SignalAction
from app.crypto_funding_arbitrage.entities.crypto_funding_arbitrage_data import CryptoFundingArbitrageData
import json
class CryptoFundingArbitrageStrategyExecutor:
    def __init__(self, strategy: Strategy):
        self.strategy = strategy

    async def run(self, 
            market_data_list: list[CryptoFundingArbitrageData], 
            handle_signals: Callable[[str], None] = None
        ):
        signals = []
        for market_data in market_data_list:
            # if market_data.error:
            #     print(f" Error fetching {market_data.funding_rate.symbol}: {market_data.error}")
            #     continue

            evaluation = await self.strategy.evaluate(market_data)
            # print(f" Evaluation for {market_data.funding_rate.symbol}:")
            print(json.dumps(evaluation, indent=2, default=str))
            signal = await self.strategy.generate_signal(market_data)
            if signal.action != SignalAction.NONE:
                print(f" Trade Signal: {signal.action} {signal.symbol} (Confidence: {signal.confidence})")
            else:
                print(f" No trade signal for {market_data.funding_rate.symbol}")
            signals.append(signal)

        if handle_signals:
            response = [
                f"Signal: {signal.action} {signal.symbol} (Confidence: {signal.confidence})" if signal.action != SignalAction.NONE else f"No signal for `{signal.symbol}`"
                for signal in signals
            ]
            handle_signals("\n".join(response))