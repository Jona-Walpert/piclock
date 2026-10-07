"""Main entry point for PiClock E-Paper Digital Clock.
"""

import logging
import signal
import sys
import time
from datetime import datetime
from threading import Event
from zoneinfo import ZoneInfo

import config
from display import DisplayManager
from time_sync import TimeSynchronizer
from power import PowerManager

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("piclock")

# Graceful shutdown event
shutdown_event = Event()


def signal_handler(signum, frame):
    """Handles termination signals for clean shutdown."""
    sig_name = signal.Signals(signum).name
    logger.info("Received termination signal %s. Shutting down cleanly...", sig_name)
    shutdown_event.set()


def main():
    """Runs the main digital clock loop."""
    logger.info("   Starting PiClock E-Paper Digital Clock")
    logger.info("   Driver: %s, Resolution: %dx%d", config.DISPLAY_DRIVER, config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT)
    logger.info("   Full Refresh Interval: %d min", config.FULL_REFRESH_INTERVAL_MINUTES)
    logger.info("   Ghosting Cleaning Cycles: %d", config.CLEANING_CYCLES)
    logger.info("   Timezone: %s", config.TIMEZONE)

    # Register OS signals
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    tz = ZoneInfo(config.TIMEZONE)

    # Initialize modules
    power_mgr = PowerManager()
    power_mgr.apply_optimizations()

    time_sync = TimeSynchronizer()
    display_mgr = DisplayManager()

    # Start background NTP time synchronization
    if config.NTP_ENABLED:
        time_sync.start()

    try:
        # 1. STRICT SYNCHRONIZATION ON STARTUP:
        # Never refresh the screen immediately in the middle of a minute.
        # Wait until the upcoming :00 second mark before performing the initial render.
        now = datetime.now(tz)
        if now.second != 0 or now.microsecond > 100_000:
            seconds_to_first_minute = 60.0 - now.second - (now.microsecond / 1_000_000.0)
            target_min = (now.minute + 1) % 60
            target_hour = now.hour if now.minute < 59 else (now.hour + 1) % 24
            logger.info(
                "PiClock started at %02d:%02d:%02d. Aligning to next minute mark (waiting %.2fs until %02d:%02d:00)...",
                now.hour, now.minute, now.second, seconds_to_first_minute, target_hour, target_min
            )
            if shutdown_event.wait(timeout=seconds_to_first_minute):
                return

        # First render happens precisely at the 00-second mark of the new minute
        now = datetime.now(tz)
        logger.info("First display render at exact minute mark %02d:%02d:00", now.hour, now.minute)
        initial_img = display_mgr.create_clock_image(now, is_synced=time_sync.is_synced)
        display_mgr.full_refresh_with_cleaning(initial_img)

        last_full_refresh_time = time.monotonic()
        last_rendered_minute = (now.hour, now.minute)

        while not shutdown_event.is_set():
            now = datetime.now(tz)

            # Precise calculation to sleep until the next 00-second mark
            seconds_remaining = 60.0 - now.second - (now.microsecond / 1_000_000.0)
            if seconds_remaining <= 0.05:
                seconds_remaining += 60.0

            logger.debug("Sleeping %.2f seconds until next minute tick...", seconds_remaining)
            if shutdown_event.wait(timeout=seconds_remaining):
                break

            # Woke up! Re-check time
            now = datetime.now(tz)
            current_minute = (now.hour, now.minute)

            # SAFETY CHECK 1: Discard early wakeups within the same minute
            if current_minute == last_rendered_minute:
                time.sleep(0.05)
                continue

            # SAFETY CHECK 2: STRICT MINUTE BOUNDARY CHECK
            # Only refresh if we are at the very beginning of the minute (second <= 2).
            # If off-schedule (e.g. clock jumped or thread lagged), skip refresh to never update mid-minute!
            if now.second > 2:
                logger.warning(
                    "Off-schedule wakeup at %02d:%02d:%02d. Skipping refresh to prevent mid-minute updates.",
                    now.hour, now.minute, now.second
                )
                continue

            last_rendered_minute = current_minute
            elapsed_since_full = time.monotonic() - last_full_refresh_time
            needs_full_refresh = elapsed_since_full >= (config.FULL_REFRESH_INTERVAL_MINUTES * 60)

            try:
                # Special midnight feature: Display new-day banner from 00:00:00 to 00:00:29
                if current_minute == (0, 0):
                    logger.info("Midnight reached! Showing new day banner for 30s (%s)", now.strftime("%A"))
                    day_banner = display_mgr.create_new_day_image(now)
                    display_mgr.partial_refresh(day_banner)

                    # Wait until 00:00:30 mark
                    seconds_to_30 = 30.0 - now.second - (now.microsecond / 1_000_000.0)
                    if seconds_to_30 > 0.05:
                        if shutdown_event.wait(timeout=seconds_to_30):
                            break

                    # Switch back to standard clock display for 00:00:30 - 00:00:59
                    now = datetime.now(tz)
                    logger.info("Returning to standard clock display at 00:00:30")
                    clock_img = display_mgr.create_clock_image(now, is_synced=time_sync.is_recently_synced())
                    display_mgr.partial_refresh(clock_img)
                    continue

                # Render updated clock image
                clock_img = display_mgr.create_clock_image(now, is_synced=time_sync.is_recently_synced())

                if needs_full_refresh and now.minute in (0, 30):
                    logger.info("Scheduled full refresh triggered at %02d:%02d:00 (elapsed: %.1f min)",
                                now.hour, now.minute, elapsed_since_full / 60.0)
                    display_mgr.full_refresh_with_cleaning(clock_img)
                    last_full_refresh_time = time.monotonic()
                else:
                    logger.info("Minute tick %02d:%02d:00 (Partial Refresh)", now.hour, now.minute)
                    display_mgr.partial_refresh(clock_img)

            except Exception as e:
                logger.exception("Error updating display at %02d:%02d: %s", now.hour, now.minute, e)
                # Recover gracefully without crashing the service
                time.sleep(1.0)

    except Exception as e:
        logger.exception("Unexpected error in main clock loop: %s", e)
    finally:
        logger.info("Performing clean display shutdown...")
        try:
            time_sync.stop()
            display_mgr.sleep()
        except Exception as e:
            logger.error("Error during cleanup: %s", e)
        logger.info("PiClock exited cleanly.")


if __name__ == "__main__":
    main()

