from app.trade.exchanges.kraken_client import KrakenClient
from app.trade.exchanges.binance_client import BinanceClient
from app.trade.exchanges.deribit_client import DeribitClient
from app.trade.exchanges.bybit_client import BybitClient
from app.trade.exchanges.okx_client import OKXClient

def get_exchange_by_name(name: str):
    if name == "kraken":
        return KrakenClient()
    elif name == "binance":
        return BinanceClient()
    elif name == "deribit":
        return DeribitClient()
    elif name == "bybit":
        return BybitClient()
    elif name == "okx":
        return OKXClient()
    else:
        raise ValueError(f"Unknown exchange: {name}")