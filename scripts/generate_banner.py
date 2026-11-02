"""Generate the original pixel banner. Requires Pillow: python -m pip install Pillow.

Run from any directory: python scripts/generate_banner.py
All lettering is drawn from the bitmap alphabet below; no font downloads needed.
"""

from pathlib import Path
from html import escape
import random

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
W, H = 1200, 420
COLORS = {
    "bg": "#080f20", "grid": "#14233d", "line": "#263f65",
    "muted": "#8faacc", "white": "#e0efff", "cyan": "#569cff",
    "violet": "#3264c8", "shadow": "#163e72", "blue": "#81c3ff",
    "panel": "#0b162b", "scan": "#0d1a30", "dim": "#35557f",
}
FONT = {
    "A": "01110/10001/10001/11111/10001/10001/10001",
    "B": "11110/10001/10001/11110/10001/10001/11110",
    "C": "01111/10000/10000/10000/10000/10000/01111",
    "D": "11110/10001/10001/10001/10001/10001/11110",
    "E": "11111/10000/10000/11110/10000/10000/11111",
    "F": "11111/10000/10000/11110/10000/10000/10000",
    "G": "01111/10000/10000/10111/10001/10001/01111",
    "H": "10001/10001/10001/11111/10001/10001/10001",
    "I": "11111/00100/00100/00100/00100/00100/11111",
    "J": "00111/00010/00010/00010/10010/10010/01100",
    "K": "10001/10010/10100/11000/10100/10010/10001",
    "L": "10000/10000/10000/10000/10000/10000/11111",
    "M": "10001/11011/10101/10101/10001/10001/10001",
    "N": "10001/11001/10101/10011/10001/10001/10001",
    "O": "01110/10001/10001/10001/10001/10001/01110",
    "P": "11110/10001/10001/11110/10000/10000/10000",
    "Q": "01110/10001/10001/10001/10101/10010/01101",
    "R": "11110/10001/10001/11110/10100/10010/10001",
    "S": "01111/10000/10000/01110/00001/00001/11110",
    "T": "11111/00100/00100/00100/00100/00100/00100",
    "U": "10001/10001/10001/10001/10001/10001/01110",
    "V": "10001/10001/10001/10001/10001/01010/00100",
    "W": "10001/10001/10001/10101/10101/10101/01010",
    "X": "10001/10001/01010/00100/01010/10001/10001",
    "Y": "10001/10001/01010/00100/00100/00100/00100",
    "Z": "11111/00001/00010/00100/01000/10000/11111",
    "0": "01110/10001/10011/10101/11001/10001/01110",
    "1": "00100/01100/00100/00100/00100/00100/01110",
    "2": "01110/10001/00001/00010/00100/01000/11111",
    "3": "11110/00001/00001/01110/00001/00001/11110",
    "4": "10010/10010/10010/11111/00010/00010/00010",
    "5": "11111/10000/10000/11110/00001/00001/11110",
    "6": "01110/10000/10000/11110/10001/10001/01110",
    "7": "11111/00001/00010/00100/01000/01000/01000",
    "8": "01110/10001/10001/01110/10001/10001/01110",
    "9": "01110/10001/10001/01111/00001/00001/01110",
    ":": "00000/00100/00100/00000/00100/00100/00000",
    "_": "00000/00000/00000/00000/00000/00000/11111",
    "[": "01110/01000/01000/01000/01000/01000/01110",
    "]": "01110/00010/00010/00010/00010/00010/01110",
    "/": "00001/00001/00010/00100/01000/10000/10000",
    ">": "10000/01000/00100/00010/00100/01000/10000",
    "-": "00000/00000/00000/11111/00000/00000/00000",
    ".": "00000/00000/00000/00000/00000/00110/00110",
    " ": "00000/00000/00000/00000/00000/00000/00000",
}


class Canvas:
    """Use the same rectangles for raster animation and the static SVG."""

    def __init__(self):
        self.image = Image.new("RGB", (W, H), COLORS["bg"])
        self.draw = ImageDraw.Draw(self.image)
        self.rects = [(0, 0, W, H, COLORS["bg"])]

    def rect(self, x, y, w, h, color):
        fill = COLORS.get(color, color)
        self.draw.rectangle((x, y, x + w - 1, y + h - 1), fill=fill)
        self.rects.append((x, y, w, h, fill))

    def text(self, text, x, y, scale, color):
        for char in text:
            for row, bits in enumerate(FONT[char].split("/")):
                for col, bit in enumerate(bits):
                    if bit == "1":
                        self.rect(x + col * scale, y + row * scale, scale, scale, color)
            x += 6 * scale


