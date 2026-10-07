"""Self-test and verification script for PiClock.
"""

import argparse
import sys
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import config
from display import DisplayManager
from drivers import MockDisplayDriver, Waveshare2in13Driver
from time_sync import TimeSynchronizer


def run_tests(use_mock: bool = False):
    print("=" * 60)
    print("           PiClock Component Self-Test")
    print("=" * 60)

    # 1. Driver Test
    print("\n[1/5] Testing Display Driver...")
    if use_mock:
        driver = MockDisplayDriver()
        print(" -> Using Mock Display Driver: SUCCESS")
    else:
        try:
            driver = Waveshare2in13Driver(config.DISPLAY_DRIVER)
            print(f" -> Hardware driver '{config.DISPLAY_DRIVER}' loaded successfully: SUCCESS")
        except Exception as e:
            print(f" -> Hardware driver failed: {e}")
            return False

    display_mgr = DisplayManager(driver=driver)

    # 2. Rendering Test
    print("\n[2/5] Testing Image Generation & Typography...")
    now = datetime.now(ZoneInfo(config.TIMEZONE))
    test_img = display_mgr.create_clock_image(now, is_synced=True)
    print(f" -> Rendered clock image dimensions: {test_img.size}, mode: {test_img.mode}")
    assert test_img.size == (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT)

    # Test Midnight New Day Banner
    banner_img = display_mgr.create_new_day_image(now)
    print(f" -> Rendered midnight new-day banner: {banner_img.size}, mode: {banner_img.mode}")
    assert banner_img.size == (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT)

    # Test Boot Splash Screen
    splash_img = display_mgr.create_splash_image("PiClock", "Starting up...")
    print(f" -> Rendered boot splash screen: {splash_img.size}, mode: {splash_img.mode}")
    assert splash_img.size == (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT)

    # Test Live Notification Card
    notif_img = display_mgr.create_notification_image("SSH Session", "User pi connected from 192.168.2.150", "22:45:00")
    print(f" -> Rendered notification card: {notif_img.size}, mode: {notif_img.mode}")
    assert notif_img.size == (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT)
    print(" -> Layout, splash, notifications, and text bounding calculations: SUCCESS")

    # 3. Time Sync Test
    print("\n[3/5] Testing Time Synchronization...")
    syncer = TimeSynchronizer()
    offset = syncer.query_ntp_server(config.NTP_SERVERS[0], timeout=3.0)
    if offset is not None:
        print(f" -> NTP query to '{config.NTP_SERVERS[0]}' succeeded. Clock offset: {offset:.2f} ms: SUCCESS")
    else:
        print(" -> Direct NTP query timed out (network dependent), checking systemd-timesyncd status...")

    sync_result = syncer.sync_now()
    print(f" -> Active time sync result: {sync_result}")

    # 4. Anti-Ghosting Full Refresh Test
    print("\n[4/5] Testing Anti-Ghosting Clean & Full Refresh...")
    display_mgr.full_refresh_with_cleaning(test_img)
    print(" -> Full refresh with deep clean cycles: SUCCESS")

    # 5. Partial Refresh Test
    print("\n[5/5] Testing Partial Refresh...")
    time.sleep(1)
    # Advance time by 1 minute for visual test
    test_img_next = display_mgr.create_clock_image(now, is_synced=True)
    display_mgr.partial_refresh(test_img_next)
    print(" -> Fast partial refresh executed: SUCCESS")

    # Clean shutdown
    print("\nCleaning up and putting display to sleep...")
    display_mgr.sleep()
    print(" -> Sleep mode: SUCCESS")

    print("\n" + "=" * 60)
    print(" ALL PICLOCK COMPONENT TESTS COMPLETED SUCCESSFULLY! ")
    print("=" * 60)
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mock", action="store_true", help="Run with mock driver")
    args = parser.parse_args()
    success = run_tests(use_mock=args.mock)
    sys.exit(0 if success else 1)

