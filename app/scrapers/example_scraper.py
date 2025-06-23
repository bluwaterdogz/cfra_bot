from app.scrapers.scraper_interface import Scraper
import httpx
import random

class ExampleScraper(Scraper):
    async def fetch(self):
        """Fetch sample data that might contain crypto-related content."""
        async with httpx.AsyncClient() as client:
            # Fetch from httpbin for basic testing
            r = await client.get("https://httpbin.org/get")
            
            # Add some sample crypto-related content for testing keyword matching
            crypto_keywords = ["bitcoin", "ethereum", "crypto", "blockchain", "defi"]
            sample_content = {
                "status": r.status_code,
                "content": r.text,
                "sample_data": {
                    "crypto_news": f"Latest {random.choice(crypto_keywords)} price update",
                    "market_data": {
                        "bitcoin_price": "$45,000",
                        "ethereum_price": "$3,200",
                        "market_cap": "$2.1 trillion"
                    },
                    "timestamp": "2024-01-15T10:30:00Z"
                }
            }
            
            return sample_content