def scene(letters=8, detail=3, cursor=False, scramble="", tick=0, command=8):
    c = Canvas()
    rng = random.Random(17)
    # Data fragments stay at the edges, leaving the identity readable.
    for x in (18, 48, 1124, 1154):
        for y in range(72, 360, 18):
            c.text("".join(rng.choice("0123456789ABCDEF") for _ in range(3)), x, y, 1, "grid")
    c.rect(74, 26, 1052, 368, "panel")
    for y in range(28, 394, 4):
        c.rect(76, y, 1048, 1, "scan")
    c.rect(74, 26, 1052, 1, "line")
    c.rect(74, 26, 180, 3, "cyan")
    c.rect(74, 26, 3, 30, "cyan")
    c.rect(1123, 26, 3, 30, "violet")
    c.rect(74, 393, 1052, 1, "line")
    c.rect(1026, 391, 100, 3, "violet")
    c.rect(1123, 365, 3, 29, "violet")
    c.text("TERMINAL / 01", 98, 46, 2, "cyan")
    c.text("IDENTITY SEQUENCE", 884, 49, 1, "muted")
    c.rect(98, 78, 1004, 1, "line")
    c.text("> WHOAMI"[:command], 116, 103, 2, "cyan")
    if command < 8:
        c.text("_", 116 + command * 12, 103, 2, "cyan")
    c.text("[", 111, 169, 6, "dim")
    c.text("]", 1053, 169, 6, "dim")
    name = "DRATOROS"[:letters]
    # RGB separation and interrupted pixels supply the cyberpunk character.
    c.text(name, 180, 154, 17, "blue")
    c.text(name, 186, 160, 17, "violet")
    c.text(name, 183, 157, 17, "white")
    if scramble and letters < 8:
        c.text(scramble, 183 + letters * 102, 157, 17, "cyan")
    if cursor:
        c.rect(183 + letters * 102, 276, 70, 4, "cyan")
    # Dim scanlines cross the title without sacrificing the shapes of the letters.
    c.rect(183, 187, 805, 2, "panel")
    c.rect(183, 239, 805, 2, "panel")
    if tick:
        y = 157 + (tick * 19) % 105
        strip = c.image.crop((178, y, 1000, y + 6))
        c.image.paste(strip, (178 + (8 if tick % 2 else -6), y))
    c.text("SYS", 98, 355, 1, "dim")
    c.text("//", 1076, 355, 1, "violet")
    if detail >= 1:
        c.text("> LINK ESTABLISHED", 184, 298, 1, "muted")
    if detail >= 2:
        c.text("> IDENTITY: DRATOROS", 184, 318, 1, "muted")
    if detail >= 3:
        c.text("> ACCESS GRANTED", 184, 347, 2, "cyan")
        c.text("DIEGO / PERSONAL GITHUB INTERFACE", 682, 354, 1, "muted")
        for n in range(11):
            c.rect(966 + n * 10, 301, 5, 25 if n % 3 else 17, "violet" if n > 7 else "dim")
    return c


def main():
    ASSETS.mkdir(exist_ok=True)
    final = scene()
    title = "Dratoros — pixel-art cyberpunk terminal"
    desc = "The name Dratoros in pixel lettering with a glitch effect, an identity terminal, and medium, electric, and light blue accents."
    rects = "\n".join(
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"/>'
        for x, y, w, h, fill in final.rects
    )
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc" shape-rendering="crispEdges">\n'
        f'<title id="title">{escape(title)}</title>\n<desc id="desc">{escape(desc)}</desc>\n'
        f'{rects}\n</svg>\n'
    )
    preview_dir = ROOT / "tmp"
    preview_dir.mkdir(exist_ok=True)
    (preview_dir / "profile-banner.svg").write_text(svg, encoding="utf-8")
    final.image.save(preview_dir / "profile-banner.png", optimize=True)

    # Shared palette preserves the exact colors and keeps GIF size small.
    palette = Image.new("P", (1, 1))
    rgb = [tuple(bytes.fromhex(v[1:])) for v in COLORS.values()]
    palette.putpalette([v for color in rgb for v in color] + [0] * (768 - len(rgb) * 3))
    frames, durations = [], []

    def append(c, duration):
        frames.append(c.image.quantize(palette=palette, dither=Image.Dither.NONE))
        durations.append(duration)

    # Open with the command being typed; the name then resolves one glyph at a time.
    # The separate PNG/SVG provide a complete composition without animation.
    append(scene(0, 0, command=0), 300)
    for n in range(1, 9):
        append(scene(0, 0, command=n), 80)
    append(scene(0, 0, True), 240)
    for n, symbol in enumerate("7A0F3E9C"):
        append(scene(n, 0, True, scramble=symbol, tick=n + 1), 90)
        append(scene(n + 1, 0, n < 7), 150)
    append(scene(8, 0, tick=2), 100)
    append(scene(8, 0), 250)
    for detail in range(1, 4):
        append(scene(8, detail), 260)
    append(final, 3600)
    frames[0].save(
        ASSETS / "profile-banner.gif", save_all=True, append_images=frames[1:],
        duration=durations, loop=0, optimize=True, disposal=1,
    )
    with Image.open(ASSETS / "profile-banner.gif") as gif:
        total = 0
        for i in range(gif.n_frames):
            gif.seek(i)
            gif.load()
            total += gif.info["duration"]
        print(f"GIF verified: {gif.n_frames} frames, {total} ms, {gif.size}")
    print(f"Size: {(ASSETS / 'profile-banner.gif').stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
