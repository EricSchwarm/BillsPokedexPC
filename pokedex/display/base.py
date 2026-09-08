"""Abstract interface for the e-ink display driver."""

from abc import ABC, abstractmethod

from PIL import Image


class DisplayDriver(ABC):
    @abstractmethod
    def draw(self, image: Image.Image) -> None:
        """Render a 264x176 image to the display."""

    @abstractmethod
    def clear(self) -> None:
        """Clear the display to white (also eliminates e-ink ghosting)."""

    @abstractmethod
    def sleep(self) -> None:
        """Put the panel into low-power sleep and release SPI/GPIO resources."""
