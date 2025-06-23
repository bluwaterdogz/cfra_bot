from app.handlers.handler_interface import Handler
from typing import Dict, Any, List
import json
import re
from datetime import datetime

class EmailHandler(Handler):
    """Handler for sending email notifications."""
    
    def __init__(self, smtp_server: str = "localhost", smtp_port: int = 587):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
    
    async def handle(self, data: Dict[str, Any]):
        """Send email notification (placeholder implementation)."""
        print(f"📧 Email notification would be sent to configured recipients")
        print(f"   Subject: Scraper Alert - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Content: {json.dumps(data, indent=2)[:200]}...")

class SMSHandler(Handler):
    """Handler for sending SMS notifications."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
    
    async def handle(self, data: Dict[str, Any]):
        """Send SMS notification (placeholder implementation)."""
        print(f"📱 SMS notification would be sent to configured recipients")
        print(f"   Message: Scraper Alert - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

class WebhookHandler(Handler):
    """Handler for sending webhook notifications."""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    async def handle(self, data: Dict[str, Any]):
        """Send webhook notification (placeholder implementation)."""
        print(f"🔗 Webhook notification would be sent to: {self.webhook_url}")
        print(f"   Payload: {json.dumps(data, indent=2)[:200]}...")

class NotificationRouter:
    """Routes notifications based on subscription configuration."""
    
    def __init__(self, subscriptions_file: str = "subscriptions.json"):
        self.subscriptions_file = subscriptions_file
        self.handlers = {}
    
    def register_handler(self, notification_type: str, handler: Handler):
        """Register a handler for a specific notification type."""
        self.handlers[notification_type] = handler
    
    def _load_subscriptions(self) -> List[Dict[str, Any]]:
        """Load subscriptions from JSON file."""
        try:
            with open(self.subscriptions_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  No subscriptions file found at {self.subscriptions_file}")
            return []
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing subscriptions file: {e}")
            return []
    
    def _check_keyword_match(self, data: Dict[str, Any], keyword: str) -> bool:
        """Check if keyword matches any text in the data."""
        data_str = json.dumps(data).lower()
        return keyword.lower() in data_str
    
    async def route_notifications(self, data: Dict[str, Any]):
        """Route notifications based on subscriptions and data content."""
        subscriptions = self._load_subscriptions()
        
        for subscription in subscriptions:
            if self._should_trigger(subscription, data):
                await self._send_notifications(subscription, data)
    
    def _should_trigger(self, subscription: Dict[str, Any], data: Dict[str, Any]) -> bool:
        """Check if a subscription should trigger based on the data."""
        sub_type = subscription.get("type")
        
        if sub_type == "keyword_match":
            keyword = subscription.get("keyword")
            return self._check_keyword_match(data, keyword)
        
        return False
    
    async def _send_notifications(self, subscription: Dict[str, Any], data: Dict[str, Any]):
        """Send notifications for a triggered subscription."""
        notify_list = subscription.get("notify", [])
        
        for notification in notify_list:
            if ":" in notification:
                notification_type, target = notification.split(":", 1)
                
                if notification_type in self.handlers:
                    handler = self.handlers[notification_type]
                    await handler.handle(data)
                else:
                    print(f"⚠️  No handler registered for notification type: {notification_type}")
            else:
                print(f"⚠️  Invalid notification format: {notification}")

# Factory functions for easy handler creation
def create_email_handler(smtp_server: str = "localhost", smtp_port: int = 587) -> EmailHandler:
    return EmailHandler(smtp_server, smtp_port)

def create_sms_handler(api_key: str = None) -> SMSHandler:
    return SMSHandler(api_key)

def create_webhook_handler(webhook_url: str) -> WebhookHandler:
    return WebhookHandler(webhook_url) 