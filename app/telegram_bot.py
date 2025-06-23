import asyncio
import logging
import os
from typing import Optional, List
from datetime import datetime
import telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from app.bot_controller import BotController
from app.handlers.telegram_notifier import TelegramNotifier

logger = logging.getLogger(__name__)

class TelegramBot:
    """Telegram bot for controlling and monitoring the scraping bot."""
    
    def __init__(self, 
                 bot_token: str,
                 allowed_user_id: int,
                 bot_controller: BotController,
                 notifier: TelegramNotifier):
        self.bot_token = bot_token
        self.allowed_user_id = allowed_user_id
        self.bot_controller = bot_controller
        self.notifier = notifier
        self.application: Optional[Application] = None
        self.is_running = False
        
    async def start(self):
        """Start the Telegram bot."""
        if self.is_running:
            logger.warning("Telegram bot is already running")
            return
            
        logger.info("🤖 Starting Telegram bot...")
        
        # Create application
        self.application = Application.builder().token(self.bot_token).build()
        
        # Add command handlers
        self.application.add_handler(CommandHandler("start", self._start_command))
        self.application.add_handler(CommandHandler("status", self._status_command))
        self.application.add_handler(CommandHandler("pause", self._pause_command))
        self.application.add_handler(CommandHandler("resume", self._resume_command))
        self.application.add_handler(CommandHandler("log", self._log_command))
        self.application.add_handler(CommandHandler("help", self._help_command))
        
        # Start polling
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        self.is_running = True
        logger.info("✅ Telegram bot started successfully")
        
        # Send startup notification
        await self.notifier.send_message("🚀 Bot system started and ready for commands!")
    
    async def stop(self):
        """Stop the Telegram bot."""
        if not self.is_running:
            logger.warning("Telegram bot is not running")
            return
            
        logger.info("🛑 Stopping Telegram bot...")
        
        if self.application:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
        
        self.is_running = False
        logger.info("✅ Telegram bot stopped")
    
    async def _check_auth(self, update: Update) -> bool:
        """Check if the user is authorized to use the bot."""
        user_id = update.effective_user.id
        if user_id != self.allowed_user_id:
            logger.warning(f"Unauthorized access attempt from user {user_id}")
            await update.message.reply_text("❌ You are not authorized to use this bot.")
            return False
        return True
    
    async def _start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        if not await self._check_auth(update):
            return
            
        welcome_message = """
🤖 *Bot Control System*

Welcome! I'm your bot controller. Here are the available commands:

/status - Check bot status
/pause - Pause bot operations  
/resume - Resume bot operations
/log - Get recent logs
/help - Show this help message

The bot is currently *running* and monitoring for data.
        """
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def _status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command."""
        if not await self._check_auth(update):
            return
            
        status = self.bot_controller.get_status()
        state = self.bot_controller.state.get_summary()
        
        status_message = f"""
📊 *Bot Status*

🔄 **Running**: {'✅ Yes' if status['is_running'] else '❌ No'}
⏸️ **Paused**: {'✅ Yes' if status['is_paused'] else '❌ No'}
⏱️ **Uptime**: {state['uptime']}
🕐 **Last Cycle**: {state['last_cycle']}
⏱️ **Cycle Duration**: {state['cycle_duration']}
❌ **Errors**: {state['errors']}
🔄 **Poll Interval**: {status['poll_interval']}s
        """
        
        await update.message.reply_text(status_message, parse_mode='Markdown')
    
    async def _pause_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /pause command."""
        if not await self._check_auth(update):
            return
            
        await self.bot_controller.pause()
        await update.message.reply_text("⏸️ Bot operations paused successfully!")
    
    async def _resume_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /resume command."""
        if not await self._check_auth(update):
            return
            
        await self.bot_controller.resume()
        await update.message.reply_text("▶️ Bot operations resumed successfully!")
    
    async def _log_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /log command."""
        if not await self._check_auth(update):
            return
            
        try:
            # Get the last N lines from the log file
            lines = 10  # Default to last 10 lines
            if context.args:
                try:
                    lines = int(context.args[0])
                    lines = min(lines, 50)  # Cap at 50 lines
                except ValueError:
                    await update.message.reply_text("❌ Please provide a valid number of lines (1-50)")
                    return
            
            log_file = "/app/logs/bot.log"
            if not os.path.exists(log_file):
                await update.message.reply_text("📝 No log file found.")
                return
            
            with open(log_file, 'r') as f:
                all_lines = f.readlines()
                last_lines = all_lines[-lines:] if len(all_lines) >= lines else all_lines
            
            if last_lines:
                log_content = ''.join(last_lines)
                # Split into chunks if too long (Telegram has message limits)
                if len(log_content) > 4000:
                    chunks = [log_content[i:i+4000] for i in range(0, len(log_content), 4000)]
                    for i, chunk in enumerate(chunks):
                        await update.message.reply_text(f"📝 Log chunk {i+1}/{len(chunks)}:\n```\n{chunk}\n```", parse_mode='Markdown')
                else:
                    await update.message.reply_text(f"📝 Last {len(last_lines)} log lines:\n```\n{log_content}\n```", parse_mode='Markdown')
            else:
                await update.message.reply_text("📝 No log entries found.")
                
        except Exception as e:
            logger.error(f"Error reading logs: {e}")
            await update.message.reply_text(f"❌ Error reading logs: {e}")
    
    async def _help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        if not await self._check_auth(update):
            return
            
        help_message = """
🤖 *Bot Control Commands*

/start - Start the bot and show welcome message
/status - Check current bot status and statistics
/pause - Pause bot operations (stops scraping cycles)
/resume - Resume bot operations
/log [N] - Get last N log lines (default: 10, max: 50)
/help - Show this help message

*Examples:*
• `/log` - Get last 10 log lines
• `/log 20` - Get last 20 log lines
        """
        
        await update.message.reply_text(help_message, parse_mode='Markdown') 