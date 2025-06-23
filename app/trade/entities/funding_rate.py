from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class FundingRate:
    symbol: str
    funding_rate: float
    timestamp: datetime