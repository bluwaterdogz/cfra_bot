import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime
import telegram
from app.handlers.handler_interface import Handler

logger = logging.getLogger(__name__)

class TelegramNotifier(Handler):
    """Handler for sending Telegram notifications."""
    
    def __init__(self, bot_token: str, chat_id: int):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.bot: Optional[telegram.Bot] = None
        
    async def handle(self, data: Dict[str, Any]):
        """Send notification via Telegram."""
        try:
            if not self.bot:
                self.bot = telegram.Bot(token=self.bot_token)
            
            # Create notification message
            message = self._format_notification(data)
            
            # Send message
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='Markdown'
            )
            
            logger.info("✅ Telegram notification sent successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to send Telegram notification: {e}")
    
    async def send_message(self, message: str):
        """Send a custom message via Telegram."""
        try:
            if not self.bot:
                self.bot = telegram.Bot(token=self.bot_token)
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='Markdown'
            )
            
            logger.info("✅ Custom Telegram message sent successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to send custom Telegram message: {e}")
    
    def _format_notification(self, data: Dict[str, Any]) -> str:
        """Format data into a readable Telegram message."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Extract key information from data
        if isinstance(data, dict):
            # Try to get meaningful content
            content = data.get('sample_data', data.get('content', str(data)))
            
            # Truncate content if too long
            if isinstance(content, str) and len(content) > 500:
                content = content[:500] + "..."
            elif isinstance(content, dict):
                content = json.dumps(content, indent=2)[:500] + "..."
            
            message = f"""
🔔 *Bot Notification*

⏰ **Time**: {timestamp}
📊 **Data Type**: {type(data).__name__}

📝 **Content**:
```
{content}
```
            """
        else:
            message = f"""
🔔 *Bot Notification*

⏰ **Time**: {timestamp}
📊 **Data Type**: {type(data).__name__}

📝 **Content**:
```
{str(data)[:500]}...
```
            """
        
        return message.strip() 