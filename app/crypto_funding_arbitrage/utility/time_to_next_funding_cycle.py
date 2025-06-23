from datetime import datetime, timedelta

def time_to_next_funding_cycle(now: datetime) -> timedelta:
    # Binance cycles: 00:00, 08:00, 16:00 UTC
    cycle_hours = [0, 8, 16]
    current_hour = now.hour

    next_cycle_hour = next((h for h in cycle_hours if h > current_hour), cycle_hours[0])
    next_cycle = now.replace(hour=next_cycle_hour, minute=0, second=0, microsecond=0)

    if next_cycle <= now:
        next_cycle += timedelta(days=1)

    return next_cycle - now