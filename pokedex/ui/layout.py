"""Renders a Pokemon dex entry to a 264x176 1-bit image for the e-ink display."""

from PIL import Image, ImageDraw, ImageFont

from config import DISPLAY_HEIGHT, DISPLAY_WIDTH, FONT_PATH, SPRITES_DIR
from pokedex.models import Pokemon

SPRITE_BOX = (88, 88)
SPRITE_POSITION = (DISPLAY_WIDTH - SPRITE_BOX[0] - 4, 2)

_TITLE_FONT = ImageFont.truetype(str(FONT_PATH), 12)
_BODY_FONT = ImageFont.truetype(str(FONT_PATH), 8)


def render_entry(pokemon: Pokemon, flavor_text: str, version: str) -> Image.Image:
    image = Image.new("1", (DISPLAY_WIDTH, DISPLAY_HEIGHT), color=1)
    draw = ImageDraw.Draw(image)

    draw.text((4, 2), f"#{pokemon.number:03d} {pokemon.name.upper()}", font=_TITLE_FONT, fill=0)
    draw.text((4, 20), "/".join(t.upper() for t in pokemon.types), font=_BODY_FONT, fill=0)

    height_ft, height_in = _decimeters_to_feet_inches(pokemon.height)
    weight_lb = _hectograms_to_pounds(pokemon.weight)
    draw.text((4, 32), f"HT {height_ft}'{height_in:02d}\"", font=_BODY_FONT, fill=0)
    draw.text((4, 44), f"WT {weight_lb:.1f} LB", font=_BODY_FONT, fill=0)

    sprite = _load_sprite(pokemon.number)
    if sprite is not None:
        image.paste(sprite, SPRITE_POSITION)

    draw.text((4, 96), f"[{version.upper()}]", font=_BODY_FONT, fill=0)
    _draw_wrapped_text(draw, flavor_text, (4, 108), DISPLAY_WIDTH - 8, _BODY_FONT)

    return image


def _load_sprite(number: int) -> Image.Image | None:
    path = SPRITES_DIR / f"{number:03d}.png"
    if not path.exists():
        return None
    sprite = Image.open(path).convert("RGBA")
    flattened = Image.alpha_composite(Image.new("RGBA", sprite.size, (255, 255, 255, 255)), sprite)
    flattened = flattened.convert("L")
    flattened.thumbnail(SPRITE_BOX)
    return flattened.convert("1", dither=Image.FLOYDSTEINBERG)


def _decimeters_to_feet_inches(decimeters: int) -> tuple[int, int]:
    total_inches = round(decimeters * 10 / 2.54)
    return divmod(total_inches, 12)


def _hectograms_to_pounds(hectograms: int) -> float:
    return hectograms * 0.1 * 2.20462


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
