"""Main application state machine: Pokemon index + game-version navigation."""

import sqlite3

from pokedex import db
from pokedex.display.base import DisplayDriver
from pokedex.input.base import Button, ButtonInput
from pokedex.ui.layout import render_entry

NATIONAL_DEX_START = 1
NATIONAL_DEX_END = 251
GAME_VERSIONS = ["red", "blue", "yellow", "gold", "silver", "crystal"]


class PokedexApp:
    def __init__(self, conn: sqlite3.Connection, display: DisplayDriver, button_input: ButtonInput):
        self._conn = conn
        self._display = display
        self._input = button_input
        self._number = NATIONAL_DEX_START
        self._version_index = 0

        self._input.on_press(Button.PREV, self._show_previous)
        self._input.on_press(Button.NEXT, self._show_next)
        self._input.on_press(Button.VERSION, self._cycle_version)
        self._input.on_press(Button.REFRESH, self._force_refresh)

    @property
    def current_number(self) -> int:
        return self._number

    @property
    def current_version(self) -> str | None:
        available = self._available_versions()
        return available[self._version_index % len(available)] if available else None

    def start(self) -> None:
        self._render()

    def _show_previous(self) -> None:
        self._number = self._number - 1 if self._number > NATIONAL_DEX_START else NATIONAL_DEX_END
        self._version_index = 0
        self._render()

    def _show_next(self) -> None:
        self._number = self._number + 1 if self._number < NATIONAL_DEX_END else NATIONAL_DEX_START
        self._version_index = 0
        self._render()

    def _cycle_version(self) -> None:
        available = self._available_versions()
        if not available:
            return
        self._version_index = (self._version_index + 1) % len(available)
        self._render()

    def _force_refresh(self) -> None:
        self._display.clear()
        self._render()

    def _available_versions(self) -> list[str]:
        return [v for v in GAME_VERSIONS if db.get_flavor_text(self._conn, self._number, v) is not None]

    def _render(self) -> None:
        pokemon = db.get_by_number(self._conn, self._number)
        version = self.current_version
        flavor_text = db.get_flavor_text(self._conn, self._number, version) if version else ""
        image = render_entry(pokemon, flavor_text, version or "")
        self._display.draw(image)
