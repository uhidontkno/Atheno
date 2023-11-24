import datetime
class formatting:
 def timeformat(epoch):
    delta = datetime.timedelta(seconds=epoch)
    days, seconds = delta.days, delta.seconds
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    result = []

    if days and days >= 1:
        result.append(f"{days}d")
    if hours and hours >= 1:
        result.append(f"{hours}h")
    if minutes:
        result.append(f"{minutes}m")
    if seconds:
        result.append(f"{seconds}s")

    return ":".join(result) if result else "0s"
 def percent(current, end, start=0):
    if start == end:
        return 100.0 if current > end else 0.0
    return (current - start) / (end - start) * 100