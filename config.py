"""Configuration settings for PiClock E-Paper Digital Clock.
"""

import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
FONTS_DIR = BASE_DIR / "fonts"

# Display Driver Configuration
# Options: "epd2in13_V4", "epd2in13_V3", "epd2in13_V2", "mock"
DISPLAY_DRIVER = os.getenv("PICLOCK_DRIVER", "epd2in13_V4")
DISPLAY_WIDTH = 250
DISPLAY_HEIGHT = 122

# Display Rotation (0 or 180 for landscape inverted)
DISPLAY_ROTATION = int(os.getenv("PICLOCK_ROTATION", "0"))

# Refresh & Anti-Ghosting Settings
# Full refresh interval in minutes (30-60 minutes recommended)
FULL_REFRESH_INTERVAL_MINUTES = int(os.getenv("PICLOCK_FULL_REFRESH_INTERVAL", "30"))

# Ghosting Prevention: Inversion/cleaning cycles before full refresh
# Each cycle alternates Clear(0x00) [Black] and Clear(0xFF) [White]
CLEANING_CYCLES = int(os.getenv("PICLOCK_CLEANING_CYCLES", "2"))
CLEANING_DELAY_SEC = float(os.getenv("PICLOCK_CLEANING_DELAY", "0.15"))

# Partial Refresh for minute jumps
PARTIAL_REFRESH_ENABLED = True

# Typography & Layout
FONT_FAMILY = "Roboto"  # "Roboto" or "DejaVuSans"
TIMEZONE = os.getenv("PICLOCK_TIMEZONE", "Europe/Berlin")
TIME_FORMAT = "%H:%M"
DATE_FORMAT = "%d.%m.%Y"
SHOW_DATE = True
SHOW_WEEKDAY = True
SHOW_STATUS_INDICATOR = True  # Subtle dot indicating NTP sync status

# German Weekdays
GERMAN_WEEKDAYS = {
    0: "Montag",
    1: "Dienstag",
    2: "Mittwoch",
    3: "Donnerstag",
    4: "Freitag",
    5: "Samstag",
    6: "Sonntag",
}

# German Months
GERMAN_MONTHS = {
    1: "Jan",
    2: "Feb",
    3: "Mär",
    4: "Apr",
    5: "Mai",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Okt",
    11: "Nov",
    12: "Dez",
}

# Time Synchronization
NTP_SYNC_INTERVAL_HOURS = int(os.getenv("PICLOCK_NTP_INTERVAL", "1"))
NTP_ENABLED = True
NTP_SERVERS = ["pool.ntp.org", "0.debian.pool.ntp.org", "time.google.com"]

# Power Saving & Battery Optimization (for Raspberry Pi Zero 2 W)
# Optimizes peripherals: HDMI off, ACT LED off, WiFi power-save, CPU governor
ENABLE_POWER_SAVING = os.getenv("PICLOCK_POWER_SAVING", "true").lower() in ("true", "1", "yes")
DISABLE_HDMI = True
DISABLE_ACT_LED = True
WIFI_POWER_SAVE = True
CPU_POWERSAVE_GOVERNOR = True

# Logging
LOG_LEVEL = os.getenv("PICLOCK_LOG_LEVEL", "INFO")

