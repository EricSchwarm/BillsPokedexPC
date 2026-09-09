"""Shared image conversion helpers for producing e-ink-ready (1-bit) sprites."""

from PIL import Image

from config import DISPLAY_WIDTH

GAME_SPRITE_TARGET_WIDTH = round(0.75 * DISPLAY_WIDTH)  # sprite width as a fraction of the display


def upscale_game_sprite(sprite: Image.Image) -> Image.Image:
    scale = GAME_SPRITE_TARGET_WIDTH / sprite.width
    size = (round(sprite.width * scale), round(sprite.height * scale))
    return sprite.resize(size, Image.NEAREST)


def flatten_to_1bit(sprite: Image.Image) -> Image.Image:
    flattened = Image.alpha_composite(Image.new("RGBA", sprite.size, (255, 255, 255, 255)), sprite)
    return flattened.convert("L").convert("1", dither=Image.FLOYDSTEINBERG)
