# Profile artwork

This document describes the files used by the current profile. The final avatar
has short faded hair with a small quiff, a full beard, blue eyes, and a dark
technical jacket over a blue hoodie, with fingerless gloves and cargo trousers.
The blue rune axe appears in all four avatar scenes.

The character artwork was created with the built-in image generation tool,
using Diego's supplied character token and later his photo as identity and
haircut references. Neither personal reference image is included in the
published assets.

## Published images and generation inputs

| Section | Published image | Required source artwork | Generator |
| --- | --- | --- | --- |
| Profile banner | `profile-banner.gif` | Original bitmap alphabet and blue palette in the generator | `scripts/generate_banner.py` |
| About Me | `about-avatar.gif` | `avatar-sprites-hacker.png`, `blue-flame-sprites.png` | `scripts/generate_about.py` |
| Where to find me | `contact-avatar.gif` | `contact-sprites-hacker-axe.png` | `scripts/generate_contacts.py` |
| What do I do | `work-avatar.gif` | `work-sprites-white-monster-axe.png` | `scripts/generate_work.py` |
| Featured Projects | `projects-avatar.gif` | `forge-sprites-hacker.png`, `forge-smoke-sprites.png` | `scripts/generate_projects.py` |
| Project covers | `project-covers/*.svg` | Original bitmap alphabet, blue palette, and vector motifs | `scripts/generate_project_covers.py` |
| Contact buttons | `contacts/*.svg` | Confirmed labels and URLs in `contacts.json` | `scripts/generate_contacts.py` |
| Tech Stack | `tech-stack/*.svg` | `tech-stack/stack.json`, `tech-stack/source/*.svg` | `scripts/generate_tech_stack.py` |

All paths in the image and source columns are relative to `assets/`.
Generator paths are relative to the repository root. Source atlases are needed
to rebuild the GIFs, even though the README does not display them directly.

## Animation and artwork details

- **Profile banner:** original blue cyberpunk terminal and bitmap lettering.
- **About Me:** an axe throw with a full-size spinning axe, blue flames, and the
  ABOUT ME reveal. The airborne axe maintains an approximately 185-pixel diagonal.
- **Where to find me:** one hand holds the axe and the other uses a smartphone.
  The English heading appears letter by letter. The local contact buttons link
  to GitHub, LinkedIn, Email, and Instagram.
- **What do I do:** the avatar types, drinks from a white/silver Monster can,
  and returns to work. The axe stays propped beside the workstation.
- **Featured Projects:** hammering an axe at an anvil, inspecting and blowing
  over the blade, then revealing the heading through drifting blue-gray smoke.

The sprite poses and effects are generated artwork. The Python scripts compose
alignment, movement, sequencing, pixel lettering, and title reveals. GIFs use a
shared palette to prevent flickering between frames.

The exact prompts relevant to the current artwork are retained in:

- [Unified outfit edits](unified-outfit-edit-prompts.txt): final About Me and
  forge clothing, and the shared hacker outfit direction.
- [Axe scene edits](axe-scene-edit-prompts.txt): the current contact and
  workstation sprites, including the contact pose correction.
- [Blue flame artwork](blue-flame-generation-prompt.txt).
- [Forge and smoke artwork](forge-generation-prompts.txt).

Some prompts mention earlier reference sheets as generation history. Those
earlier sheets are not needed by the current generators.

## Static project covers

The two local SVG covers reuse the original palette and bitmap alphabet from
`generate_banner.py`. All lettering is exported as vector rectangles, without
external fonts, images, scripts, services, or animation. Connected modules
represent the construction ERP; map pins over waves represent the fishing
community. These are decorative symbols, not application screenshots.

Each cover links to its repository. Short English descriptions, technology
labels, and text links remain ordinary README content.

## Technology icons and licenses

The local SVG tiles use rounded navy backgrounds and readable English labels.
The categories are Frontend, Backend & Databases, Data & BI, and DevOps, Tools &
Automation. The selected technologies come from Diego's supplied resume and
later confirmations.

Keep the original icon sources, `stack.json`, `sources.json`, and all license
files: these support regeneration and attribution. Source links and licensing
details are in [tech-stack/SOURCES.md](tech-stack/SOURCES.md).

## Regenerate

Install Pillow to run the artwork generators. The technology tile generator
uses only Python's standard library. Run the required command from the root:

```text
python scripts/generate_banner.py
python scripts/generate_about.py
python scripts/generate_contacts.py
python scripts/generate_work.py
python scripts/generate_projects.py
python scripts/generate_project_covers.py
python scripts/generate_tech_stack.py
```

Published GIFs and SVGs go to `assets/`. Static PNG/SVG previews and motion
review sheets go to `tmp/`, which is excluded from Git. Historical artwork
and canceled experiments are also kept only in the ignored local archive.

