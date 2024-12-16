# only function to get interval in seconds from string
# 1s, 1m, 1h, 1d, 1w, 1y, auto
def calculate_time_seconds(interval: str) -> int:
    """
    Calculate the time in seconds from a string interval.
    :param interval: str: The interval string. Must be in the format of '1s', '1m', '1h', '1d', '1w', '1y', or 'auto'.
    :return: int: The interval in seconds.
    """
    interval = interval.lower()
    if interval == "auto":
        return -1
    if interval[-1] not in ["s", "m", "h", "d", "w", "y"]:
        raise ValueError(f"Invalid interval: {interval}. Must end with one of ['s', 'm', 'h', 'd', 'w', 'y'].")
    value = int(interval[:-1])
    unit = interval[-1]
    if unit == "s":
        return value
    if unit == "m":
        return value * 60
    if unit == "h":
        return value * 3600
    if unit == "d":
        return value * 86400
    if unit == "w":
        return value * 604800
    if unit == "y":
        return value * 31536000
    raise ValueError(f"Invalid interval: {interval}. Must end with one of ['s', 'm', 'h', 'd', 'w', 'y'].")
