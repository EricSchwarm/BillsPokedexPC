"""Main application state machine: Pokemon index + game-version navigation."""

import random
import sqlite3

from pokedex import db
from pokedex.display.base import DisplayDriver
from pokedex.input.base import Button, ButtonInput
from pokedex.ui.layout import render_entry, render_home_screen

NATIONAL_DEX_START = 1
NATIONAL_DEX_END = 251

# Each tuple is one "stop" for the version button. A group is available if
# any version in it has flavor text for the current Pokemon, and the first
# available member is the one shown. Red/Blue always share identical text;
# Gold/Silver do not (every entry differs) but are grouped as one stop here
# anyway, showing Gold's text.
GAME_GROUPS: list[tuple[str, ...]] = [
    ("red", "blue"),
    ("yellow",),
    ("gold", "silver"),
    ("crystal",),
]


class PokedexApp:
    def __init__(self, conn: sqlite3.Connection, display: DisplayDriver, button_input: ButtonInput):
        self._conn = conn
        self._display = display
        self._input = button_input
        self._number = NATIONAL_DEX_START
        self._group_index = 0
        self._showing_home = True

        self._input.on_press(Button.NEXT, self._show_next)
        self._input.on_press(Button.PREV, self._show_previous)
        self._input.on_press(Button.RANDOM, self._show_random)
        self._input.on_press(Button.VERSION, self._cycle_version)

    @property
    def current_number(self) -> int:
        return self._number

    @property
    def current_version(self) -> str | None:
        available = self._available_groups()
        if not available:
            return None
        group = available[self._group_index % len(available)]
        return self._first_synced_version(group)

    def start(self) -> None:
        self._render()

    def _show_next(self) -> None:
        if self._dismiss_home():
            return
        self._number = self._number + 1 if self._number < NATIONAL_DEX_END else NATIONAL_DEX_START
        self._group_index = 0
        self._render()

    def _show_previous(self) -> None:
        if self._dismiss_home():
            return
        self._number = self._number - 1 if self._number > NATIONAL_DEX_START else NATIONAL_DEX_END
        self._group_index = 0
        self._render()

    def _show_random(self) -> None:
        if self._dismiss_home():
            return
        self._number = random.randint(NATIONAL_DEX_START, NATIONAL_DEX_END)
        self._group_index = 0
        self._render()

    def _cycle_version(self) -> None:
        if self._dismiss_home():
            return
        available = self._available_groups()
        if not available:
            return
        self._group_index = (self._group_index + 1) % len(available)
        self._render()

    def _dismiss_home(self) -> bool:
        """First press of any button leaves the home screen without also
        performing that button's action; returns whether it did so."""
        if not self._showing_home:
            return False
        self._showing_home = False
        self._render()
        return True

    def _available_groups(self) -> list[tuple[str, ...]]:
        return [group for group in GAME_GROUPS if self._first_synced_version(group) is not None]

    def _first_synced_version(self, group: tuple[str, ...]) -> str | None:
        for version in group:
            if db.get_flavor_text(self._conn, self._number, version) is not None:
                return version
        return None

    def _render(self) -> None:
        if self._showing_home:
            self._display.draw(render_home_screen())
            return
        pokemon = db.get_by_number(self._conn, self._number)
        version = self.current_version
        flavor_text = db.get_flavor_text(self._conn, self._number, version) if version else ""
        image = render_entry(pokemon, flavor_text, version or "")
        self._display.draw(image)
