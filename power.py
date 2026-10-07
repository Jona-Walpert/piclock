"""Power management and energy optimization module for Raspberry Pi Zero 2 W.
"""

import logging
import os
import subprocess
from pathlib import Path
from typing import Optional

import config

logger = logging.getLogger(__name__)


class PowerManager:
    """Manages low-power modes, peripheral shutoff, and energy savings."""

    def __init__(self):
        self.is_raspberry_pi = Path("/sys/firmware/devicetree/base/model").exists()

    def disable_hdmi(self) -> bool:
        """Disables HDMI output circuitry to save ~25-30 mA."""
        if not self.is_raspberry_pi:
            return False

        try:
            # Try vcgencmd first
            res = subprocess.run(["vcgencmd", "display_power", "0"], capture_output=True, text=True, timeout=2)
            if res.returncode == 0:
                logger.info("HDMI display circuitry powered down via vcgencmd (saved ~25mA)")
                return True
        except Exception:
            pass

        try:
            # Fallback to tvservice if present
            res = subprocess.run(["tvservice", "-o"], capture_output=True, text=True, timeout=2)
            if res.returncode == 0:
                logger.info("HDMI output disabled via tvservice")
                return True
        except Exception as e:
            logger.debug("Could not disable HDMI: %s", e)

        return False

    def disable_leds(self) -> bool:
        """Turns off the onboard green activity (ACT) LED to save ~5 mA."""
        led_paths = [
            Path("/sys/class/leds/ACT/brightness"),
            Path("/sys/class/leds/led0/brightness"),
        ]

        for p in led_paths:
            if p.exists():
                try:
                    p.write_text("0")
                    logger.info("Onboard ACT LED switched off (%s)", p)
                    return True
                except Exception as e:
                    logger.debug("Could not write to %s: %s", p, e)

        return False

    def enable_wifi_power_save(self) -> bool:
        """Enables 802.11 power saving mode on wlan0 interface."""
        try:
            res = subprocess.run(["iw", "dev", "wlan0", "set", "power_save", "on"], capture_output=True, text=True, timeout=2)
            if res.returncode == 0:
                logger.info("WiFi power-save mode enabled on wlan0")
                return True
        except Exception as e:
            logger.debug("Could not enable WiFi power-save: %s", e)

        return False

    def set_cpu_powersave_governor(self) -> bool:
        """Sets CPU frequency scaling governor to 'powersave' (locks to 600 MHz)."""
        cpu_path = Path("/sys/devices/system/cpu/cpufreq/policy0/scaling_governor")
        if cpu_path.exists():
            try:
                cpu_path.write_text("powersave")
                logger.info("CPU governor set to 'powersave' (600 MHz)")
                return True
            except Exception as e:
                logger.debug("Could not set CPU governor: %s", e)

        return False

    def set_wifi_radio(self, enabled: bool) -> bool:
        """Enables or disables the WiFi radio for on-demand NTP updates."""
        state = "unblock" if enabled else "block"
        try:
            res = subprocess.run(["rfkill", state, "wifi"], capture_output=True, text=True, timeout=3)
            if res.returncode == 0:
                logger.info("WiFi radio set to: %s", "ON" if enabled else "OFF")
                return True
        except Exception as e:
            logger.debug("Could not set WiFi radio state: %s", e)

        return False

    def apply_optimizations(self):
        """Applies all enabled energy-saving optimizations."""
        if not getattr(config, "ENABLE_POWER_SAVING", False):
            logger.debug("Power saving optimizations are disabled in config")
            return

        logger.info("Applying power-saving optimizations for Pi Zero 2 W...")

        if getattr(config, "DISABLE_HDMI", True):
            self.disable_hdmi()

        if getattr(config, "DISABLE_ACT_LED", True):
            self.disable_leds()

        if getattr(config, "WIFI_POWER_SAVE", True):
            self.enable_wifi_power_save()

        if getattr(config, "CPU_POWERSAVE_GOVERNOR", True):
            self.set_cpu_powersave_governor()

        logger.info("Power optimizations applied successfully")
