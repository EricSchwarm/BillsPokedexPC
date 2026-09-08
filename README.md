# Bill's Pokedex PC

Offline Pokedex slideshow for a Raspberry Pi 3B+ with a Waveshare 2.7" e-ink HAT
(264x176, 1-bit B/W, 4 buttons on BCM 5/6/13/19).

## Current status

Data layer only: SQLite DB + sprite downloader covering national dex #1-251
(Gen 1 + Gen 2). Display/input/UI code not yet implemented.

## Setup

    pip install -r requirements-dev.txt

## Fetch the offline dataset

    python -m pokedex.fetch

Populates `pokedex.db` and `sprites/<number>.png` from PokeAPI. Safe to
interrupt (Ctrl+C) and re-run — already-synced entries are skipped. Use
`--force` to re-fetch everything from scratch.

## Run tests

    pytest
