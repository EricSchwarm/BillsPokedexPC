"""Shared paths and hardware constants for the Pokedex project."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "pokedex.db"
SPRITES_DIR = BASE_DIR / "sprites"
FONT_PATH = BASE_DIR / "pokedex" / "assets" / "fonts" / "PressStart2P-Regular.ttf"

# Waveshare 2.7" e-ink HAT, landscape orientation.
DISPLAY_WIDTH = 264
DISPLAY_HEIGHT = 176

# Onboard buttons, BCM numbering.
BUTTON_PREV_PIN = 5
BUTTON_NEXT_PIN = 6
BUTTON_VERSION_PIN = 13
BUTTON_REFRESH_PIN = 19
