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
    db.upsert_flavor_text(conn, 1, "red", "A strange seed was planted on its back at birth.")

    assert db.get_flavor_text(conn, 1, "red") == "A strange seed was planted on its back at birth."


def test_get_flavor_text_missing_version_returns_none(conn):
    db.upsert_core(conn, number=1, name="bulbasaur", generation=1, height=7, weight=69, types=["grass", "poison"])
    db.upsert_flavor_text(conn, 1, "red", "Some text.")

    assert db.get_flavor_text(conn, 1, "gold") is None


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
