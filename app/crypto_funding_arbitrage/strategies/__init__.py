from app.crypto_funding_arbitrage.strategies.crypto_funding_arbitrage_strategy import CryptoFundingArbitrageStrategy

def get_strategy_by_name(name: str, exchange):
    if name == "cfrashort":
        return CryptoFundingArbitrageStrategy(exchange)
    else:
        raise ValueError(f"Unknown strategy: {name}")