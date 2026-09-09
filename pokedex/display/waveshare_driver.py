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
        # The HAT is mounted in portrait; rotate the 264x176 landscape canvas
        # to match. Empirically tuning this: ROTATE_90/ROTATE_270 change the
        # image's dimensions (264x176 -> 176x264), which switches which
        # orientation branch getbuffer() takes internally, so the resulting
        # rotation direction doesn't follow simply from the panel's raw pixel
        # geometry. ROTATE_180 keeps the same 264x176 shape, staying on
        # getbuffer()'s other branch instead.
        rotated = image.transpose(Image.ROTATE_180)
        self._epd.display(self._epd.getbuffer(rotated))

    def clear(self) -> None:
        self._epd.Clear()

    def sleep(self) -> None:
        self._epd.sleep()
