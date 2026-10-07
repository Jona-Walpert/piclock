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
from notify import get_pending_notification

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
        # 1. BOOT SPLASH SCREEN
        # Immediately display fullscreen 'PiClock' splash screen so user knows system is up
        logger.info("Displaying fullscreen boot splash screen...")
        splash_img = display_mgr.create_splash_image("PiClock", "System starting...")
        display_mgr.partial_refresh(splash_img)

        # Wait a minimum of 4 seconds or until the upcoming :00 mark
        now = datetime.now(tz)
        seconds_to_first_minute = 60.0 - now.second - (now.microsecond / 1_000_000.0)
        if seconds_to_first_minute < 4.0:
            seconds_to_first_minute += 60.0

        logger.info("Splash screen active. Aligning to next minute mark (%.1fs)...", seconds_to_first_minute)
        # Sleep until minute mark while still checking for shutdown
        if shutdown_event.wait(timeout=seconds_to_first_minute):
            return

        # First regular clock render precisely at :00.00
        now = datetime.now(tz)
        logger.info("First clock display render at exact minute mark %02d:%02d:00", now.hour, now.minute)
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

            # Sleep in small increments to check for live on-screen notifications
            end_sleep_time = time.monotonic() + seconds_remaining
            while time.monotonic() < end_sleep_time and not shutdown_event.is_set():
                # Check for live notifications (e.g. SSH login, update, network status)
                notif = get_pending_notification()
                if notif:
                    logger.info("Displaying notification on screen: [%s] %s", notif['title'], notif['message'])
                    notif_img = display_mgr.create_notification_image(
                        notif['title'], notif['message'], notif.get('time_str')
                    )
                    display_mgr.partial_refresh(notif_img)
                    # Hold notification for requested duration
                    duration = min(notif.get('duration', 8), 20)
                    shutdown_event.wait(timeout=duration)
                    # Restore clock screen immediately after notification
                    current_now = datetime.now(tz)
                    restored_clock = display_mgr.create_clock_image(current_now, is_synced=time_sync.is_recently_synced())
                    display_mgr.partial_refresh(restored_clock)

                # Sleep chunk of 0.5s
                chunk = min(0.5, end_sleep_time - time.monotonic())
                if chunk > 0:
                    shutdown_event.wait(timeout=chunk)

            if shutdown_event.is_set():
                break

            # Woke up at minute boundary! Re-check time
            now = datetime.now(tz)
            current_minute = (now.hour, now.minute)

            # SAFETY CHECK 1: Discard duplicate/early wakeups
            if current_minute == last_rendered_minute:
                time.sleep(0.05)
                continue

            # SAFETY CHECK 2: STRICT MINUTE BOUNDARY CHECK
            # Only refresh if we are at the very beginning of the minute (second <= 2).
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

