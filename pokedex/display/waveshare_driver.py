"""DisplayDriver backed by Waveshare's vendored epd2in7_V2 panel driver.

Pi-only: the vendored driver imports spidev/gpiozero and reads /proc/cpuinfo
at import time, so this module cannot be imported off a Raspberry Pi. If your
HAT is the older V1 panel revision, swap the import below for
``pokedex.display.vendor.epd2in7`` instead (same public API).
"""

from PIL import Image

from pokedex.display.base import DisplayDriver
from pokedex.display.vendor import epd2in7_V2


class WaveshareDriver(DisplayDriver):
    def __init__(self):
        self._epd = epd2in7_V2.EPD()
        self._epd.init()
        self._epd.Clear()

    def draw(self, image: Image.Image) -> None:
        self._epd.display(self._epd.getbuffer(image))

    def clear(self) -> None:
        self._epd.Clear()

    def sleep(self) -> None:
        self._epd.sleep()
