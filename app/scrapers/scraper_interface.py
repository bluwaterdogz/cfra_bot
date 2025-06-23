from abc import ABC, abstractmethod

class Scraper(ABC):
    @abstractmethod
    async def fetch(self) -> dict:
        pass