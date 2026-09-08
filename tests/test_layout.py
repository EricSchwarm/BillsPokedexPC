"""Tests for pokedex.ui.layout rendering."""

from config import DISPLAY_HEIGHT, DISPLAY_WIDTH
from pokedex.models import Pokemon
from pokedex.ui.layout import _load_sprite, render_entry

BULBASAUR = Pokemon(number=1, name="bulbasaur", generation=1, height=7, weight=69, genus="Seed Pokemon", types=["grass", "poison"])
CHIKORITA = Pokemon(number=152, name="chikorita", generation=2, height=9, weight=64, genus="Leaf Pokemon", types=["grass"])
NO_SPRITE = Pokemon(number=9999, name="missingno", generation=1, height=10, weight=10, genus="", types=["normal"])


def test_render_entry_produces_correct_size_and_mode():
    image = render_entry(BULBASAUR, "A strange seed was planted on its back at birth.", "red")

    assert image.size == (DISPLAY_WIDTH, DISPLAY_HEIGHT)
    assert image.mode == "1"


def test_render_entry_handles_single_type_pokemon():
    image = render_entry(CHIKORITA, "A friendly leaf sprouts from its head.", "gold")

    assert image.size == (DISPLAY_WIDTH, DISPLAY_HEIGHT)


def test_render_entry_handles_missing_sprite_file():
    image = render_entry(NO_SPRITE, "No data.", "red")

    assert image.size == (DISPLAY_WIDTH, DISPLAY_HEIGHT)


def test_render_entry_handles_no_version_selected():
    image = render_entry(BULBASAUR, "A strange seed was planted on its back at birth.", "")

    assert image.size == (DISPLAY_WIDTH, DISPLAY_HEIGHT)


def test_load_sprite_prefers_game_specific_sprite_and_upscales_crisply():
    sprite = _load_sprite(1, "red")

    assert sprite is not None
    assert sprite.size == (80, 80)  # native in-game sprite is 40x40, upscaled 2x


def test_load_sprite_falls_back_to_official_artwork_when_game_sprite_missing():
    sprite = _load_sprite(1, "nonexistent-version")

    assert sprite is not None
    assert sprite.size[0] <= 80 and sprite.size[1] <= 80


def test_load_sprite_returns_none_when_nothing_available():
    assert _load_sprite(9999, "red") is None
