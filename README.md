# Bill's Pokedex PC

Offline Pokedex slideshow for a Raspberry Pi 3B+ with a Waveshare 2.7" e-ink HAT
(264x176, 1-bit B/W, 4 buttons on BCM 5/6/13/19).

## Layout

- `pokedex/db.py`, `pokedex/models.py`, `pokedex/fetch.py` — offline SQLite dataset and its downloader.
- `pokedex/display/` — `DisplayDriver` interface plus the Waveshare epd2in7_V2 wrapper (Pi-only; vendored driver in `display/vendor/`).
- `pokedex/input/` — `ButtonInput` interface plus the gpiozero implementation for the onboard buttons (Pi-only).
- `pokedex/ui/layout.py` — renders a dex entry to a 264x176 1-bit image.
- `pokedex/app.py` / `main.py` — state machine and entry point wiring it all together.
- `systemd/pokedex.service` — autostart unit for the Pi.

## Setup

    pip install -r requirements-dev.txt      # laptop: requests + pytest, for fetching/testing
    pip install -r requirements.txt          # both: Pillow
    pip install -r requirements-hardware.txt # Pi only: gpiozero, lgpio, spidev

## Fetch the offline dataset

    python -m pokedex.fetch

Populates, per Pokemon (national dex #1-251, Gen 1 + Gen 2):

- `pokedex.db` — name, types, height/weight, genus (e.g. "Seed Pokemon"), and
  English flavor text per game version, stored two ways: `text` is
  whitespace-collapsed for wrapping to the display width, `raw_text` preserves
  the original in-game line breaks (`\n`) and page breaks (`\x0c`, the
  Gen I/II games' "press a button for more" prompt).
- `sprites/<number>.png` — official artwork.
- `sprites/games/<version>/<number>.png` — the original in-game sprite for each
  of the 6 games (red, blue, yellow, gold, silver, crystal). Red/Blue/Yellow
  use the grayscale sprite (the pixel-accurate rendering for the original
  monochrome Game Boy); Gold/Silver/Crystal use the full-color sprite (Game
  Boy Color titles were genuinely in color). Not every Pokemon has all 6 —
  Gen 2 Pokemon didn't exist yet in Red/Blue/Yellow.

Safe to interrupt (Ctrl+C) and re-run — already-synced entries are skipped.
Use `--force` to re-fetch everything from scratch.

## Run tests

    pytest

## Running the slideshow

    python main.py

Displays one Pokemon at a time. Buttons (BCM 5/6/13/19, HAT-labeled 1-4):

- **Button 1** — next Pokemon
- **Button 2** — previous Pokemon
- **Button 3** — random Pokemon
- **Button 4** — cycle the game version shown, among whichever of
  Red/Blue, Yellow, Gold/Silver, and Crystal actually exist for that
  Pokemon. Red/Blue always share identical text, so there's no ambiguity
  there; Gold and Silver differ for every entry, and that stop shows
  Gold's text.

## Deploying to the Pi

Enable SPI via `raspi-config`, confirm the `pi` user is in the `spi`/`gpio`
groups, `git pull` this repo, install `requirements.txt` +
`requirements-hardware.txt`, then install `systemd/pokedex.service`.

If your HAT is the older V1 panel revision, swap the import in
`pokedex/display/waveshare_driver.py` from `epd2in7_V2` to `epd2in7`.
