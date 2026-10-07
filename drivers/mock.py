"""Mock display driver for offline testing and development without physical hardware.
"""

import logging
from PIL import Image
from .base import BaseDisplayDriver

logger = logging.getLogger(__name__)


class MockDisplayDriver(BaseDisplayDriver):
    """Simulates an E-Paper display and saves rendered images to disk."""

    def __init__(self, width: int = 250, height: int = 122, output_path: str = "/tmp/piclock_preview.png"):
        self._width = width
        self._height = height
        self._output_path = output_path
        self._is_sleeping = False
        logger.info("MockDisplayDriver initialized (%dx%d), preview at %s", self._width, self._height, self._output_path)

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    def init(self) -> None:
        logger.info("[MockDisplay] Hardware init (full update mode)")
        self._is_sleeping = False

    def init_partial(self) -> None:
        logger.info("[MockDisplay] Hardware init (partial update mode)")
        self._is_sleeping = False

    def clear(self, color: int = 0xFF) -> None:
        color_name = "WHITE" if color == 0xFF else "BLACK"
        logger.info("[MockDisplay] Clear screen with %s (0x%02X)", color_name, color)
        img = Image.new("1", (self._width, self._height), 255 if color == 0xFF else 0)
        img.save(self._output_path)

    def display_full(self, image: Image.Image) -> None:
        logger.info("[MockDisplay] Full display refresh")
        image.save(self._output_path)

    def display_partial(self, image: Image.Image) -> None:
        logger.info("[MockDisplay] Partial display refresh")
        image.save(self._output_path)

    def sleep(self) -> None:
        logger.info("[MockDisplay] Deep sleep activated")
        self._is_sleeping = True

