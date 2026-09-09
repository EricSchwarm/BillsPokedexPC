"""Renders a Pokemon dex entry to a 176x264 1-bit image for the e-ink display,
matching the panel's native portrait pixel grid.

Page layout: name + number centered at the top, the Pokemon's sprite
centered below it, and the brief in-game dex description wrapped at the
bottom.
"""

from PIL import Image, ImageDraw, ImageFont

from config import DISPLAY_HEIGHT, DISPLAY_WIDTH, EINK_SPRITES_DIR, FONT_PATH, SPRITES_DIR
from pokedex.models import Pokemon
from pokedex.sprite_convert import flatten_to_1bit

ARTWORK_SPRITE_BOX = (160, 160)
SPRITE_TOP = 20  # just clears the 12pt header, which ends around y=16
BOTTOM_MARGIN = 4
FOOTER_GAP = 2
POKEBALL_DIAMETER = 140

BOX_MARGIN = 4  # horizontal distance from the screen edges to the text box
BOX_PADDING = 4  # distance from the box border to the text inside it
BOX_BORDER_GAP = 2  # gap between the double border's outer and inner lines

_TITLE_FONT = ImageFont.truetype(str(FONT_PATH), 12)
# 6pt rather than 8pt: verified against every stored flavor text that this is
# the largest size that never overlaps the sprite at its current size/position
# for the longest entries (worst case needs 5 wrapped lines at this width).
_BODY_FONT = ImageFont.truetype(str(FONT_PATH), 6)


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

    footer_height = _line_height(draw, _BODY_FONT) if version else 0
    box_bottom = DISPLAY_HEIGHT - BOTTOM_MARGIN
    if version:
        box_bottom -= footer_height + FOOTER_GAP

    text_max_width = DISPLAY_WIDTH - 2 * (BOX_MARGIN + BOX_PADDING)
    lines = _wrap_lines(draw, flavor_text, text_max_width, _BODY_FONT)
    _draw_text_box(draw, lines, _BODY_FONT, box_bottom)

    if version:
        label = f"{version.upper()} VERSION"
        label_width = draw.textlength(label, font=_BODY_FONT)
        draw.text(((DISPLAY_WIDTH - label_width) / 2, DISPLAY_HEIGHT - BOTTOM_MARGIN - footer_height), label, font=_BODY_FONT, fill=0)

    return image


def render_home_screen() -> Image.Image:
    """A Poke Ball centered on an otherwise blank screen, shown until the
    first button press."""
    image = Image.new("1", (DISPLAY_WIDTH, DISPLAY_HEIGHT), color=1)
    draw = ImageDraw.Draw(image)

    radius = POKEBALL_DIAMETER // 2
    cx, cy = DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2
    bbox = (cx - radius, cy - radius, cx + radius, cy + radius)

    draw.ellipse(bbox, outline=0, fill=1, width=3)
    draw.pieslice(bbox, start=180, end=360, fill=0)
    draw.line((cx - radius, cy, cx + radius, cy), fill=0, width=4)

    button_radius = radius // 4
    button_bbox = (cx - button_radius, cy - button_radius, cx + button_radius, cy + button_radius)
    draw.ellipse(button_bbox, outline=0, fill=1, width=3)

    center_radius = button_radius // 3
    center_bbox = (cx - center_radius, cy - center_radius, cx + center_radius, cy + center_radius)
    draw.ellipse(center_bbox, fill=0)

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


def _wrap_lines(draw: ImageDraw.ImageDraw, text: str, max_width: int, font) -> list[str]:
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
    return lines


def _draw_text_box(draw: ImageDraw.ImageDraw, lines: list[str], font, bottom: int) -> None:
    """Draws a double-bordered box (as in the games' dialogue text boxes),
    bottom-anchored and horizontally centered, sized to fit the given lines."""
    line_height = _line_height(draw, font)
    box_height = line_height * len(lines) + 2 * BOX_PADDING
    left, right = BOX_MARGIN, DISPLAY_WIDTH - BOX_MARGIN
    top = bottom - box_height

    draw.rectangle((left, top, right, bottom), outline=0, fill=1, width=2)
    gap = BOX_BORDER_GAP
    draw.rectangle((left + gap, top + gap, right - gap, bottom - gap), outline=0, width=1)

    y = top + BOX_PADDING
    for line in lines:
        draw.text((left + BOX_PADDING, y), line, font=font, fill=0)
        y += line_height


def _line_height(draw: ImageDraw.ImageDraw, font) -> int:
    # Measured from actual glyph metrics rather than the font's nominal point
    # size, since a bitmap-style font can rasterize taller than its point size.
    top, bottom = draw.textbbox((0, 0), "Ag0", font=font)[1::2]
    return (bottom - top) + 2
