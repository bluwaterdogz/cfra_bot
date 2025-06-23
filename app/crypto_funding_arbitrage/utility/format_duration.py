from datetime import timedelta

def format_duration(hours: float) -> str:
    if hours == float("inf"):
        return "Infinity"
    
    td = timedelta(hours=hours)
    days = td.days
    hours = td.seconds // 3600
    minutes = (td.seconds % 3600) // 60

    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")

    return " ".join(parts) or "0m"