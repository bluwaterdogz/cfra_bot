import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.scrapers.scraper_interface import Scraper
from app.parsers.parser_interface import Parser
from app.handlers.handler_interface import Handler
from app.state import BotState

logger = logging.getLogger(__name__)

class BotController:
    """Manages the lifecycle and execution of the scraping bot."""
    
    def __init__(self, 
                 scraper: Scraper,
                 parser: Parser,
                 handlers: List[Handler],
                 state: BotState,
                 poll_interval: int = 60):
        self.scraper = scraper
        self.parser = parser
        self.handlers = handlers
        self.state = state
        self.poll_interval = poll_interval
        self.is_running = False
        self.task: Optional[asyncio.Task] = None
        
    async def start(self):
        """Start the bot controller."""
        if self.is_running:
            logger.warning("Bot is already running")
            return
            
        logger.info("🚀 Starting bot controller...")
        self.is_running = True
        self.state.set_running(True)
        
        # Start the main loop
        self.task = asyncio.create_task(self._main_loop())
        logger.info("✅ Bot controller started successfully")
    
    async def stop(self):
        """Stop the bot controller."""
        if not self.is_running:
            logger.warning("Bot is not running")
            return
            
        logger.info("🛑 Stopping bot controller...")
        self.is_running = False
        self.state.set_running(False)
        
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        
        logger.info("✅ Bot controller stopped")
    
    async def pause(self):
        """Pause the bot operations."""
        logger.info("⏸️  Pausing bot operations...")
        self.state.set_paused(True)
        logger.info("✅ Bot operations paused")
    
    async def resume(self):
        """Resume the bot operations."""
        logger.info("▶️  Resuming bot operations...")
        self.state.set_paused(False)
        logger.info("✅ Bot operations resumed")
    
    async def _main_loop(self):
        """Main execution loop for the bot."""
        logger.info(f"🔄 Starting main loop with {self.poll_interval}s intervals")
        
        while self.is_running:
            try:
                if not self.state.is_paused:
                    await self._execute_cycle()
                else:
                    logger.debug("Bot is paused, skipping cycle")
                
                # Wait for next cycle
                await asyncio.sleep(self.poll_interval)
                
            except asyncio.CancelledError:
                logger.info("Main loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                # Continue running despite errors
                await asyncio.sleep(self.poll_interval)
    
    async def _execute_cycle(self):
        """Execute one complete scraping cycle."""
        cycle_start = datetime.now()
        logger.info("🔄 Starting scraping cycle...")
        
        try:
            # Step 1: Fetch raw data
            logger.debug("📡 Fetching data...")
            raw_data = await self.scraper.fetch()
            logger.debug(f"✅ Fetched {len(str(raw_data))} characters of raw data")
            
            # Step 2: Parse data
            logger.debug("🔍 Parsing data...")
            parsed_data = await self.parser.parse(raw_data)
            logger.debug("✅ Data parsed successfully")
            
            # Step 3: Process with handlers
            logger.debug("💾 Processing with handlers...")
            for handler in self.handlers:
                await handler.handle(parsed_data)
            
            # Update state
            cycle_duration = (datetime.now() - cycle_start).total_seconds()
            self.state.update_last_cycle(cycle_start, cycle_duration)
            
            logger.info(f"✅ Cycle completed in {cycle_duration:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ Error in scraping cycle: {e}", exc_info=True)
            self.state.increment_error_count()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current bot status."""
        return {
            "is_running": self.is_running,
            "is_paused": self.state.is_paused,
            "last_cycle": self.state.last_cycle_time,
            "cycle_duration": self.state.last_cycle_duration,
            "error_count": self.state.error_count,
            "poll_interval": self.poll_interval
        } 