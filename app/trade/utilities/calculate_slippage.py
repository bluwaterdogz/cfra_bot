
from typing import List

def calculate_slippage(order_book: List[List[str]], trade_size: float, side: str = "buy") -> float:
    """
    Estimate slippage based on order book and trade size.
    
    Parameters:
        order_book: List of [price, quantity] pairs (asks for buy, bids for sell).
        trade_size: How much of the asset you want to buy or sell.
        side: 'buy' means you eat asks, 'sell' means you eat bids.
    
    Returns:
        Estimated slippage as a percentage (e.g., 0.001 means 0.1%)
    """
    if not order_book:
        return 0.0  # or raise an error

    remaining = trade_size
    total_cost = 0.0
    weighted_qty = 0.0

    for price_str, qty_str in order_book:
        price = float(price_str)
        qty = float(qty_str)

        if remaining <= qty:
            total_cost += remaining * price
            weighted_qty += remaining
            break
        else:
            total_cost += qty * price
            weighted_qty += qty
            remaining -= qty

    if weighted_qty == 0:
        return 0.0

    avg_execution_price = total_cost / weighted_qty
    top_price = float(order_book[0][0])

    # For 'buy', slippage is how much above top ask you paid
    # For 'sell', slippage is how much below top bid you got
    if side == "buy":
        slippage = (avg_execution_price - top_price) / top_price
    else:
        slippage = (top_price - avg_execution_price) / top_price

    return slippage