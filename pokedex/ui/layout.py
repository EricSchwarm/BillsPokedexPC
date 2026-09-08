"""Renders a Pokemon dex entry to a 264x176 1-bit image for the e-ink display.

Page layout: name + number centered at the top, the Pokemon's sprite
centered in the middle, and the brief in-game dex description wrapped at
the bottom.
"""

from PIL import Image, ImageDraw, ImageFont

from config import DISPLAY_HEIGHT, DISPLAY_WIDTH, EINK_SPRITES_DIR, FONT_PATH, SPRITES_DIR
from pokedex.models import Pokemon
from pokedex.sprite_convert import flatten_to_1bit

ARTWORK_SPRITE_BOX = (80, 80)
SPRITE_TOP = 24
DESCRIPTION_TOP = 112

_TITLE_FONT = ImageFont.truetype(str(FONT_PATH), 14)
_BODY_FONT = ImageFont.truetype(str(FONT_PATH), 8)


def render_entry(pokemon: Pokemon, flavor_text: str, version: str) -> Image.Image:
    image = Image.new("1", (DISPLAY_WIDTH, DISPLAY_HEIGHT), color=1)
    draw = ImageDraw.Draw(image)

    header = f"#{pokemon.number:03d} {pokemon.name.upper()}"
    header_width = draw.textlength(header, font=_TITLE_FONT)
    draw.text(((DISPLAY_WIDTH - header_width) / 2, 4), header, font=_TITLE_FONT, fill=0)

    sprite = _load_sprite(pokemon.number, version)
    if sprite is not None:
        x = (DISPLAY_WIDTH - sprite.width) // 2
        image.paste(sprite, (x, SPRITE_TOP))

    _draw_wrapped_text(draw, flavor_text, (4, DESCRIPTION_TOP), DISPLAY_WIDTH - 8, _BODY_FONT)

    return image


def _load_sprite(number: int, version: str) -> Image.Image | None:
    eink_path = EINK_SPRITES_DIR / version / f"{number:03d}.png" if version else None
    if eink_path is not None and eink_path.exists():
        return Image.open(eink_path)

    # Rare fallback (e.g. a version whose sprite hasn't been pre-converted yet):
    # build a 1-bit sprite on the fly from the official artwork.
    artwork_path = SPRITES_DIR / f"{number:03d}.png"
    if artwork_path.exists():
        sprite = Image.open(artwork_path).convert("RGBA")
        sprite.thumbnail(ARTWORK_SPRITE_BOX, Image.LANCZOS)
        return flatten_to_1bit(sprite)

    return None


def _draw_wrapped_text(draw: ImageDraw.ImageDraw, text: str, position: tuple[int, int], max_width: int, font) -> None:
    lines = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=font) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)

    x, y = position
    line_height = font.size + 2
    for line in lines:
        draw.text((x, y), line, font=font, fill=0)
        y += line_height
