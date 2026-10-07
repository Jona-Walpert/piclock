"""Driver adapter for Waveshare 2.13inch E-Paper displays (V4, V3, V2).
"""

import logging
from PIL import Image
from .base import BaseDisplayDriver

logger = logging.getLogger(__name__)


class Waveshare2in13Driver(BaseDisplayDriver):
    """Adapter wrapping Waveshare 2.13 EPD driver variants."""

    def __init__(self, revision: str = "epd2in13_V4"):
        self.revision = revision
        self._epd = None
        self._load_driver()

    def _load_driver(self):
        try:
            if self.revision == "epd2in13_V4":
                from .waveshare import epd2in13_V4 as epd_mod
            elif self.revision == "epd2in13_V3":
                from .waveshare import epd2in13_V3 as epd_mod
            elif self.revision == "epd2in13_V2":
                from .waveshare import epd2in13_V2 as epd_mod
            else:
                raise ValueError(f"Unsupported Waveshare revision: {self.revision}")
            self._epd = epd_mod.EPD()
            logger.info("Loaded Waveshare driver: %s (w=%d, h=%d)", self.revision, self.width, self.height)
        except Exception as e:
            logger.error("Failed to load Waveshare driver %s: %s", self.revision, e)
            raise

    @property
    def width(self) -> int:
        # In landscape orientation, display height (250) is the width
        return max(self._epd.width, self._epd.height)

    @property
    def height(self) -> int:
        # In landscape orientation, display width (122) is the height
        return min(self._epd.width, self._epd.height)

    def init(self) -> None:
        """Initialize display for full refresh."""
        logger.debug("Initializing EPD for full refresh")
        if hasattr(self._epd, "FULL_UPDATE"):
            self._epd.init(self._epd.FULL_UPDATE)
        else:
            self._epd.init()

    def init_partial(self) -> None:
        """Initialize display for partial refresh."""
        logger.debug("Initializing EPD for partial refresh")
        if hasattr(self._epd, "init_part"):
            self._epd.init_part()
        elif hasattr(self._epd, "PART_UPDATE"):
            self._epd.init(self._epd.PART_UPDATE)
        else:
            self._epd.init()

    def clear(self, color: int = 0xFF) -> None:
        """Clear display buffer and screen."""
        logger.debug("Clearing EPD with color 0x%02X", color)
        self._epd.Clear(color)

    def display_full(self, image: Image.Image) -> None:
        """Render full display image and refresh."""
        buffer = self._epd.getbuffer(image)
        if hasattr(self._epd, "displayPartBaseImage"):
            self._epd.displayPartBaseImage(buffer)
        else:
            self._epd.display(buffer)

    def display_partial(self, image: Image.Image) -> None:
        """Render partial display update without screen flash."""
        buffer = self._epd.getbuffer(image)
        self._epd.displayPartial(buffer)

    def sleep(self) -> None:
        """Put display into deep sleep to prevent panel burn-in/damage."""
        logger.debug("Putting EPD into sleep mode")
        self._epd.sleep()

