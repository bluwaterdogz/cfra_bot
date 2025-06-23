from app.handlers.handler_interface import Handler
import json
from datetime import datetime
import os

class SaveToFileHandler(Handler):
    async def handle(self, data: dict):
        # Create the output directory if it doesn't exist
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)

        # Timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(output_dir, f"data_{timestamp}.json")

        # Write data to JSON
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        print(f"✅ Wrote data to {filepath}")