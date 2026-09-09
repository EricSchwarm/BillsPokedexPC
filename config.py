"""Shared paths and hardware constants for the Pokedex project."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "pokedex.db"
SPRITES_DIR = BASE_DIR / "sprites"
EINK_SPRITES_DIR = SPRITES_DIR / "eink"
FONT_PATH = BASE_DIR / "pokedex" / "assets" / "fonts" / "PressStart2P-Regular.ttf"

# Waveshare 2.7" e-ink HAT, native portrait orientation (panel's own pixel grid).
DISPLAY_WIDTH = 176
DISPLAY_HEIGHT = 264

# Onboard buttons, BCM numbering: button 1/2/3/4 on the HAT.
BUTTON_NEXT_PIN = 5
BUTTON_PREV_PIN = 6
BUTTON_RANDOM_PIN = 13
BUTTON_VERSION_PIN = 19
