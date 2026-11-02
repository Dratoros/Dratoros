"""Build the forge animation and smoke reveal for Featured Projects.

Requires Pillow. Run: python scripts/generate_projects.py
The image model supplies the smith poses and smoke; this script assembles
the hammering/blowing sequence and reveals the existing pixel typeface.
"""

from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

from generate_banner import Canvas, COLORS

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SIZE = (1200, 340)


def load_sprites():
    atlas = Image.open(ASSETS / "forge-sprites-hacker.png").convert("RGBA")
    cell_w = atlas.width // 4
    # The first row's anvil bases extend slightly past the nominal 512 px
    # divider. Cut in the clear gutter, keeping every stump and boot complete.
    divider = round(atlas.height * 540 / 1024)
    poses = []
    for n in range(8):
        x = (n % 4) * cell_w
        top, bottom = (0, divider) if n < 4 else (divider, atlas.height)
        cell = atlas.crop((x, top, x + cell_w, bottom))
        low = cell.resize((96, round(cell.height / 4)), Image.Resampling.NEAREST)
        # The outfit edit carries a narrow edge of the next forge into the
        # right gutter. Exclude that strip before positioning each scene.
        low.paste((0, 0, 0, 0), (93, 0, 96, low.height))
        sprite = low.resize((192, low.height * 2), Image.Resampling.NEAREST)
        opaque = sprite.getchannel("A").point(lambda a: 255 if a >= 220 else 0)
        bounds = opaque.getbbox()
        if bounds is None:
            raise ValueError("Empty forge pose")
        poses.append((sprite, (102, 283 - bounds[3])))
    return poses


