from datetime import datetime
from typing import Optional

class BotState:
    """Manages the state and statistics of the bot."""
    
    def __init__(self):
        self._is_running = False
        self._is_paused = False
        self._last_cycle_time: Optional[datetime] = None
        self._last_cycle_duration: float = 0.0
        self._error_count = 0
        self._start_time: Optional[datetime] = None
    
    @property
    def is_running(self) -> bool:
        """Check if the bot is running."""
        return self._is_running
    
    @property
    def is_paused(self) -> bool:
        """Check if the bot is paused."""
        return self._is_paused
    
    @property
    def last_cycle_time(self) -> Optional[datetime]:
        """Get the timestamp of the last completed cycle."""
        return self._last_cycle_time
    
    @property
    def last_cycle_duration(self) -> float:
        """Get the duration of the last cycle in seconds."""
        return self._last_cycle_duration
    
    @property
    def error_count(self) -> int:
        """Get the total number of errors encountered."""
        return self._error_count
    
    @property
    def start_time(self) -> Optional[datetime]:
        """Get when the bot was started."""
        return self._start_time
    
    @property
    def uptime(self) -> Optional[float]:
        """Get the uptime in seconds."""
        if self._start_time:
            return (datetime.now() - self._start_time).total_seconds()
        return None
    
    def set_running(self, running: bool):
        """Set the running state."""
        self._is_running = running
        if running and not self._start_time:
            self._start_time = datetime.now()
    
    def set_paused(self, paused: bool):
        """Set the paused state."""
        self._is_paused = paused
    
    def update_last_cycle(self, cycle_time: datetime, duration: float):
        """Update the last cycle information."""
        self._last_cycle_time = cycle_time
        self._last_cycle_duration = duration
    
    def increment_error_count(self):
        """Increment the error count."""
        self._error_count += 1
    
    def reset_error_count(self):
        """Reset the error count."""
        self._error_count = 0
    
    def get_summary(self) -> dict:
        """Get a summary of the current state."""
        uptime = self.uptime
        uptime_str = f"{uptime:.1f}s" if uptime else "N/A"
        
        return {
            "running": self._is_running,
            "paused": self._is_paused,
            "uptime": uptime_str,
            "last_cycle": self._last_cycle_time.isoformat() if self._last_cycle_time else "Never",
            "cycle_duration": f"{self._last_cycle_duration:.2f}s",
            "errors": self._error_count
        } 