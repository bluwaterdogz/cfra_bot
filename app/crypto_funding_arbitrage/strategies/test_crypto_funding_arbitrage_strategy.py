import pytest
from datetime import datetime, timezone

# Import the strategy to be tested and the signal action enum
from app.crypto_funding_arbitrage.strategies.crypto_funding_arbitrage_strategy import CryptoFundingArbitrageStrategy
from app.trade.entities.signal import SignalAction
from app.crypto_funding_arbitrage.entities.crypto_funding_arbitrage_data import CryptoFundingArbitrageData
from app.trade.entities.fees import Fees
from app.trade.entities.order_book import OrderBook
from app.trade.entities.funding_rate import FundingRate

# -------------------------------
# ✅ Test 1: Profitable scenario
# Funding rate is high enough and costs are low
# -------------------------------

@pytest.mark.asyncio
async def test_profitable_scenario():
    strategy = CryptoFundingArbitrageStrategy(threshold=0.0005, max_hours_to_wait=8)

    symbol = "BTCUSDT"
    timestamp = datetime.now(timezone.utc).replace(hour=0, minute=1)
    market_data = CryptoFundingArbitrageData(
        funding_rate=FundingRate(symbol=symbol, funding_rate=0.0012, timestamp=timestamp),  # High enough to be profitable
        fees=Fees(maker=0.0002, taker=0.0003),  # Reasonable fee
        order_book=OrderBook(symbol=symbol, bids=[], asks=[], timestamp=timestamp), # Near funding payout
    )

    result = await strategy.evaluate(market_data)

    # It should be marked profitable
    assert result["is_profitable"]
    assert result["net_return"] > 0
    assert result["breakeven_hours"] < strategy.hold_time_hours

    # A trade signal should be generated
    signal = await strategy.generate_signal(market_data)
    assert signal is not None
    assert signal.signal_action == SignalAction.BUY

# -------------------------------
# ❌ Test 2: Not profitable due to low funding rate
# Funding rate is below threshold
# -------------------------------

@pytest.mark.asyncio
async def test_not_profitable_due_to_low_funding():
    strategy = CryptoFundingArbitrageStrategy(threshold=0.0005)
    timestamp = datetime.now(timezone.utc).replace(hour=1, minute=0)
    symbol = "ETHUSDT"
    market_data = CryptoFundingArbitrageData(
        funding_rate=FundingRate(symbol="ETHUSDT", funding_rate=0.0001, timestamp=timestamp),  # Below threshold
        fees=Fees(maker=0.0002, taker=0.0003),
        order_book=OrderBook(symbol=symbol, bids=[], asks=[], timestamp=timestamp),
    )

    result = await strategy.evaluate(market_data)

    # Should not be considered profitable
    assert not result["is_profitable"]

    # No trade signal should be returned
    signal = await strategy.generate_signal(market_data)
    assert signal is None

# -------------------------------
# ⏰ Test 3: Not profitable due to delay
# Funding payout is too far away to be worth it
# -------------------------------

@pytest.mark.asyncio
async def test_not_profitable_due_to_funding_delay():
    strategy = CryptoFundingArbitrageStrategy(
        threshold=0.0005,
        max_hours_to_wait=2  # Strategy only considers opportunities with payout ≤ 2h away
    )

    timestamp = datetime.now(timezone.utc).replace(hour=1, minute=0)
    symbol = "XRPUSDT"
    market_data = CryptoFundingArbitrageData(
        funding_rate=FundingRate(symbol=symbol, funding_rate=0.002, timestamp=timestamp),  # High funding rate
        fees=Fees(maker=0.0002, taker=0.0003),
        order_book=OrderBook(symbol=symbol, bids=[], asks=[], timestamp=timestamp),
    )

    result = await strategy.evaluate(market_data)

    # Profitability is there, but funding is too far away
    assert result["net_return"] > 0
    assert result["funding_rate"] > strategy.threshold
    assert result["time_to_funding_hours"] > strategy.max_hours_to_wait
    assert not result["is_profitable"]

    # So no signal should be generated
    signal = await strategy.generate_signal(market_data)
    assert signal is None