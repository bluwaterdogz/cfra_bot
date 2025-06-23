from abc import ABC, abstractmethod

class Handler(ABC):
    @abstractmethod
    async def handle(self, data: dict):
        pass