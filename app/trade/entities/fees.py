from dataclasses import dataclass


@dataclass
class Fees:
    maker: float
    taker: float