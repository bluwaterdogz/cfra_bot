# Modular Crypto/Scraping Bot System

A long-running, modular bot system built with Python and asyncio that can scrape data, process it, and send notifications via Telegram.

## Features

- 🔄 **Long-running**: Designed to run for months with proper restart policies
- 🧩 **Modular**: Interchangeable Scraper, Parser, and Handler components
- 🤖 **Telegram Integration**: Control and monitor via Telegram commands
- 📊 **Real-time Status**: Check bot status, logs, and statistics
- 📝 **Comprehensive Logging**: Rotating file logs with console output
- 🐳 **Docker Ready**: Full Docker and Docker Compose support
- ⚡ **Async Architecture**: Built with asyncio for high performance

## Quick Start

### 1. Set up Telegram Bot

1. Create a bot with @BotFather on Telegram
2. Get your user ID by messaging @userinfobot
3. Copy `env.example` to `.env` and fill in your credentials

### 2. Run with Docker Compose

```bash
# Build and start the bot
make bot-up

# View logs
make bot-logs

# Stop the bot
make bot-down
```

### 3. Control via Telegram

Use these commands in your Telegram bot:

- `/start` - Welcome message and help
- `/status` - Check bot status and statistics
- `/pause` - Pause bot operations
- `/resume` - Resume bot operations
- `/log [N]` - Get last N log lines
- `/help` - Show all available commands

## Development

```bash
# Install dependencies
make dev-install

# Run locally
make dev-run
```

## Configuration

Required environment variables in `.env`:

- `TELEGRAM_BOT_TOKEN` - Your Telegram bot token
- `TELEGRAM_USER_ID` - Your Telegram user ID
- `POLL_INTERVAL` - Scraping cycle interval (seconds, default: 60)
# cfra_bot