def load_smoke():
    atlas = Image.open(ASSETS / "forge-smoke-sprites.png").convert("RGBA")
    cell_w, cell_h = atlas.width // 3, atlas.height // 2
    result = []
    for n in range(6):
        x, y = (n % 3) * cell_w, (n // 3) * cell_h
        cell = atlas.crop((x, y, x + cell_w, y + cell_h))
        cell = cell.resize((192, 192), Image.Resampling.NEAREST)
        result.append(cell.resize((384, 384), Image.Resampling.NEAREST))
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
    c.text("04 / FORGE", 62, 40, 1, "muted")
    c.text("DRATOROS", 1080, 40, 1, "blue")
    for x in range(96, 364, 12):
        c.rect(x, 283, 6, 2, "dim")
    c.text("CRAFT / REFINE", 120, 299, 1, "dim")
    return c.image.crop((0, 0, *SIZE)).convert("RGBA")


def heading(details=False):
    c = Canvas()
    c.text("FEATURED", 444, 106, 10, "violet")
    c.text("FEATURED", 441, 103, 10, "white")
    c.text("PROJECTS", 444, 190, 12, "violet")
    c.text("PROJECTS", 441, 187, 12, "white")
    if details:
        c.rect(444, 289, 45, 3, "cyan")
        c.text("PROJECT SHOWCASE", 510, 285, 1, "muted")
    layer = Image.new("RGBA", SIZE)
    draw = ImageDraw.Draw(layer)
    for x, y, w, h, color in c.rects[1:]:
        draw.rectangle((x, y, x + w - 1, y + h - 1), fill=color)
    return layer


def vapor_layer(smoke, step, front, opacity):
    effect = Image.new("RGBA", SIZE)
    plume = smoke[step % len(smoke)].copy()
    plume.putalpha(plume.getchannel("A").point(lambda a: round(a * opacity)))
    effect.alpha_composite(plume, (round(front - 380), -36))
    # Pixel-stepped fade keeps the smoke away from the avatar and frame.
    clip = Image.new("L", SIZE)
    draw = ImageDraw.Draw(clip)
    for left in range(280, 1150, 2):
        opacity = max(0, min(1, (left - 280) / 52, (1150 - left) / 32))
        draw.rectangle((left, 76, left + 1, 280), fill=round(opacity * 255))
    effect.putalpha(ImageChops.multiply(effect.getchannel("A"), clip))
    return effect


def frame(base, characters, smoke, pose, sweep=None, step=0, reveal=0,
          dissipate=0, details=False):
    output = base.copy()
    sprite, position = characters[pose]
    output.alpha_composite(sprite, position)
    if sweep is not None:
        front = 332 + 998 * sweep
        output.alpha_composite(vapor_layer(smoke, step, front, min(0.85, 0.25 + sweep * 4)))
        reveal = max(0, min(1, (front - 24 - 428) / 690))
        if pose == 6 and sweep < 0.45:
            # A few small wisps connect the blowing pose to vapor at the blade.
            breath = ImageDraw.Draw(output)
            for n in range(3):
                x = 242 + n * 17 + step % 3
                y = 177 - n * 2
                breath.rectangle((x, y, x + 8, y + 1), fill=COLORS["muted"])
    if dissipate:
        output.alpha_composite(vapor_layer(smoke, step, 1330, dissipate * 0.6))
    if reveal:
        edge = 428 + round(690 * reveal)
        output.alpha_composite(heading(details).crop((0, 0, edge, SIZE[1])))
    return output.convert("RGB")


def main():
    characters, smoke, base = load_sprites(), load_smoke(), background()
    frames, durations = [], []
    marks = {}

    def append(pose, duration, **kwargs):
        frames.append(frame(base, characters, smoke, pose, **kwargs))
        durations.append(duration)

    append(0, 450)
    for strike in range(3):
        append(1, 180 if strike == 0 else 160)
        append(2, 200 if strike == 0 else 180)
        marks["strike"] = len(frames)
        append(3, 120)
    append(4, 300)
    append(5, 650)
    marks["blow"] = len(frames)
    for n in range(27):
        # He blows first, then watches the finished work as the vapor drifts.
        pose = 6 if n < 13 else 5 if n < 19 else 7
        if n == 11:
            marks["reveal"] = len(frames)
        append(pose, 70, sweep=n / 26, step=n)
    for n in range(9):
        append(7, 70, reveal=1, dissipate=(9 - n) / 9, step=27 + n,
               details=n >= 4)
    append(7, 3600, reveal=1, details=True)

    preview_dir = ROOT / "tmp"
    preview_dir.mkdir(exist_ok=True)
    frames[-1].save(preview_dir / "projects-avatar.png", optimize=True)
    indexes = (0, marks["strike"], marks["blow"] + 3,
               marks["reveal"], len(frames) - 1)
    sample = Image.new("RGB", (SIZE[0], SIZE[1] * len(indexes)))
    for row, index in enumerate(indexes):
        sample.paste(frames[index], (0, row * SIZE[1]))
    palette = sample.quantize(colors=128, method=Image.Quantize.MEDIANCUT)
    indexed = [f.quantize(palette=palette, dither=Image.Dither.NONE) for f in frames]
    indexed[0].save(
        ASSETS / "projects-avatar.gif", save_all=True, append_images=indexed[1:],
        duration=durations, loop=0, optimize=True, disposal=1,
    )
    with Image.open(ASSETS / "projects-avatar.gif") as gif:
        elapsed = 0
        for n in range(gif.n_frames):
            gif.seek(n)
            gif.load()
            elapsed += gif.info["duration"]
        print(f"Forge GIF verified: {gif.n_frames} frames, {elapsed} ms, {gif.size}")
    print(f"Size: {(ASSETS / 'projects-avatar.gif').stat().st_size:,} bytes")
    review = Image.new("RGB", (SIZE[0], SIZE[1] * 5))
    for row, index in enumerate((2, marks["strike"], marks["blow"] + 2,
                                 marks["reveal"] + 3, len(frames) - 1)):
        review.paste(frames[index], (0, row * SIZE[1]))
    (ROOT / "tmp").mkdir(exist_ok=True)
    review.save(ROOT / "tmp" / "projects-motion-review.png")


if __name__ == "__main__":
    main()
