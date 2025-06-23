from app.trade.exchanges.exchange_client import ExchangeClient
from typing import List
from app.crypto_funding_arbitrage.entities.crypto_funding_arbitrage_data import CryptoFundingArbitrageData

class CryptoFundingArbitrageDataAggregator:
    def __init__(self, exchange_client: ExchangeClient, symbols: List[str]):
        self.exchange_client = exchange_client
        self.symbols = symbols

    async def fetch_all(self) -> List[CryptoFundingArbitrageData]:  
        results = []
        for symbol in self.symbols:
            try:
                funding_rate = await self.exchange_client.fetch_funding_rate(symbol)
                order_book = await self.exchange_client.fetch_order_book(symbol)
                fees = await self.exchange_client.fetch_fees(symbol)
                results.append(CryptoFundingArbitrageData(funding_rate, order_book, fees))
            except Exception as e:
                print(f"Error fetching {symbol}: {e}")
                continue  # skip appending
        return results