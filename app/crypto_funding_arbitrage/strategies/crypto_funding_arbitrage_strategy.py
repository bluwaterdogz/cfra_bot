from typing import Optional

from app.trade.entities.signal import Signal, SignalAction
from app.trade.entities.strategy import Strategy
from app.trade.entities.order_book import OrderBook
from app.crypto_funding_arbitrage.utility.format_duration import format_duration
from app.crypto_funding_arbitrage.utility.time_to_next_funding_cycle import time_to_next_funding_cycle
from app.crypto_funding_arbitrage.strategies.config import (
    DEFAULT_TAKER_FEE,
    DEFAULT_SLIPPAGE,
    DEFAULT_THRESHOLD,
    DEFAULT_HOLD_TIME_HOURS,
    DEFAULT_MAX_HOURS_TO_WAIT,
    DEFAULT_ORDER_SIZE_USD,
    DEFAULT_SLIPPAGE
)
from app.crypto_funding_arbitrage.entities.crypto_funding_arbitrage_data import CryptoFundingArbitrageData

class CryptoFundingArbitrageStrategy(Strategy):
    
    def __init__(
        self,
        threshold: float = DEFAULT_THRESHOLD,
        hold_time_hours: int = DEFAULT_HOLD_TIME_HOURS,
        max_hours_to_wait: int = DEFAULT_MAX_HOURS_TO_WAIT
    ):
        """
        :param threshold: Minimum funding rate to consider an opportunity.
        :param hold_time_hours: Duration needed to qualify for funding.
        :param max_hours_to_wait: Max time until next funding event to still consider entering.
        """
        self.threshold = threshold
        self.hold_time_hours = hold_time_hours
        self.max_hours_to_wait = max_hours_to_wait


    def name(self) -> str:
        return "CryptoFundingArbitrageStrategy"

    async def evaluate(self, market_data: CryptoFundingArbitrageData) -> dict:
        funding_rate = market_data.funding_rate.funding_rate
        fees = market_data.fees

        taker_fee = fees.taker
        if taker_fee is None:
            taker_fee = DEFAULT_TAKER_FEE
            raise ValueError(f"Taker fee is None for {market_data.funding_rate.symbol}")

        slippage = self._calculate_slippage(market_data.order_book)
        gross_return = self._calculate_gross_return(funding_rate)
        estimated_cost = self._calculate_estimated_cost(taker_fee, slippage)
        net_return = self._calculate_net_return(gross_return, estimated_cost)
        breakeven_hours = self._calculate_breakeven_hours(
            net_return, estimated_cost, gross_return
        )
        wait_hours = self._calculate_time_to_next_funding_hours(market_data)
        return {
            "symbol": market_data.funding_rate.symbol,
            "funding_rate": funding_rate,
            "taker_fee": taker_fee,
            "slippage": slippage,
            "net_return": net_return,
            "breakeven_hours": breakeven_hours,
            "breakeven_human": format_duration(breakeven_hours),
            "time_to_funding_hours": wait_hours,
            "is_profitable": (
                net_return > 0 and
                funding_rate > self.threshold and
                wait_hours <= self.max_hours_to_wait
            )
        }

    async def generate_signal(self, market_data: CryptoFundingArbitrageData) -> Optional[Signal]:
        eval_result = await self.evaluate(market_data)

        if eval_result["is_profitable"]:
            return Signal(
                symbol=eval_result["symbol"],
                signal_action=SignalAction.BUY,
                confidence=round(eval_result["net_return"], 6),
                metadata=eval_result
            )
        return Signal(
                symbol=eval_result["symbol"],
                action=SignalAction.NONE,
                confidence=0,
                metadata={}
            )


    # --- Internal calculation methods ---

    def _calculate_gross_return(self, funding_rate: float) -> float:
        return max(funding_rate, 0.0)  # Prevent negative return

    def _calculate_estimated_cost(self, taker_fee: float, slippage: float) -> float:
        return 2 * max(taker_fee + slippage, 0.0)  # Prevent negative costs

    def _calculate_net_return(self, gross_return: float, estimated_cost: float) -> float:
        return gross_return - estimated_cost

    def _calculate_breakeven_hours(self, net_return: float, estimated_cost: float, funding_rate: float) -> float:
        if funding_rate <= 0:
            return float("inf")
        funding_per_hour = funding_rate / self.hold_time_hours
        return estimated_cost / funding_per_hour

    def _calculate_time_to_next_funding_hours(self, market_data: CryptoFundingArbitrageData) -> float:
        funding_time = market_data.funding_rate.timestamp
        wait_delta = time_to_next_funding_cycle(funding_time)
        return wait_delta.total_seconds() / 3600
    
    def _calculate_slippage(self, order_book: OrderBook, order_size_usd: float = DEFAULT_ORDER_SIZE_USD) -> float:
        """
        Estimate slippage for a market buy order of a given USD size using the asks side of the order book.
        Slippage is defined as the % difference between the average execution price and the best ask.
        """
        asks = order_book.asks
        if not asks:
            return DEFAULT_SLIPPAGE  # No liquidity? Use fallback.

        total_cost = 0.0
        remaining_usd = order_size_usd
        best_price = asks[0][0]

        for price, quantity in asks:
            level_value = price * quantity
            if level_value >= remaining_usd:
                total_cost += price * (remaining_usd / price)
                remaining_usd = 0
                break
            else:
                total_cost += level_value
                remaining_usd -= level_value

        if remaining_usd > 0:  # Order size too large for book depth
            return DEFAULT_SLIPPAGE

        avg_price = total_cost / order_size_usd
        slippage = (avg_price - best_price) / best_price
        return  max(0.0, slippage)
