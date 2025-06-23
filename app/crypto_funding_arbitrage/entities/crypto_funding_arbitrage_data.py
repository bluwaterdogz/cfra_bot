from dataclasses import dataclass
from app.trade.entities.funding_rate import FundingRate
from app.trade.entities.order_book import OrderBook
from app.trade.entities.fees import Fees

@dataclass
class CryptoFundingArbitrageData:
    funding_rate: FundingRate
    order_book: OrderBook
    fees: Fees