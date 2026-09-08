"""Tests for pokedex.db query functions."""

import sqlite3

import pytest

from pokedex import db


@pytest.fixture
def conn():
    connection = sqlite3.connect(":memory:")
    db.init_db(connection)
    yield connection
    connection.close()


def test_get_by_number_returns_pokemon(conn):
    db.upsert_core(conn, number=1, name="bulbasaur", generation=1, height=7, weight=69, types=["grass", "poison"])

    result = db.get_by_number(conn, 1)

    assert result.number == 1
    assert result.name == "bulbasaur"
    assert result.generation == 1
    assert result.height == 7
    assert result.weight == 69
    assert result.types == ["grass", "poison"]


def test_get_by_number_missing_returns_none(conn):
    assert db.get_by_number(conn, 999) is None


def test_get_flavor_text_returns_text_for_version(conn):
    db.upsert_core(conn, number=1, name="bulbasaur", generation=1, height=7, weight=69, types=["grass", "poison"])
    db.upsert_flavor_text(conn, 1, "red", "cleaned text", "raw\ntext")

    assert db.get_flavor_text(conn, 1, "red") == "cleaned text"


def test_get_flavor_text_missing_version_returns_none(conn):
    db.upsert_core(conn, number=1, name="bulbasaur", generation=1, height=7, weight=69, types=["grass", "poison"])
    db.upsert_flavor_text(conn, 1, "red", "cleaned text", "raw\ntext")

    assert db.get_flavor_text(conn, 1, "gold") is None


def test_get_raw_flavor_text_preserves_original_formatting(conn):
    db.upsert_core(conn, number=1, name="bulbasaur", generation=1, height=7, weight=69, types=["grass", "poison"])
    db.upsert_flavor_text(conn, 1, "red", "cleaned text", "line one\nline two\x0cpage two")

    assert db.get_raw_flavor_text(conn, 1, "red") == "line one\nline two\x0cpage two"


def test_get_raw_flavor_text_missing_version_returns_none(conn):
    db.upsert_core(conn, number=1, name="bulbasaur", generation=1, height=7, weight=69, types=["grass", "poison"])

    assert db.get_raw_flavor_text(conn, 1, "gold") is None


def test_set_genus_updates_pokemon(conn):
    db.upsert_core(conn, number=1, name="bulbasaur", generation=1, height=7, weight=69, types=["grass", "poison"])

    db.set_genus(conn, 1, "Seed Pokemon")

    assert db.get_by_number(conn, 1).genus == "Seed Pokemon"


def test_list_by_generation_returns_only_matching_pokemon_sorted(conn):
    db.upsert_core(conn, number=2, name="ivysaur", generation=1, height=10, weight=130, types=["grass", "poison"])
    db.upsert_core(conn, number=152, name="chikorita", generation=2, height=9, weight=64, types=["grass"])
    db.upsert_core(conn, number=1, name="bulbasaur", generation=1, height=7, weight=69, types=["grass", "poison"])

    gen1 = db.list_by_generation(conn, 1)

    assert [p.number for p in gen1] == [1, 2]
    assert all(p.generation == 1 for p in gen1)


def test_list_by_generation_empty_returns_empty_list(conn):
    assert db.list_by_generation(conn, 1) == []


def test_flavor_synced_flag_defaults_false_then_true(conn):
    db.upsert_core(conn, number=1, name="bulbasaur", generation=1, height=7, weight=69, types=["grass"])

    assert db.is_flavor_synced(conn, 1) is False

    db.mark_flavor_synced(conn, 1)

    assert db.is_flavor_synced(conn, 1) is True


def test_game_sprites_synced_flag_defaults_false_then_true(conn):
    db.upsert_core(conn, number=1, name="bulbasaur", generation=1, height=7, weight=69, types=["grass"])

    assert db.is_game_sprites_synced(conn, 1) is False

    db.mark_game_sprites_synced(conn, 1)

    assert db.is_game_sprites_synced(conn, 1) is True
