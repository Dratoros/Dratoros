"""Assemble the workstation/avatar loop for the What do I do heading.

Requires Pillow. Run: python scripts/generate_work.py
The generated atlas supplies the character, desk, computer and drink poses.
The script handles alignment, timing and the existing bitmap title lettering.
"""

from bisect import bisect_right
from pathlib import Path

from PIL import Image, ImageDraw

from generate_banner import Canvas

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SIZE = (1200, 340)
TITLE = "WHAT DO I DO"


def load_sprites():
    atlas = Image.open(ASSETS / "work-sprites-white-monster-axe.png").convert("RGBA")
    cell_w, cell_h = atlas.width // 4, atlas.height // 2
    result = []
    for n in range(8):
        left, top = (n % 4) * cell_w, (n // 4) * cell_h
        cell = atlas.crop((left, top, left + cell_w, top + cell_h))
        cell = cell.resize((96, 128), Image.Resampling.NEAREST)
        sprite = cell.resize((192, 256), Image.Resampling.NEAREST)
        # Align the whole workstation, including desk legs, between both rows.
        opaque = sprite.getchannel("A").point(lambda a: 255 if a >= 220 else 0)
        bounds = opaque.getbbox()
        if bounds is None:
            raise ValueError("Empty workstation sprite")
        result.append((sprite, (132, 283 - bounds[3])))
    return result


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
    c.text("03 / WORKSTATION", 62, 40, 1, "muted")
    c.text("DRATOROS", 1080, 40, 1, "blue")
    for x in range(96, 364, 12):
        c.rect(x, 283, 6, 2, "dim")
    c.text("BUILD / AUTOMATE", 120, 299, 1, "dim")
    return c.image.crop((0, 0, *SIZE)).convert("RGBA")


def heading(letters):
    c = Canvas()
    text = TITLE[:letters]
    c.text(text, 444, 143, 9, "violet")
    c.text(text, 441, 140, 9, "white")
    if 0 < letters < len(TITLE):
        c.rect(441 + letters * 54, 211, 27, 3, "cyan")
    if letters == len(TITLE):
        c.rect(444, 237, 45, 3, "cyan")
        c.text("DATA / AUTOMATION / DEVELOPMENT", 510, 233, 1, "muted")
    layer = Image.new("RGBA", SIZE)
    draw = ImageDraw.Draw(layer)
    for x, y, w, h, color in c.rects[1:]:
        draw.rectangle((x, y, x + w - 1, y + h - 1), fill=color)
    return layer


def frame(base, character, letters):
    output = base.copy()
    sprite, position = character
    output.alpha_composite(sprite, position)
    output.alpha_composite(heading(letters))
    return output.convert("RGB")


def main():
    characters, base = load_sprites(), background()
    # Type, take a sip, set the can down and return to the keyboard.
    sequence = (0, 1, 0, 2, 1, 0, 2, 0, 3, 4, 5, 6, 7,
                0, 1, 2, 0, 1, 0, 2, 0, 1, 2, 0)
    pose_durations = (500, 180, 160, 200, 180, 160, 200, 400, 220, 280,
                      800, 280, 350, 500, 200, 220, 350, 200, 350, 200,
                      350, 200, 220, 700)
    starts, elapsed = [], 0
    for duration in pose_durations:
        starts.append(elapsed)
        elapsed += duration
    times = sorted(set(starts + [500 + n * 100 for n in range(len(TITLE))] + [elapsed]))
    frames, durations = [], []
    for start, end in zip(times, times[1:]):
        pose = sequence[bisect_right(starts, start) - 1]
        letters = max(0, min(len(TITLE), 1 + (start - 500) // 100))
        frames.append(frame(base, characters[pose], letters))
        durations.append(end - start)

    # A shared palette keeps blue, skin tones and the white/silver can stable.
    samples = (0, bisect_right(times, 1200) - 1,
               bisect_right(times, 2700) - 1, bisect_right(times, 3200) - 1,
               len(frames) - 1)
    sample = Image.new("RGB", (SIZE[0], SIZE[1] * len(samples)))
    for row, index in enumerate(samples):
        sample.paste(frames[index], (0, row * SIZE[1]))
    palette = sample.quantize(colors=128, method=Image.Quantize.MEDIANCUT)
    indexed = [f.quantize(palette=palette, dither=Image.Dither.NONE) for f in frames]
    indexed[0].save(
        ASSETS / "work-avatar.gif", save_all=True, append_images=indexed[1:],
        duration=durations, loop=0, optimize=True, disposal=1,
    )
    preview_dir = ROOT / "tmp"
    preview_dir.mkdir(exist_ok=True)
    frame(base, characters[0], len(TITLE)).save(preview_dir / "work-avatar.png", optimize=True)
    with Image.open(ASSETS / "work-avatar.gif") as gif:
        elapsed = 0
        for i in range(gif.n_frames):
            gif.seek(i)
            gif.load()
            elapsed += gif.info["duration"]
        print(f"Workstation GIF verified: {gif.n_frames} frames, {elapsed} ms, {gif.size}")
    print(f"Size: {(ASSETS / 'work-avatar.gif').stat().st_size:,} bytes")
    review = Image.new("RGB", (SIZE[0], SIZE[1] * 4))
    for row, when in enumerate((800, 2200, 2800, 4300)):
        index = bisect_right(times, when) - 1
        review.paste(frames[index], (0, row * SIZE[1]))
    (ROOT / "tmp").mkdir(exist_ok=True)
    review.save(ROOT / "tmp" / "work-motion-review.png")


if __name__ == "__main__":
    main()
