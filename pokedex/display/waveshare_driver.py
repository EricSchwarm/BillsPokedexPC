"""DisplayDriver backed by Waveshare's vendored epd2in7 (V1) panel driver.

Pi-only: the vendored driver imports spidev/gpiozero and reads /proc/cpuinfo
at import time, so this module cannot be imported off a Raspberry Pi. V1 and
V2 panels use inverted BUSY-pin polarity, so using the wrong one hangs
forever on the very first busy-wait rather than failing loudly. If your HAT
turns out to be a newer V2 panel, swap the import below for
``pokedex.display.vendor.epd2in7_V2`` instead (same public API).
"""

from PIL import Image

from pokedex.display.base import DisplayDriver
from pokedex.display.vendor import epd2in7


class WaveshareDriver(DisplayDriver):
    def __init__(self):
        self._epd = epd2in7.EPD()
        self._epd.init()
        self._epd.Clear()

    def draw(self, image: Image.Image) -> None:
        self._epd.display(self._epd.getbuffer(image))

    def clear(self) -> None:
        self._epd.Clear()

    def sleep(self) -> None:
        self._epd.sleep()
