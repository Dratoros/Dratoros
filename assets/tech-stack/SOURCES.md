# Technology icon sources

These local SVG tiles identify technologies listed in Diego's supplied resume,
the approved profile proposal, and his later skill confirmations. Source artwork is retained in `source/`.
The tiles are assembled by `scripts/generate_tech_stack.py` from `stack.json`.
All SVGs are self-contained and require no external font, script, or image load.

- **Devicon:** React, TypeScript, Python, C#, .NET Core, PostgreSQL, Supabase,
  Redis, Apache Kafka, Docker, Git, GitHub, Linux, Nginx, and n8n.
  [Official repository](https://github.com/devicons/devicon).
  Copyright (c) 2015 konpa. [MIT license](DEVICON-LICENSE.txt).
- **Microsoft Power BI Icons:** Power BI and Power Query.
  [Original Power BI SVG](https://github.com/microsoft/PowerBI-Icons/blob/master/SVG/Power-BI.svg),
  [original Power Query SVG](https://github.com/microsoft/PowerBI-Icons/blob/master/SVG/Power-Query-Colored.svg).
  Microsoft and contributors. [CC BY 4.0 license](MICROSOFT-LICENSE.txt).
  The source drawings are unchanged; they are scaled and placed within a
  rounded tile with a label below.
- **Simple Icons 11.0.0:** Tableau.
  [Original SVG](https://github.com/simple-icons/simple-icons/blob/11.0.0/icons/tableau.svg).
  [CC0 1.0 license](SIMPLE-ICONS-LICENSE.md).
- **SQL:** an original generic database symbol drawn locally. It represents SQL
  as a language, rather than implying experience with an additional database product.

The GitHub and Apache Kafka monochrome marks use a light fill for contrast.
The Tableau monochrome mark uses light blue. Other source colors are preserved.
All cards add a blue/navy rounded background and an English text label.
The .NET Core mark has a light backing so its transparent letter cutouts remain legible.
Per-file upstream URLs and blob hashes are recorded in `sources.json`.
