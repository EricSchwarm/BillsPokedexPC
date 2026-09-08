"""ButtonInput backed by gpiozero, wired to the HAT's onboard buttons.

Pi-only: gpiozero requires a real GPIO backend (lgpio on Trixie) to construct
a Button, so this module cannot be used off a Raspberry Pi.
"""

from typing import Callable

from gpiozero import Button as GPIOButton

from config import (
    BUTTON_NEXT_PIN,
    BUTTON_PREV_PIN,
    BUTTON_REFRESH_PIN,
    BUTTON_VERSION_PIN,
)
from pokedex.input.base import Button, ButtonInput

_PIN_BY_BUTTON = {
    Button.PREV: BUTTON_PREV_PIN,
    Button.NEXT: BUTTON_NEXT_PIN,
    Button.VERSION: BUTTON_VERSION_PIN,
    Button.REFRESH: BUTTON_REFRESH_PIN,
}


class GpioButtonInput(ButtonInput):
    def __init__(self):
        self._buttons = {
            button: GPIOButton(pin, pull_up=True, bounce_time=0.05)
            for button, pin in _PIN_BY_BUTTON.items()
        }

    def on_press(self, button: Button, callback: Callable[[], None]) -> None:
        self._buttons[button].when_pressed = callback

    def close(self) -> None:
        for gpio_button in self._buttons.values():
            gpio_button.close()
