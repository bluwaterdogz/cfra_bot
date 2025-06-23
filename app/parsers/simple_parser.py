from app.parsers.parser_interface import Parser
from typing import Any, Dict

class SimpleParser(Parser):
    """Default parser that wraps raw data into a structured format."""
    
    async def parse(self, raw_data: Any) -> Dict[str, Any]:
        """
        Parse raw data by wrapping it in a structured format.
        
        Args:
            raw_data: The raw data from the scraper
            
        Returns:
            Dict containing the wrapped data with metadata
        """
        return {
            "raw_data": raw_data,
            "parsed_at": self._get_timestamp(),
            "parser_type": "simple"
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat() 