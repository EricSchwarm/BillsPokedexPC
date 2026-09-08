"""Pre-converts the downloaded in-game sprites into the exact size, format,
and 1-bit black & white the e-ink display needs, so no image processing
happens on the Pi at render time.

Usage:
    python -m pokedex.prepare_eink_sprites

Reads sprites/games/<version>/<number>.png and writes the converted result
to sprites/eink/<version>/<number>.png, mirroring the same folder layout.
"""

from pathlib import Path

from PIL import Image

from config import EINK_SPRITES_DIR, SPRITES_DIR
from pokedex.sprite_convert import flatten_to_1bit, upscale_game_sprite

GAMES_DIR = SPRITES_DIR / "games"


def convert_one(src: Path, dest: Path) -> None:
    sprite = Image.open(src).convert("RGBA")
    sprite = upscale_game_sprite(sprite)
    bw = flatten_to_1bit(sprite)
    dest.parent.mkdir(parents=True, exist_ok=True)
    bw.save(dest)


def run() -> None:
    sources = sorted(GAMES_DIR.glob("*/*.png"))
    for i, src in enumerate(sources, start=1):
        version = src.parent.name
        dest = EINK_SPRITES_DIR / version / src.name
        convert_one(src, dest)
        print(f"[{i}/{len(sources)}] {version}/{src.name}")


if __name__ == "__main__":
    run()
