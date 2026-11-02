"""Assemble generated pixel sprites into the axe-throw section intro.

Requires Pillow. Run: python scripts/generate_about.py
The image model supplies the poses, axe, and blue flame cycle. This script
composes their motion and reveals the existing pixel typeface through the fire.
"""

import math
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

from generate_banner import Canvas, COLORS

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SIZE = (1200, 340)
AXE_DIAGONAL = 185


def load_sprites():
    atlas = Image.open(ASSETS / "avatar-sprites-hacker.png").convert("RGBA")
    cell_w, cell_h = atlas.width // 4, atlas.height // 2
    sprites = []
    for i in range(8):
        left, top = (i % 4) * cell_w, (i // 4) * cell_h
        cell = atlas.crop((left, top, left + cell_w, top + cell_h))
        if i == 7:
            # Match the held weapon's visible length. Never shrink it to fit a
            # rotating bounding box: only expand the canvas during rotation.
            axe = cell.crop(cell.getbbox())
            scale = AXE_DIAGONAL / math.hypot(axe.width, axe.height)
            size = tuple(max(2, 2 * round(edge * scale / 2)) for edge in axe.size)
            axe = axe.resize((size[0] // 2, size[1] // 2), Image.Resampling.NEAREST)
            axe = axe.resize(size, Image.Resampling.NEAREST)
            continue
        # Native low resolution, then integer scaling keeps the 8-bit silhouette.
        cell = cell.resize((96, 128), Image.Resampling.NEAREST)
        if i == 6:
            # The previous pose's fingertips overlap this cell's left gutter.
            # Keep the aligned canvas while excluding that neighboring fragment.
            cell.paste((0, 0, 0, 0), (0, 0, 8, 128))
        sprites.append(cell.resize((192, 256), Image.Resampling.NEAREST))
    return sprites, axe


def load_flames():
    atlas = Image.open(ASSETS / "blue-flame-sprites.png").convert("RGBA")
    cell_w, cell_h = atlas.width // 3, atlas.height // 2
    flames = []
    for n in range(6):
        x, y = (n % 3) * cell_w, (n // 3) * cell_h
        cell = atlas.crop((x, y, x + cell_w, y + cell_h))
        cell = cell.resize((160, 160), Image.Resampling.NEAREST)
        flames.append(cell.resize((320, 320), Image.Resampling.NEAREST))
    return flames


def background():
    c = Canvas()
    c.rect(0, 0, 1200, 420, "bg")
    c.rect(42, 22, 1116, 296, "panel")
    for y in range(26, 317, 5):
        c.rect(44, y, 1112, 1, "scan")
    c.rect(42, 22, 1116, 1, "line")
    c.rect(42, 22, 112, 3, "cyan")
    c.rect(42, 22, 3, 18, "cyan")
    c.rect(42, 317, 1116, 1, "line")
    c.rect(1050, 315, 108, 3, "violet")
    c.text("01 / CHARACTER FILE", 62, 40, 1, "muted")
    c.text("DRATOROS", 1080, 40, 1, "blue")
    for x in range(96, 364, 12):
        c.rect(x, 283, 6, 2, "dim")
    c.text("PERSONAL TOKEN", 120, 299, 1, "dim")
    return c.image.crop((0, 0, *SIZE)).convert("RGBA")


def heading(details=True):
    c = Canvas()
    c.text("ABOUT ME", 444, 133, 12, "violet")
    c.text("ABOUT ME", 441, 130, 12, "white")
    if details:
        c.rect(444, 237, 45, 3, "cyan")
        c.text("DIEGO / DRATOROS", 510, 231, 2, "muted")
        c.text("> PROFILE UNLOCKED", 444, 271, 1, "blue")
    # Type layer has no dependence on generated image pixels.
    layer = Image.new("RGBA", SIZE)
    for x, y, w, h, color in c.rects[1:]:
        ImageDraw.Draw(layer).rectangle((x, y, x + w - 1, y + h - 1), fill=color)
    return layer


def blue_fire(flames, step, x, y, opacity=1):
    effect = Image.new("RGBA", SIZE)
    flame = flames[step % len(flames)]
    if opacity < 1:
        flame = flame.copy()
        flame.putalpha(flame.getchannel("A").point(lambda a: round(a * opacity)))
    # The bright tip follows the weapon; the tongues stream behind it.
    effect.alpha_composite(flame, (round(x - 300), round(y - 208)))
    # Fade into the stage boundaries in pixel steps rather than cutting a
    # rectangular edge through the fire. The avatar stays unobscured.
    clip = Image.new("L", SIZE)
    draw = ImageDraw.Draw(clip)
    for left in range(300, 1150, 2):
        opacity = max(0, min(1, (left - 300) / 48, (1150 - left) / 28))
        draw.rectangle((left, 72, left + 1, 280), fill=round(255 * opacity))
    effect.putalpha(ImageChops.multiply(effect.getchannel("A"), clip))
    return effect


def frame(base, sprites, axe, flames, pose=0, flight=None, reveal=0,
          flame_step=0, embers=0, details=False):
    canvas = base.copy()
    # Frame feet differ slightly between rows in the source atlas.
    canvas.alpha_composite(sprites[pose], (102, 42 if pose < 4 else 58))
    if flight is not None:
        x = 285 + flight * 1045
        # A shallow arc leaves room for the full-size rotating axe.
        y = 171 - math.sin(flight * math.pi) * 22
        ignition = min(1, flight * 8)
        canvas.alpha_composite(blue_fire(flames, flame_step, x, y, ignition))
        spun = axe.rotate(-flight * 720, Image.Resampling.NEAREST, expand=True)
        canvas.alpha_composite(spun, (int(x - spun.width / 2), int(y - spun.height / 2)))
        # Letters materialize in the trail while the axe is still in the air.
        reveal = max(0, min(1, (x - 18 - 428) / 690))
    if embers:
        canvas.alpha_composite(blue_fire(flames, flame_step, 1330, 171, embers))
    if reveal:
        layer = heading(details=details)
        edge = 428 + int(690 * reveal)
        canvas.alpha_composite(layer.crop((0, 0, edge, SIZE[1])))
    return canvas.convert("RGB")


def main():
    sprites, axe = load_sprites()
    flames = load_flames()
    base = background()
    frames, durations = [], []

    def append(pose, duration, **kwargs):
        frames.append(frame(base, sprites, axe, flames, pose=pose, **kwargs))
        durations.append(duration)

    append(0, 650)
    append(1, 240)
    append(2, 280)
    append(3, 90)
    for n in range(27):
        pose = 3 if n < 4 else 4 if n < 10 else 5 if n < 17 else 6
        append(pose, 70, flight=n / 26, flame_step=n)
    for n in range(8):
        append(6, 70, reveal=1, embers=(8 - n) / 8, flame_step=27 + n,
               details=n >= 4)
    append(6, 4200, reveal=1, details=True)

    final = frames[-1]
    preview_dir = ROOT / "tmp"
    preview_dir.mkdir(exist_ok=True)
    final.save(preview_dir / "about-avatar.png", optimize=True)
    # Train one palette across the motion, avoiding color flicker between poses.
    sample = Image.new("RGB", (SIZE[0], SIZE[1] * 6))
    for i, index in enumerate((0, 2, 10, 17, 24, len(frames) - 1)):
        sample.paste(frames[index], (0, i * SIZE[1]))
    palette = sample.quantize(colors=128, method=Image.Quantize.MEDIANCUT)
    indexed = [f.quantize(palette=palette, dither=Image.Dither.NONE) for f in frames]
    indexed[0].save(
        ASSETS / "about-avatar.gif", save_all=True, append_images=indexed[1:],
        duration=durations, loop=0, optimize=True, disposal=1,
    )
    with Image.open(ASSETS / "about-avatar.gif") as gif:
        elapsed = 0
        for i in range(gif.n_frames):
            gif.seek(i)
            gif.load()
            elapsed += gif.info["duration"]
        print(f"Avatar GIF verified: {gif.n_frames} frames, {elapsed} ms, {gif.size}")
    print(f"Size: {(ASSETS / 'about-avatar.gif').stat().st_size:,} bytes")
    print(f"Fixed axe sprite: {axe.size}, diagonal {math.hypot(*axe.size):.1f} px")
    # A review sheet shows the key motion beats without requiring a GIF player.
    sheet = Image.new("RGB", (SIZE[0], SIZE[1] * 6))
    for row, index in enumerate((2, 7, 14, 22, 31, len(frames) - 1)):
        sheet.paste(frames[index], (0, row * SIZE[1]))
    review = ROOT / "tmp" / "avatar-motion-review.png"
    review.parent.mkdir(exist_ok=True)
    sheet.save(review)


if __name__ == "__main__":
    main()
