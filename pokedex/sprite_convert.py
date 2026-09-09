"""Shared image conversion helpers for producing e-ink-ready (1-bit) sprites."""

from PIL import Image

GAME_SPRITE_SCALE = 4  # native in-game sprites are 40x40; nearest-neighbor upscale keeps pixel art crisp


def upscale_game_sprite(sprite: Image.Image) -> Image.Image:
    size = (sprite.width * GAME_SPRITE_SCALE, sprite.height * GAME_SPRITE_SCALE)
    return sprite.resize(size, Image.NEAREST)


def flatten_to_1bit(sprite: Image.Image) -> Image.Image:
    flattened = Image.alpha_composite(Image.new("RGBA", sprite.size, (255, 255, 255, 255)), sprite)
    return flattened.convert("L").convert("1", dither=Image.FLOYDSTEINBERG)
