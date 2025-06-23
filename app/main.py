# run.py
import os
import asyncio
import threading
from dotenv import load_dotenv
from telebot import TeleBot
from typing import Callable
from app.trade.entities.signal import Signal
from app.crypto_funding_arbitrage.strategies import get_strategy_by_name
from app.trade.exchanges import get_exchange_by_name
from app.crypto_funding_arbitrage.executors.crypto_funding_arbitrage_strategy_executor import CryptoFundingArbitrageStrategyExecutor
from app.crypto_funding_arbitrage.aggregator.crypto_funding_arbitrage_data_aggregator import CryptoFundingArbitrageDataAggregator
from app.trade.symbols.kraken import KRAKEN_SYMBOLS
from app.trade.symbols.binance import BINANCE_SYMBOLS

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

EXCHANGES = ["kraken", "binance", "deribit", "bybit", "okx"]
STRATEGIES = ["cfrashort"]

bot = TeleBot(TELEGRAM_TOKEN)

# --- Async Strategy Runner ---
async def run_async_strategy(exchange_name: str, strategy_name: str, handle_signals: Callable[[str], None]):
    exchange_client = get_exchange_by_name(exchange_name)
    symbols = KRAKEN_SYMBOLS if exchange_name == "kraken" else BINANCE_SYMBOLS

    aggregator = CryptoFundingArbitrageDataAggregator(exchange_client, symbols)
    strategy = get_strategy_by_name(strategy_name, exchange_client)

    market_data_list = await aggregator.fetch_all()

    executor = CryptoFundingArbitrageStrategyExecutor(strategy)
    await executor.run(
        market_data_list, 
        handle_signals=handle_signals
    )


# --- CLI interaction ---
def select_cli_option():
    print("\nAvailable exchanges:", ", ".join(EXCHANGES))
    exchange_name = input("Choose exchange: ").strip()

    print("Available strategies:", ", ".join(STRATEGIES))
    strategy_name = input("Choose strategy: ").strip()

    return exchange_name, strategy_name


# --- Telegram handler ---
@bot.message_handler(commands=["run"])
def handle_telegram_command(message):
    try:
        parts = message.text.split()
        if len(parts) != 3:
            bot.reply_to(message, "Usage: /run <exchange> <strategy>")
            return

        _, exchange, strategy = parts

        # Run in new event loop inside thread
        def run_in_thread():        
            asyncio.run(
                run_async_strategy(
                    exchange_name=exchange, 
                    strategy_name=strategy, 
                    handle_signals=lambda reply_message: bot.reply_to(message, reply_message)
                )
            )

        threading.Thread(target=run_in_thread).start()
        bot.reply_to(message, f"Running `{strategy}` on `{exchange}`...")

    except Exception as e:
        bot.reply_to(message, f"Error: {e}")


# --- Main entrypoint ---
if __name__ == "__main__":
    # try:
    #     exchange_name, strategy_name = select_cli_option()
    #     asyncio.run(run_async_strategy(exchange_name, strategy_name))
    # except KeyboardInterrupt:
    #     print("Exiting interactive mode.")

    print("\n[Telegram bot is now listening...]\n")
    bot.infinity_polling()

async def main():
    exchange_client = get_exchange_by_name("kraken")
    
    aggregator = CryptoFundingArbitrageDataAggregator(exchange_client, KRAKEN_SYMBOLS)

    strategy = get_strategy_by_name("funding_rate_arbitrage", exchange_client)

    # 5. Fetch market data for all symbols
    market_data_list = await aggregator.fetch_all()

    # 6. Evaluate and optionally act on each symbol
    executor = CryptoFundingArbitrageStrategyExecutor(strategy)
    await executor.run(market_data_list)


