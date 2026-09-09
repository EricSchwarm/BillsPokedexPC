"""Tests for the PokedexApp state machine, using fake display/input doubles.

The real WaveshareDriver and GpioButtonInput require SPI/GPIO hardware and
can't be imported off a Raspberry Pi, so these fakes stand in for them.
"""

import sqlite3

import pytest

from pokedex import db
from pokedex.app import NATIONAL_DEX_END, NATIONAL_DEX_START, PokedexApp
from pokedex.display.base import DisplayDriver
from pokedex.input.base import Button, ButtonInput
from pokedex.ui.layout import render_home_screen


class FakeDisplay(DisplayDriver):
    def __init__(self):
        self.frames = []
        self.clear_count = 0

    def draw(self, image):
        self.frames.append(image)

    def clear(self):
        self.clear_count += 1

    def sleep(self):
        pass


class FakeButtonInput(ButtonInput):
    def __init__(self):
        self._callbacks = {}

    def on_press(self, button, callback):
        self._callbacks[button] = callback

    def close(self):
        pass

    def press(self, button):
        self._callbacks[button]()


@pytest.fixture
def conn():
    connection = sqlite3.connect(":memory:")
    db.init_db(connection)

    # Bulbasaur: available in red/blue, gold/silver (via gold only), and
    # crystal, but not yellow -> exercises cycling across three groups
    # while skipping an unavailable one.
    db.upsert_core(connection, number=1, name="bulbasaur", generation=1, height=7, weight=69, types=["grass", "poison"])
    db.upsert_flavor_text(connection, 1, "red", "Bulbasaur red text.", "Bulbasaur\nred text.")
    db.upsert_flavor_text(connection, 1, "blue", "Bulbasaur blue text.", "Bulbasaur\nblue text.")
    db.upsert_flavor_text(connection, 1, "gold", "Bulbasaur gold text.", "Bulbasaur\ngold text.")
    db.upsert_flavor_text(connection, 1, "crystal", "Bulbasaur crystal text.", "Bulbasaur\ncrystal text.")
    db.mark_flavor_synced(connection, 1)

    db.upsert_core(connection, number=2, name="ivysaur", generation=1, height=10, weight=130, types=["grass", "poison"])
    db.upsert_flavor_text(connection, 2, "yellow", "Ivysaur yellow text.", "Ivysaur\nyellow text.")
    db.mark_flavor_synced(connection, 2)

    # Chikorita: silver only, no gold -> exercises the gold/silver group
    # falling back to its second member.
    db.upsert_core(connection, number=152, name="chikorita", generation=2, height=9, weight=64, types=["grass"])
    db.upsert_flavor_text(connection, 152, "silver", "Chikorita silver text.", "Chikorita\nsilver text.")
    db.mark_flavor_synced(connection, 152)

    db.upsert_core(connection, number=NATIONAL_DEX_END, name="celebi", generation=2, height=6, weight=50, types=["psychic", "grass"])
    db.mark_flavor_synced(connection, NATIONAL_DEX_END)

    yield connection
    connection.close()


def make_app(conn, skip_home=True):
    display = FakeDisplay()
    button_input = FakeButtonInput()
    app = PokedexApp(conn, display, button_input)
    if skip_home:
        app._showing_home = False
    return app, display, button_input


def test_start_renders_first_pokemon(conn):
    app, display, _ = make_app(conn)

    app.start()

    assert app.current_number == NATIONAL_DEX_START
    assert len(display.frames) == 1


def test_next_advances_and_wraps_at_end(conn):
    app, display, buttons = make_app(conn)
    app.start()

    app._number = NATIONAL_DEX_END
    buttons.press(Button.NEXT)

    assert app.current_number == NATIONAL_DEX_START
    assert len(display.frames) == 2


def test_previous_wraps_at_start(conn):
    app, display, buttons = make_app(conn)
    app.start()

    buttons.press(Button.PREV)

    assert app.current_number == NATIONAL_DEX_END


def test_random_jumps_to_a_valid_number_and_rerenders(conn, monkeypatch):
    app, display, buttons = make_app(conn)
    app.start()
    frame_count = len(display.frames)
    monkeypatch.setattr("pokedex.app.random.randint", lambda lo, hi: 2)

    buttons.press(Button.RANDOM)

    assert app.current_number == 2
    assert len(display.frames) == frame_count + 1


def test_version_cycles_through_available_groups_only(conn):
    app, _, buttons = make_app(conn)
    app.start()

    assert app.current_version == "red"

    buttons.press(Button.VERSION)  # yellow group unavailable, skipped
    assert app.current_version == "gold"

    buttons.press(Button.VERSION)
    assert app.current_version == "crystal"

    buttons.press(Button.VERSION)
    assert app.current_version == "red"


def test_gold_silver_group_falls_back_to_silver_when_gold_missing(conn):
    app, _, buttons = make_app(conn)
    app._number = 152
    app.start()

    assert app.current_version == "silver"


def test_version_cycle_noop_when_no_flavor_text_available(conn):
    app, display, buttons = make_app(conn)
    app._number = NATIONAL_DEX_END
    app.start()
    frame_count = len(display.frames)

    assert app.current_version is None

    buttons.press(Button.VERSION)

    assert len(display.frames) == frame_count


def test_changing_pokemon_resets_version_to_first_available(conn):
    app, _, buttons = make_app(conn)
    app.start()
    buttons.press(Button.VERSION)
    assert app.current_version == "gold"

    buttons.press(Button.NEXT)

    assert app.current_number == 2
    assert app.current_version == "yellow"


def test_start_shows_home_screen(conn):
    app, display, _ = make_app(conn, skip_home=False)

    app.start()

    assert len(display.frames) == 1
    assert list(display.frames[0].getdata()) == list(render_home_screen().getdata())


def test_first_button_press_dismisses_home_without_performing_its_action(conn):
    app, display, buttons = make_app(conn, skip_home=False)
    app.start()

    buttons.press(Button.NEXT)

    assert app.current_number == NATIONAL_DEX_START  # consumed by dismissing home, not advanced
    assert len(display.frames) == 2
    assert list(display.frames[1].getdata()) != list(render_home_screen().getdata())


def test_second_button_press_behaves_normally_after_home_dismissed(conn):
    app, display, buttons = make_app(conn, skip_home=False)
    app.start()
    buttons.press(Button.NEXT)  # dismisses home

    buttons.press(Button.NEXT)  # now a real "next"

    assert app.current_number == 2
