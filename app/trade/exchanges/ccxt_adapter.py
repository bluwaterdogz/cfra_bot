# import ccxt.async_support as ccxt

# class CcxtAdapter:
#     def __init__(self, api_key, secret, symbol="BTC/USDT"):
#         self.client = ccxt.binance({
#             "apiKey": api_key,
#             "secret": secret,
#             "enableRateLimit": True,
#         })
#         self.symbol = symbol

#     async def place_order(self, signal: Signal):
#         side = "buy" if signal.signal_action == SignalAction.BUY else "sell"
#         await self.client.create_market_order(self.symbol, side, amount=0.01)