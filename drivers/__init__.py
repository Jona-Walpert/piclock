"""Display driver factory and export.
"""

from .base import BaseDisplayDriver
from .mock import MockDisplayDriver
from .driver_waveshare import Waveshare2in13Driver


def get_driver(driver_name: str) -> BaseDisplayDriver:
    """Factory function returning the configured display driver.

    Args:
        driver_name: Name of driver (e.g. 'epd2in13_V4', 'epd2in13_V3', 'epd2in13_V2', 'mock')
    """
    driver_name_lower = driver_name.lower()
    if driver_name_lower == "mock":
        return MockDisplayDriver()
    elif driver_name_lower in ("epd2in13_v4", "epd2in13_v3", "epd2in13_v2"):
        return Waveshare2in13Driver(revision=driver_name)
    else:
        raise ValueError(f"Unknown display driver: {driver_name}")


__all__ = ["BaseDisplayDriver", "MockDisplayDriver", "Waveshare2in13Driver", "get_driver"]

