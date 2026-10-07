"""Display Manager and UI rendering engine for PiClock.
"""

import logging
import os
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from PIL import Image, ImageDraw, ImageFont

import config
from drivers import get_driver, BaseDisplayDriver

logger = logging.getLogger(__name__)


class DisplayManager:
    """Manages clock layout rendering, partial updates, and ghosting elimination."""

    def __init__(self, driver: BaseDisplayDriver = None):
        self.driver = driver or get_driver(config.DISPLAY_DRIVER)
        self.width = config.DISPLAY_WIDTH
        self.height = config.DISPLAY_HEIGHT
        self.rotation = config.DISPLAY_ROTATION
        self.timezone = ZoneInfo(config.TIMEZONE)

        self._load_fonts()
        self._is_initialized = False

    def _load_fonts(self):
        """Loads typography fonts with fallbacks."""
        # Primary font files
        roboto_bold = config.FONTS_DIR / "Roboto-Bold.ttf"
        roboto_regular = config.FONTS_DIR / "Roboto-Regular.ttf"
        dejavu_bold = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
        dejavu_regular = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")

        # Select font paths
        if roboto_bold.exists():
            time_font_path = str(roboto_bold)
            date_font_path = str(roboto_regular if roboto_regular.exists() else roboto_bold)
        elif dejavu_bold.exists():
            time_font_path = str(dejavu_bold)
            date_font_path = str(dejavu_regular if dejavu_regular.exists() else dejavu_bold)
        else:
            time_font_path = None
            date_font_path = None

        self._time_font_path = time_font_path
        self._date_font_path = date_font_path

        if time_font_path:
            logger.info("Using fonts from: %s", time_font_path)
            self.font_time = ImageFont.truetype(time_font_path, 64)
            self.font_date = ImageFont.truetype(date_font_path, 17)
            self.font_status = ImageFont.truetype(date_font_path, 11)
            self.font_day_large = ImageFont.truetype(time_font_path, 36)
        else:
            logger.warning("No TrueType font found, using default bitmap font")
            self.font_time = ImageFont.load_default()
            self.font_date = ImageFont.load_default()
            self.font_status = ImageFont.load_default()
            self.font_day_large = ImageFont.load_default()

    def initialize_display(self):
        """Initialize the underlying hardware display."""
        if not self._is_initialized:
            logger.info("Initializing display hardware...")
            self.driver.init()
            self._is_initialized = True

    def create_clock_image(self, current_time: datetime, is_synced: bool = True) -> Image.Image:
        """Renders the clock frame onto a 1-bit monochrome PIL Image.

        Args:
            current_time: The current datetime.
            is_synced: Whether time was recently synced with NTP.

        Returns:
            A PIL Image in mode '1' (255=White background, 0=Black text).
        """
        # Create pure white background (255)
        image = Image.new("1", (self.width, self.height), 255)
        draw = ImageDraw.Draw(image)

        # 1. Format Time (HH:MM)
        time_str = current_time.strftime(config.TIME_FORMAT)
        time_bbox = draw.textbbox((0, 0), time_str, font=self.font_time)
        time_w = time_bbox[2] - time_bbox[0]
        time_h = time_bbox[3] - time_bbox[1]

        # Center time in top section
        time_x = (self.width - time_w) // 2
        time_y = 4
        draw.text((time_x, time_y), time_str, font=self.font_time, fill=0)

        # 2. Subtle Divider Line
        divider_y = 74
        draw.line([(18, divider_y), (self.width - 18, divider_y)], fill=0, width=1)

        # 3. Format Date & Weekday (German format: "Mi, 07. Okt 2026")
        weekday_name = config.GERMAN_WEEKDAYS.get(current_time.weekday(), current_time.strftime("%a"))
        month_name = config.GERMAN_MONTHS.get(current_time.month, current_time.strftime("%b"))
        date_str = f"{weekday_name}, {current_time.day:02d}. {month_name} {current_time.year}"

        date_bbox = draw.textbbox((0, 0), date_str, font=self.font_date)
        date_w = date_bbox[2] - date_bbox[0]
        date_x = (self.width - date_w) // 2
        date_y = 86
        draw.text((date_x, date_y), date_str, font=self.font_date, fill=0)

        # 4. Status Indicator (small dot if synced)
        if config.SHOW_STATUS_INDICATOR and is_synced:
            # Small 3x3 dot at top-right
            draw.ellipse([(self.width - 12, 10), (self.width - 8, 14)], fill=0)

        # Apply rotation if configured
        if self.rotation == 180:
            image = image.rotate(180)

        return image

    def create_new_day_image(self, current_time: datetime) -> Image.Image:
        """Renders a prominent new-day banner shown at midnight (00:00:00 to 00:00:29).

        Displays the full weekday name in large typography across the screen.
        """
        image = Image.new("1", (self.width, self.height), 255)
        draw = ImageDraw.Draw(image)

        # 1. Header: "NEUER TAG"
        header_str = "★ NEUER TAG ★"
        header_bbox = draw.textbbox((0, 0), header_str, font=self.font_status)
        header_w = header_bbox[2] - header_bbox[0]
        draw.text(((self.width - header_w) // 2, 8), header_str, font=self.font_status, fill=0)

        # Decorative line above weekday
        draw.line([(25, 24), (self.width - 25, 24)], fill=0, width=1)

        # 2. Large Weekday Name (e.g. "DONNERSTAG")
        weekday_name = config.GERMAN_WEEKDAYS.get(current_time.weekday(), current_time.strftime("%A")).upper()

        font = self.font_day_large
        if self._time_font_path:
            font_size = 36
            bbox = draw.textbbox((0, 0), weekday_name, font=font)
            while (bbox[2] - bbox[0]) > 225 and font_size > 20:
                font_size -= 2
                font = ImageFont.truetype(self._time_font_path, font_size)
                bbox = draw.textbbox((0, 0), weekday_name, font=font)
        else:
            bbox = draw.textbbox((0, 0), weekday_name, font=font)

        day_w = bbox[2] - bbox[0]
        day_x = (self.width - day_w) // 2
        day_y = 35
        draw.text((day_x, day_y), weekday_name, font=font, fill=0)

        # Decorative line below weekday
        draw.line([(25, 78), (self.width - 25, 78)], fill=0, width=1)

        # 3. Date Subtitle: "08. Okt 2026"
        month_name = config.GERMAN_MONTHS.get(current_time.month, current_time.strftime("%b"))
        date_str = f"{current_time.day:02d}. {month_name} {current_time.year}"
        date_bbox = draw.textbbox((0, 0), date_str, font=self.font_date)
        date_w = date_bbox[2] - date_bbox[0]
        draw.text(((self.width - date_w) // 2, 88), date_str, font=self.font_date, fill=0)

        if self.rotation == 180:
            image = image.rotate(180)

        return image

    def full_refresh_with_cleaning(self, image: Image.Image):
        """Performs ghosting elimination cycles followed by a full display refresh.

        This alternates Black and White flashes to reset all e-paper microcapsules,
        removing residual ghosting artifacts before applying the new frame.
        """
        self.initialize_display()
        logger.info("Starting anti-ghosting deep clean (%d cycles)...", config.CLEANING_CYCLES)

        for cycle in range(1, config.CLEANING_CYCLES + 1):
            logger.debug("Cleaning cycle %d: Flashing Black", cycle)
            self.driver.clear(0x00)  # Black
            time.sleep(config.CLEANING_DELAY_SEC)

            logger.debug("Cleaning cycle %d: Flashing White", cycle)
            self.driver.clear(0xFF)  # White
            time.sleep(config.CLEANING_DELAY_SEC)

        logger.info("Applying full display refresh")
        self.driver.display_full(image)

    def partial_refresh(self, image: Image.Image):
        """Performs a fast partial refresh without screen flickering."""
        if not self._is_initialized:
            self.initialize_display()

        logger.debug("Applying partial display refresh")
        self.driver.display_partial(image)

    def sleep(self):
        """Puts the display driver to sleep safely."""
        logger.info("Putting display to sleep")
        self.driver.sleep()
        self._is_initialized = False
