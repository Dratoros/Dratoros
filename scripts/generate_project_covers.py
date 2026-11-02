"""Build static SVG project covers using the profile's existing pixel alphabet.

Requires Pillow, like the avatar generators. Run:
    python scripts/generate_project_covers.py

The SVGs contain only local vector shapes; PNGs in tmp/ are for visual review.
"""

from html import escape
from pathlib import Path
import xml.etree.ElementTree as ET

from generate_banner import Canvas

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "project-covers"
WIDTH, HEIGHT = 1200, 264
PROJECTS = (
    {
        "slug": "erp-integration-platform",
        "name": "ERP Integration Platform",
        "category": "CONSTRUCTION MANAGEMENT",
        "lines": ("ERP INTEGRATION", "PLATFORM"),
        "number": "01",
        "motif": "modules",
    },
    {
        "slug": "toloni-pescarias",
        "name": "Toloni Pescarias",
        "category": "FISHING COMMUNITY",
        "lines": ("TOLONI", "PESCARIAS"),
        "number": "02",
        "motif": "locations",
    },
)


def modules(canvas):
    """Connected modules echo an ERP without presenting an invented UI."""
    canvas.rect(889, 115, 200, 3, "dim")
    canvas.rect(987, 90, 3, 65, "dim")
    for x, y in ((872, 78), (1008, 78), (940, 142)):
        canvas.rect(x, y, 82, 44, "line")
        canvas.rect(x + 2, y + 2, 78, 40, "grid")
        canvas.rect(x + 12, y + 12, 8, 8, "cyan")
        canvas.rect(x + 30, y + 12, 38, 3, "muted")
        canvas.rect(x + 12, y + 28, 56, 3, "dim")


def locations(canvas):
    """Two pixel map pins over quiet waves suggest the fishing community."""
    for row, y in enumerate((142, 166, 190)):
        for n in range(7):
            x = 858 + n * 34
            step = 5 if (row + n) % 2 else 0
            canvas.rect(x, y + step, 18, 3, "dim")
            canvas.rect(x + 18, y + 5 - step, 16, 3, "dim")
    canvas.rect(910, 107, 121, 3, "line")
    canvas.rect(1028, 93, 3, 17, "line")
    for x, y in ((888, 72), (1011, 60)):
        canvas.rect(x + 8, y, 30, 5, "blue")
        canvas.rect(x, y + 5, 46, 35, "blue")
        canvas.rect(x + 6, y + 40, 34, 6, "blue")
        canvas.rect(x + 13, y + 46, 20, 7, "blue")
        canvas.rect(x + 19, y + 53, 8, 7, "blue")
        canvas.rect(x + 12, y + 12, 22, 20, "panel")
        canvas.rect(x + 17, y + 17, 12, 10, "cyan")


def cover(project):
    canvas = Canvas()
    canvas.rect(12, 12, 1176, 240, "panel")
    for y in range(15, 211, 6):
        canvas.rect(16, y, 1168, 1, "scan")
    canvas.rect(12, 12, 1176, 2, "line")
    canvas.rect(12, 12, 184, 4, "cyan")
    canvas.rect(12, 12, 5, 200, "cyan")
    canvas.rect(1184, 36, 4, 176, "line")
    canvas.text(project["category"], 42, 31, 3, "blue")
    canvas.text(project["number"], 1120, 31, 3, "muted")
    for line, y in zip(project["lines"], (79, 143)):
        canvas.text(line, 45, y + 3, 7, "shadow")
        canvas.text(line, 42, y, 7, "white")
    canvas.rect(817, 72, 2, 119, "line")
    if project["motif"] == "modules":
        modules(canvas)
    else:
        locations(canvas)
    canvas.rect(12, 212, 1176, 40, "violet")
    canvas.rect(12, 212, 1176, 2, "cyan")
    canvas.text("VIEW REPOSITORY", 42, 222, 3, "white")
    # Pixel arrow, using the same geometric vocabulary as the profile.
    canvas.rect(1100, 230, 41, 4, "white")
    canvas.rect(1135, 224, 6, 4, "white")
    canvas.rect(1141, 228, 6, 8, "white")
    canvas.rect(1135, 236, 6, 4, "white")
    return canvas


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    review = ROOT / "tmp" / "project-covers"
    review.mkdir(parents=True, exist_ok=True)
    for project in PROJECTS:
        canvas = cover(project)
        title = escape(project["name"])
        description = escape(project["category"].title() + ". View repository.")
        # Bitmap lettering is exported as shapes, so GitHub needs no web font.
        shapes = "".join(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}"/>'
            for x, y, w, h, color in canvas.rects
        )
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
            f'viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc" '
            f'shape-rendering="crispEdges"><title id="title">{title}</title>'
            f'<desc id="desc">{description}</desc>{shapes}</svg>\n'
        )
        ET.fromstring(svg)
        path = OUTPUT / f'{project["slug"]}.svg'
        path.write_text(svg, encoding="utf-8")
        canvas.image.crop((0, 0, WIDTH, HEIGHT)).save(review / f'{project["slug"]}.png')
        print(f"Generated static cover: {path.relative_to(ROOT)} ({len(svg):,} bytes)")


if __name__ == "__main__":
    main()
