"""Resumable downloader that populates the offline Pokedex DB and sprite folders.

Usage:
    python -m pokedex.fetch [--force]

Downloads, per Pokemon: core data + official artwork (sprites/<n>.png),
English flavor text per game version, and the original in-game sprite for
each of the 6 games (sprites/games/<version>/<n>.png).

Safe to interrupt (Ctrl+C) and re-run: each of the 251 entries is checked
independently and only the missing pieces are re-fetched.
"""

from __future__ import annotations

import argparse
import re
import sys
import time
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import DB_PATH, SPRITES_DIR
from pokedex import db

API_BASE = "https://pokeapi.co/api/v2"
NATIONAL_DEX_START = 1
NATIONAL_DEX_END = 251  # inclusive: Gen 1 + Gen 2
VERSIONS = {"red", "blue", "yellow", "gold", "silver", "crystal"}
REQUEST_DELAY_SECONDS = 0.1

GAME_SPRITES_DIR = SPRITES_DIR / "games"

# Red/Blue/Yellow ran on the original monochrome Game Boy, so "front_gray" is
# the pixel-accurate in-game rendering; PokeAPI's "front_default" for those
# three is a stylized green recolor, not what actually displayed on hardware.
# Gold/Silver/Crystal ran on Game Boy Color and were genuinely full color, so
# "front_default" is correct there.
GAME_SPRITE_SOURCES = {
    "red": ("generation-i", "red-blue", "front_gray"),
    "blue": ("generation-i", "red-blue", "front_gray"),
    "yellow": ("generation-i", "yellow", "front_gray"),
    "gold": ("generation-ii", "gold", "front_default"),
    "silver": ("generation-ii", "silver", "front_default"),
    "crystal": ("generation-ii", "crystal", "front_default"),
}


def generation_for(number: int) -> int:
    return 1 if number <= 151 else 2


def sprite_path(number: int) -> Path:
    return SPRITES_DIR / f"{number:03d}.png"


def game_sprite_path(version: str, number: int) -> Path:
    return GAME_SPRITES_DIR / version / f"{number:03d}.png"


def build_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=5,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def clean_flavor_text(raw: str) -> str:
    return re.sub(r"\s+", " ", raw.replace("\f", " ")).strip()


def download_sprite(session: requests.Session, url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    response = session.get(url, timeout=15)
    response.raise_for_status()
    tmp = dest.with_suffix(".tmp")
    tmp.write_bytes(response.content)
    tmp.replace(dest)  # atomic, and overwrites on Windows unlike Path.rename


def sync_core(session: requests.Session, conn, number: int) -> dict:
    data = session.get(f"{API_BASE}/pokemon/{number}", timeout=15).json()
    types = [t["type"]["name"] for t in sorted(data["types"], key=lambda t: t["slot"])]
    db.upsert_core(
        conn,
        number=number,
        name=data["name"],
        generation=generation_for(number),
        height=data["height"],
        weight=data["weight"],
        types=types,
    )

    dest = sprite_path(number)
    if not dest.exists() or dest.stat().st_size == 0:
        url = data["sprites"]["other"]["official-artwork"]["front_default"]
        if url:
            download_sprite(session, url, dest)

    return data


def sync_game_sprites(session: requests.Session, conn, number: int, pokemon_data: dict | None = None) -> None:
    data = pokemon_data or session.get(f"{API_BASE}/pokemon/{number}", timeout=15).json()
    versions = data["sprites"]["versions"]
    for version, (gen_key, game_key, field) in GAME_SPRITE_SOURCES.items():
        dest = game_sprite_path(version, number)
        if dest.exists() and dest.stat().st_size > 0:
            continue
        url = versions.get(gen_key, {}).get(game_key, {}).get(field)
        if url:  # absent for e.g. red/blue/yellow on Gen 2 Pokemon, which didn't exist yet
            download_sprite(session, url, dest)
    db.mark_game_sprites_synced(conn, number)


def sync_flavor_text(session: requests.Session, conn, number: int) -> None:
    data = session.get(f"{API_BASE}/pokemon-species/{number}", timeout=15).json()
    seen = set()
    for entry in data["flavor_text_entries"]:
        version = entry["version"]["name"]
        language = entry["language"]["name"]
        if language != "en" or version not in VERSIONS or version in seen:
            continue  # PokeAPI has duplicate entries per version; first one wins
        seen.add(version)
        db.upsert_flavor_text(conn, number, version, clean_flavor_text(entry["flavor_text"]))
    db.mark_flavor_synced(conn, number)


def run(force: bool = False) -> None:
    conn = db.connect(DB_PATH)
    db.init_db(conn)
    session = build_session()

    for number in range(NATIONAL_DEX_START, NATIONAL_DEX_END + 1):
        needs_core = force or db.get_by_number(conn, number) is None or not sprite_path(number).exists()
        needs_flavor = force or not db.is_flavor_synced(conn, number)
        needs_game_sprites = force or not db.is_game_sprites_synced(conn, number)

        if not needs_core and not needs_flavor and not needs_game_sprites:
            print(f"[{number:03d}/{NATIONAL_DEX_END}] already synced, skipping")
            continue

        try:
            pokemon_data = None
            if needs_core:
                pokemon_data = sync_core(session, conn, number)
                time.sleep(REQUEST_DELAY_SECONDS)
            if needs_flavor:
                sync_flavor_text(session, conn, number)
                time.sleep(REQUEST_DELAY_SECONDS)
            if needs_game_sprites:
                sync_game_sprites(session, conn, number, pokemon_data)
                time.sleep(REQUEST_DELAY_SECONDS)
        except requests.RequestException as exc:
            print(f"[{number:03d}/{NATIONAL_DEX_END}] FAILED: {exc}", file=sys.stderr)
            continue

        print(f"[{number:03d}/{NATIONAL_DEX_END}] synced")

    conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch Gen 1+2 Pokemon data into the offline DB.")
    parser.add_argument("--force", action="store_true", help="Re-fetch everything, ignoring existing data.")
    args = parser.parse_args()
    run(force=args.force)


if __name__ == "__main__":
    main()
