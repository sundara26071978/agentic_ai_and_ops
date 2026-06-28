city = "India"

print(f"The city is: {city}")

import time

def get_current_time() -> str:
    """
    Returns the current time as a formatted string.
    """
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

print(f"The current time is: {get_current_time()}")