FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create logs directory
RUN mkdir -p /app/logs && chmod 755 /app/logs

# Make sure Python sees /app as the module root
ENV PYTHONPATH=/app

# Since main.py is in app/, this is the correct path:
CMD ["python", "app/main.py"]