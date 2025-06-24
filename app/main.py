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
import argparse

DEFAULT_EXCHANGE = "binance"
DEFAULT_STRATEGY = "cfrashort"
MAX_THREADS = 10

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

def parse_telegram_command(message):
    parts = message.text.strip().split()
    command = parts[0]
    exchange = DEFAULT_EXCHANGE
    strategy = DEFAULT_STRATEGY
    print(f"[DEBUG] Parts: {parts}")
    if len(parts) == 2:
        strategy = parts[1]
    elif len(parts) == 3:
        exchange = parts[1]
        strategy = parts[2]
    elif len(parts) > 3:
        bot.reply_to(message, "Usage: /run [<exchange>] <strategy>")
        return None, None, None

    return command, exchange, strategy

# --- Telegram handler ---
@bot.message_handler(commands=["run"])
def handle_telegram_command(message):
    try:
        _, exchange, strategy = parse_telegram_command(message)

        # Run in new event loop inside thread
        def run_in_thread():        
            asyncio.run(
                run_async_strategy(
                    exchange_name=exchange, 
                    strategy_name=strategy, 
                    handle_signals=lambda reply_message: bot.reply_to(message, reply_message)
                )
            )
        if threading.active_count() < MAX_THREADS:
            threading.Thread(target=run_in_thread).start()
            bot.reply_to(message, f"Running `{strategy}` on `{exchange}`...")
        else:
            print(f"[DEBUG] Too many threads: {threading.active_count()}")

    except Exception as e:
        print(f"[DEBUG] Error: {e}")
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=["help"])
def handle_telegram_help(message):
    bot.reply_to(message, "Usage: /run <exchange> <strategy>, \nExchanges: " + ", ".join(EXCHANGES) + ", \nStrategies: " + ", ".join(STRATEGIES))


def get_args():
    parser = argparse.ArgumentParser(description="Run crypto strategy on selected exchange.")
    parser.add_argument(
        "--listen", "-l",
        dest="listen",
        action="store_true",
        help="Enable Telegram bot listening (default: False)"
    )
    parser.add_argument(
        "--exchange", "-ex",
        type=str,
        choices=EXCHANGES,
        default=DEFAULT_EXCHANGE,
        help="Exchange to use (default: binance)"
    )
    parser.add_argument(
        "--strategy", "-strat",
        type=str,
        choices=STRATEGIES,
        default=DEFAULT_STRATEGY,
        help="Trading strategy to run (default: cfrashort)"
    )
    args = parser.parse_args()
    return args

async def main():
    args = get_args()

    if args.listen:
        print("\n[Telegram bot is now listening...]\n")
        bot.infinity_polling()
    else:
        print(f"Running strategy: {args.strategy}")
        print(f"Using exchange: {args.exchange}")
        await run_async_strategy(
            args.exchange, 
            args.strategy, 
            lambda reply_message: print(reply_message)
        )


# --- Main entrypoint ---
if __name__ == "__main__":
    asyncio.run(main())     # run the main function
