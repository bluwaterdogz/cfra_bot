from abc import ABC, abstractmethod
from typing import Any, Dict

class Parser(ABC):
    @abstractmethod
    async def parse(self, raw_data: Any) -> Dict[str, Any]:
        """
        Parse raw data into a structured format.
        
        Args:
            raw_data: The raw data from the scraper
            
        Returns:
            Dict containing parsed/structured data
        """
        pass 