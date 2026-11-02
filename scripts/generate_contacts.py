"""Build the phone-avatar GIF and local, split-label contact badges.

Requires Pillow. Run: python scripts/generate_contacts.py
Only URLs explicitly supplied or already confirmed belong in contacts.json.
Null URLs render as pending badges without a clickable link.
"""

import json
from bisect import bisect_right
from html import escape
from pathlib import Path
from urllib.parse import urlsplit

from PIL import Image, ImageDraw

from generate_banner import Canvas, COLORS

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SIZE = (1200, 340)


def sprites():
    atlas = Image.open(ASSETS / "contact-sprites-hacker-axe.png").convert("RGBA")
    cell_w, cell_h = atlas.width // 4, atlas.height // 2
    result = []
    for n in range(8):
        x, y = (n % 4) * cell_w, (n // 4) * cell_h
        sprite = atlas.crop((x, y, x + cell_w, y + cell_h))
        sprite = sprite.resize((96, 128), Image.Resampling.NEAREST)
        sprite = sprite.resize((192, 256), Image.Resampling.NEAREST)
        # Align feet rather than each cell, since the generated rows have padding.
        opaque = sprite.getchannel("A").point(lambda a: 255 if a >= 220 else 0)
        bbox = opaque.getbbox()
        if bbox is None:
            raise ValueError("Empty character cell")
        feet = opaque.crop((0, bbox[3] - 24, 192, bbox[3])).getbbox()
        foot_center = (feet[0] + feet[2]) // 2
        result.append((sprite, (218 - foot_center, 283 - bbox[3])))
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
    c.text("02 / SOCIAL CHANNELS", 62, 40, 1, "muted")
    c.text("DRATOROS", 1080, 40, 1, "blue")
    for x in range(96, 364, 12):
        c.rect(x, 283, 6, 2, "dim")
    c.text("STAY IN TOUCH", 126, 299, 1, "dim")
    return c.image.crop((0, 0, *SIZE)).convert("RGBA")


def heading(letters):
    c = Canvas()
    first, second = "WHERE TO"[:letters], "FIND ME"[:max(0, letters - 8)]
    c.text(first, 444, 106, 10, "violet")
    c.text(first, 441, 103, 10, "white")
    c.text(second, 444, 190, 12, "violet")
    c.text(second, 441, 187, 12, "white")
    if 0 < letters < 8:
        c.rect(441 + letters * 60, 177, 30, 3, "cyan")
    elif 8 <= letters < 15:
        c.rect(441 + (letters - 8) * 72, 276, 30, 3, "cyan")
    if letters == 15:
        c.rect(444, 289, 45, 3, "cyan")
        c.text("SOCIALS / CONTACT", 510, 285, 1, "muted")
    layer = Image.new("RGBA", SIZE)
    draw = ImageDraw.Draw(layer)
    for x, y, w, h, color in c.rects[1:]:
        draw.rectangle((x, y, x + w - 1, y + h - 1), fill=color)
    return layer


def frame(base, character, phase, letters=15):
    output = base.copy()
    sprite, position = character
    output.alpha_composite(sprite, position)
    output.alpha_composite(heading(letters))
    draw = ImageDraw.Draw(output)
    # A tiny message bubble adds a social cue without covering the phone.
    if phase in (1, 2, 3, 4, 5, 6):
        x, y = 334, 134 - min(phase, 4) * 3
        draw.rectangle((x + 3, y, x + 43, y + 25), fill=COLORS["line"])
        draw.rectangle((x, y + 3, x + 46, y + 22), fill=COLORS["line"])
        draw.rectangle((x + 3, y + 3, x + 43, y + 22), fill=COLORS["panel"])
        draw.rectangle((x + 7, y + 24, x + 12, y + 29), fill=COLORS["line"])
        for n in range(3):
            fill = COLORS["blue"] if n <= phase % 3 else COLORS["dim"]
            draw.rectangle((x + 10 + n * 10, y + 11, x + 13 + n * 10, y + 14), fill=fill)
    return output.convert("RGB")


def generate_gif():
    characters, base = sprites(), background()
    sequence = (0, 1, 2, 3, 4, 6, 1, 2, 3, 4, 5, 6, 7, 6, 0)
    pose_durations = (600, 180, 140, 180, 240, 400, 180, 140, 180, 240, 450, 420, 120, 380, 700)
    pose_starts, elapsed = [], 0
    for duration in pose_durations:
        pose_starts.append(elapsed)
        elapsed += duration
    # Merge pose changes and typing events so both motions stay independent.
    # The first tap triggers the title; the complete heading holds for reading.
    times = sorted(set(pose_starts + [650 + n * 110 for n in range(15)] + [elapsed]))
    frames, durations = [], []
    for start, end in zip(times, times[1:]):
        pose_index = bisect_right(pose_starts, start) - 1
        letters = max(0, min(15, 1 + (start - 650) // 110))
        frames.append(frame(base, characters[sequence[pose_index]], pose_index % 8, letters))
        durations.append(end - start)
    # One palette across the cycle prevents per-frame palette flicker.
    sample = Image.new("RGB", (SIZE[0], SIZE[1] * 4))
    for row, index in enumerate((0, len(frames) // 3, 2 * len(frames) // 3, len(frames) - 1)):
        sample.paste(frames[index], (0, row * SIZE[1]))
    palette = sample.quantize(colors=128, method=Image.Quantize.MEDIANCUT)
    indexed = [f.quantize(palette=palette, dither=Image.Dither.NONE) for f in frames]
    indexed[0].save(
        ASSETS / "contact-avatar.gif", save_all=True, append_images=indexed[1:],
        duration=durations, loop=0, optimize=True, disposal=1,
    )
    preview_dir = ROOT / "tmp"
    preview_dir.mkdir(exist_ok=True)
    frames[-1].save(preview_dir / "contact-avatar.png", optimize=True)
    with Image.open(ASSETS / "contact-avatar.gif") as gif:
        elapsed = 0
        for i in range(gif.n_frames):
            gif.seek(i)
            gif.load()
            elapsed += gif.info["duration"]
        print(f"Contact GIF verified: {gif.n_frames} frames, {elapsed} ms, {gif.size}")
    print(f"Size: {(ASSETS / 'contact-avatar.gif').stat().st_size:,} bytes")
    review = Image.new("RGB", (SIZE[0], SIZE[1] * 4))
    for row, when in enumerate((0, 1100, 1800, 3200)):
        index = bisect_right(times, when) - 1
        review.paste(frames[index], (0, row * SIZE[1]))
    (ROOT / "tmp").mkdir(exist_ok=True)
    review.save(ROOT / "tmp" / "contact-motion-review.png")


def icon(service):
    # Small, original interface glyphs; no downloaded logo or font dependency.
    paths = {
        "github": '<circle cx="6" cy="4" r="2"/><circle cx="6" cy="16" r="2"/><circle cx="15" cy="6" r="2"/><path d="M6 6v8m0-3c7 0 9-1 9-3"/>',
        "linkedin": '<rect x="2" y="2" width="17" height="17"/><path d="M6 9v6m0-9v1m4 8V9m0 2c0-3 5-3 5 0v4"/>',
        "email": '<rect x="1" y="4" width="19" height="13"/><path d="m2 5 9 7 8-7"/>',
        "instagram": '<rect x="2" y="2" width="17" height="17" rx="4"/><circle cx="10.5" cy="10.5" r="4"/><circle cx="16" cy="5" r=".7"/>',
    }
    return f'<g transform="translate(13 8)" fill="none" stroke="#dcecff" stroke-width="1.7">{paths[service]}</g>'


def generate_badges():
    contacts = json.loads((ASSETS / "contacts.json").read_text(encoding="utf-8"))
    folder = ASSETS / "contacts"
    folder.mkdir(exist_ok=True)
    lines = ['<!-- CONTACT BUTTONS: generated by scripts/generate_contacts.py -->', '<p align="center">']
    for n, contact in enumerate(contacts):
        label = contact["label"].upper()
        confirmed = bool(contact["url"])
        status = contact["handle"] or "LINK PENDING"
        left = 50 + len(label) * 8
        right = 24 + len(status) * 8
        width = left + right
        description = f'{contact["label"]}: {status}'
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="36" '
            f'viewBox="0 0 {width} 36" role="img" aria-labelledby="title">'
            f'<title id="title">{escape(description)}</title>'
            f'<path fill="#263f65" d="M0 0h{left}v36H0z"/>'
            f'<path fill="{"#3264c8" if confirmed else "#14233d"}" d="M{left} 0h{right}v36H{left}z"/>'
            f'{icon(contact["id"])}'
            f'<g font-family="Consolas, monospace" font-size="12" font-weight="700" letter-spacing="1" fill="#e0efff">'
            f'<text x="42" y="23">{escape(label)}</text>'
            f'<text x="{left + 12}" y="23" fill="{"#ffffff" if confirmed else "#8faacc"}">{escape(status)}</text>'
            '</g></svg>\n'
        )
        badge = folder / f'{contact["id"]}.svg'
        badge.write_text(svg, encoding="utf-8")
        img = f'<img src="assets/contacts/{contact["id"]}.svg" alt="{escape(description, quote=True)}" height="32" />'
        if confirmed:
            if urlsplit(contact["url"]).scheme not in ("https", "mailto"):
                raise ValueError("Contact URLs must use https or mailto")
            img = f'<a href="{escape(contact["url"], quote=True)}">{img}</a>'
        lines.append(f'  {img}')
        if n % 2 == 1 and n < len(contacts) - 1:
            lines.append('  <br />')
    lines += ['</p>', '<!-- /CONTACT BUTTONS -->']
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    start = text.index('<!-- CONTACT BUTTONS:')
    end = text.index('<!-- /CONTACT BUTTONS -->', start) + len('<!-- /CONTACT BUTTONS -->')
    readme.write_text(text[:start] + '\n'.join(lines) + text[end:], encoding="utf-8")
    linked = sum(bool(contact["url"]) for contact in contacts)
    print(f"Contact badges generated: {linked} linked, {len(contacts) - linked} pending")


if __name__ == "__main__":
    generate_gif()
    generate_badges()
