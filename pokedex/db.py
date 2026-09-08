"""SQLite storage and queries for the offline Pokedex data."""

import sqlite3
from pathlib import Path

from config import DB_PATH
from pokedex.models import Pokemon

SCHEMA = """
CREATE TABLE IF NOT EXISTS pokemon (
    number INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    generation INTEGER NOT NULL,
    height INTEGER NOT NULL,
    weight INTEGER NOT NULL,
    flavor_synced INTEGER NOT NULL DEFAULT 0,
    game_sprites_synced INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS pokemon_types (
    number INTEGER NOT NULL REFERENCES pokemon(number),
    slot INTEGER NOT NULL,
    type_name TEXT NOT NULL,
    PRIMARY KEY (number, slot)
);

CREATE TABLE IF NOT EXISTS flavor_text (
    number INTEGER NOT NULL REFERENCES pokemon(number),
    version TEXT NOT NULL,
    text TEXT NOT NULL,
    PRIMARY KEY (number, version)
);
"""


def connect(db_path: Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    _ensure_column(conn, "pokemon", "game_sprites_synced", "INTEGER NOT NULL DEFAULT 0")
    conn.commit()


def _ensure_column(conn: sqlite3.Connection, table: str, column: str, column_type: str) -> None:
    existing = {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}
    if column not in existing:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}")


def upsert_core(
    conn: sqlite3.Connection,
    number: int,
    name: str,
    generation: int,
    height: int,
    weight: int,
    types: list[str],
) -> None:
    conn.execute(
        """
        INSERT INTO pokemon (number, name, generation, height, weight)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(number) DO UPDATE SET
            name = excluded.name,
            generation = excluded.generation,
            height = excluded.height,
            weight = excluded.weight
        """,
        (number, name, generation, height, weight),
    )
    conn.execute("DELETE FROM pokemon_types WHERE number = ?", (number,))
    conn.executemany(
        "INSERT INTO pokemon_types (number, slot, type_name) VALUES (?, ?, ?)",
        [(number, slot, type_name) for slot, type_name in enumerate(types, start=1)],
    )
    conn.commit()


def upsert_flavor_text(conn: sqlite3.Connection, number: int, version: str, text: str) -> None:
    conn.execute(
        """
        INSERT INTO flavor_text (number, version, text)
        VALUES (?, ?, ?)
        ON CONFLICT(number, version) DO UPDATE SET text = excluded.text
        """,
        (number, version, text),
    )
    conn.commit()


def mark_flavor_synced(conn: sqlite3.Connection, number: int) -> None:
    conn.execute("UPDATE pokemon SET flavor_synced = 1 WHERE number = ?", (number,))
    conn.commit()


def is_flavor_synced(conn: sqlite3.Connection, number: int) -> bool:
    row = conn.execute("SELECT flavor_synced FROM pokemon WHERE number = ?", (number,)).fetchone()
    return bool(row and row[0])


def mark_game_sprites_synced(conn: sqlite3.Connection, number: int) -> None:
    conn.execute("UPDATE pokemon SET game_sprites_synced = 1 WHERE number = ?", (number,))
    conn.commit()


def is_game_sprites_synced(conn: sqlite3.Connection, number: int) -> bool:
    row = conn.execute("SELECT game_sprites_synced FROM pokemon WHERE number = ?", (number,)).fetchone()
    return bool(row and row[0])


def get_by_number(conn: sqlite3.Connection, number: int) -> Pokemon | None:
    row = conn.execute(
        "SELECT number, name, generation, height, weight FROM pokemon WHERE number = ?",
        (number,),
    ).fetchone()
    if row is None:
        return None
    types = [
        r[0]
        for r in conn.execute(
            "SELECT type_name FROM pokemon_types WHERE number = ? ORDER BY slot",
            (number,),
        )
    ]
    return Pokemon(
        number=row[0],
        name=row[1],
        generation=row[2],
        height=row[3],
        weight=row[4],
        types=types,
    )


def get_flavor_text(conn: sqlite3.Connection, number: int, version: str) -> str | None:
    row = conn.execute(
        "SELECT text FROM flavor_text WHERE number = ? AND version = ?",
        (number, version),
    ).fetchone()
    return row[0] if row else None


def list_by_generation(conn: sqlite3.Connection, generation: int) -> list[Pokemon]:
    numbers = [
        r[0]
        for r in conn.execute(
            "SELECT number FROM pokemon WHERE generation = ? ORDER BY number",
            (generation,),
        )
    ]
    return [get_by_number(conn, n) for n in numbers]
