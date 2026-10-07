"""Base display driver interface for E-Paper displays.
"""

from abc import ABC, abstractmethod
from PIL import Image


class BaseDisplayDriver(ABC):
    """Abstract base class for E-Paper display drivers."""

    @property
    @abstractmethod
    def width(self) -> int:
        """Physical display width in pixels."""
        pass

    @property
    @abstractmethod
    def height(self) -> int:
        """Physical display height in pixels."""
        pass

    @abstractmethod
    def init(self) -> None:
        """Initialize the display hardware for full refresh mode."""
        pass

    @abstractmethod
    def init_partial(self) -> None:
        """Initialize or prepare the display hardware for partial refresh mode."""
        pass

    @abstractmethod
    def clear(self, color: int = 0xFF) -> None:
        """Clear the display.
        
        Args:
            color: 0xFF for White, 0x00 for Black.
        """
        pass

    @abstractmethod
    def display_full(self, image: Image.Image) -> None:
        """Perform a full display update with the given PIL Image."""
        pass

    @abstractmethod
    def display_partial(self, image: Image.Image) -> None:
        """Perform a fast partial display update with the given PIL Image."""
        pass

    @abstractmethod
    def sleep(self) -> None:
        """Put display into low-power deep sleep mode."""
        pass

