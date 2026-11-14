#!/usr/bin/env python3
"""Generate index.html and sounds.json from the sounds/ tree."""
from __future__ import annotations

import json
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOUNDS = ROOT / "sounds"
AUDIO_EXTS = {".mp3", ".ogg", ".wav", ".m4a", ".opus", ".flac", ".aac"}

# Preferred folder order (pack categories, then any extras alphabetically)
CATEGORY_ORDER = [
    "Filling",
    "Slow filling",
    "Wetting",
    "Moving",
    "Squish",
    "Plap",
    "Pullups",
    "Stomach noises",
    "Toots",
]
REVERB_ORDER = [
    "Clean (no reverb)",
    "Room reverb",
    "Bathroom reverb",
]


def collect() -> list[dict]:
    items = []
    for path in sorted(SOUNDS.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in AUDIO_EXTS:
            continue
        rel = path.relative_to(SOUNDS)
        parts = rel.parts
        if len(parts) >= 3:
            category, variant, name = parts[0], parts[1], parts[-1]
        elif len(parts) == 2:
            category, variant, name = parts[0], "", parts[1]
        else:
            category, variant, name = "Other", "", parts[0]
        items.append(
            {
                "file": rel.as_posix(),
                "name": path.stem,
                "filename": path.name,
                "category": category,
                "variant": variant or "Default",
                "ext": path.suffix.lower().lstrip("."),
                "bytes": path.stat().st_size,
            }
        )
    return items


def sort_key(item: dict):
    cat = item["category"]
    var = item["variant"]
    cidx = CATEGORY_ORDER.index(cat) if cat in CATEGORY_ORDER else 1000
    vidx = REVERB_ORDER.index(var) if var in REVERB_ORDER else 1000
    return (cidx, cat.lower(), vidx, var.lower(), item["name"].lower())


def group(items: list[dict]) -> OrderedDict:
    grouped: OrderedDict = OrderedDict()
    for item in items:
        grouped.setdefault(item["category"], OrderedDict()).setdefault(
            item["variant"], []
        ).append(item)
    return grouped


def fmt_size(n: int) -> str:
    if n < 1024 * 1024:
        return f"{n / 1024:.0f} KB"
    return f"{n / (1024 * 1024):.1f} MB"


def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def render(items: list[dict]) -> str:
    grouped = group(items)
    total = len(items)
    total_bytes = sum(i["bytes"] for i in items)
    cats = len(grouped)

    sections = []
    for cat, variants in grouped.items():
        cat_count = sum(len(v) for v in variants.values())
        variant_blocks = []
        for var, tracks in variants.items():
            rows = []
            for t in tracks:
                src = "sounds/" + t["file"]
                rows.append(
                    f"""            <li class="track" data-name="{esc(t['name'].lower())}" data-file="{esc(t['filename'].lower())}" data-category="{esc(cat.lower())}" data-variant="{esc(var.lower())}">
              <div class="track-meta">
                <span class="track-name">{esc(t['name'])}</span>
                <span class="track-file">{esc(t['filename'])} · {fmt_size(t['bytes'])}</span>
              </div>
              <audio controls preload="none" src="{esc(src)}"></audio>
            </li>"""
                )
            variant_blocks.append(
                f"""        <details class="variant" open>
          <summary><span class="variant-name">{esc(var)}</span><span class="count">{len(tracks)}</span></summary>
          <ul class="tracks">
{chr(10).join(rows)}
          </ul>
        </details>"""
            )
        sections.append(
            f"""      <section class="category" data-category="{esc(cat.lower())}" data-label="{esc(cat)}">
        <h2>{esc(cat)} <span class="count">{cat_count}</span></h2>
{chr(10).join(variant_blocks)}
      </section>"""
        )

    body_sections = "\n".join(sections)
    manifest_note = f"{total} sounds · {cats} categories · {fmt_size(total_bytes)}"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Diaper/ABDL soundpack — Viscep</title>
  <meta name="description" content="Listener for Viscep's Diaper/ABDL soundpack. All sounds by Viscep." />
  <style>
    :root {{
      --bg: #12150f;
      --bg-raise: #1b2018;
      --bg-row: #22281e;
      --line: #32392c;
      --ink: #e8e3d4;
      --muted: #9a937e;
      --accent: #c4b07a;
      --accent-dim: #8f7e4d;
      --focus: #d9c88a;
    }}
    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; padding: 0; }}
    body {{
      font-family: "Iowan Old Style", "Palatino Linotype", Palatino, "Book Antiqua", Georgia, serif;
      background:
        radial-gradient(1200px 500px at 10% -10%, #2a3322 0%, transparent 55%),
        var(--bg);
      color: var(--ink);
      line-height: 1.5;
      min-height: 100vh;
    }}
    a {{ color: var(--accent); }}
    a:hover {{ color: var(--focus); }}
    .wrap {{
      max-width: 920px;
      margin: 0 auto;
      padding: 2.5rem 1.25rem 5rem;
    }}
    header {{
      border-bottom: 1px solid var(--line);
      padding-bottom: 1.75rem;
      margin-bottom: 1.5rem;
    }}
    .eyebrow {{
      font-family: ui-sans-serif, system-ui, sans-serif;
      letter-spacing: 0.16em;
      text-transform: uppercase;
      font-size: 0.68rem;
      color: var(--accent);
      margin: 0 0 0.6rem;
    }}
    h1 {{
      font-weight: 600;
      font-size: clamp(1.8rem, 4vw, 2.6rem);
      letter-spacing: -0.02em;
      margin: 0 0 0.6rem;
      line-height: 1.15;
    }}
    .lede {{
      color: var(--muted);
      margin: 0 0 0.85rem;
      max-width: 40rem;
    }}
    .stats {{
      font-family: ui-sans-serif, system-ui, sans-serif;
      font-size: 0.8rem;
      color: var(--muted);
    }}
    .toolbar {{
      position: sticky;
      top: 0;
      z-index: 5;
      background: color-mix(in srgb, var(--bg) 88%, transparent);
      backdrop-filter: blur(10px);
      padding: 0.85rem 0;
      margin: 0 0 1.25rem;
      border-bottom: 1px solid var(--line);
    }}
    #q {{
      width: 100%;
      font: inherit;
      font-family: ui-sans-serif, system-ui, sans-serif;
      font-size: 1rem;
      padding: 0.7rem 0.9rem;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--bg-raise);
      color: var(--ink);
      outline: none;
    }}
    #q:focus {{ border-color: var(--accent-dim); box-shadow: 0 0 0 3px color-mix(in srgb, var(--accent) 25%, transparent); }}
    #status {{
      font-family: ui-sans-serif, system-ui, sans-serif;
      font-size: 0.8rem;
      color: var(--muted);
      margin: 0.55rem 0 0;
      min-height: 1.2em;
    }}
    .category {{
      background: var(--bg-raise);
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 1rem 1rem 0.4rem;
      margin: 0 0 1rem;
    }}
    .category h2 {{
      font-size: 1.25rem;
      font-weight: 600;
      margin: 0 0 0.65rem;
      display: flex;
      align-items: baseline;
      gap: 0.55rem;
    }}
    .count {{
      font-family: ui-sans-serif, system-ui, sans-serif;
      font-size: 0.72rem;
      font-weight: 600;
      color: var(--bg);
      background: var(--accent);
      border-radius: 999px;
      padding: 0.1rem 0.5rem;
      letter-spacing: 0.02em;
    }}
    .variant {{
      border-top: 1px solid var(--line);
      padding: 0.2rem 0 0.35rem;
    }}
    .variant summary {{
      cursor: pointer;
      list-style: none;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.55rem 0.15rem;
      font-family: ui-sans-serif, system-ui, sans-serif;
      font-size: 0.85rem;
      color: var(--muted);
      user-select: none;
    }}
    .variant summary::-webkit-details-marker {{ display: none; }}
    .variant-name {{ color: var(--ink); }}
    .variant summary::before {{
      content: "";
      width: 0.4rem;
      height: 0.4rem;
      border-right: 2px solid var(--accent-dim);
      border-bottom: 2px solid var(--accent-dim);
      transform: rotate(-45deg);
      transition: transform 0.15s ease;
      margin-right: 0.15rem;
    }}
    .variant[open] summary::before {{ transform: rotate(45deg); }}
    .tracks {{
      list-style: none;
      margin: 0;
      padding: 0 0 0.4rem;
    }}
    .track {{
      display: grid;
      grid-template-columns: minmax(8rem, 1fr) minmax(12rem, 1.4fr);
      gap: 0.6rem 1rem;
      align-items: center;
      padding: 0.55rem 0.4rem;
      border-radius: 8px;
    }}
    .track:nth-child(odd) {{ background: var(--bg-row); }}
    .track-name {{ display: block; font-size: 0.98rem; }}
    .track-file {{
      display: block;
      font-family: ui-sans-serif, system-ui, sans-serif;
      font-size: 0.72rem;
      color: var(--muted);
    }}
    audio {{
      width: 100%;
      height: 2.1rem;
    }}
    .hidden {{ display: none !important; }}
    footer {{
      margin-top: 2rem;
      padding-top: 1rem;
      border-top: 1px solid var(--line);
      color: var(--muted);
      font-size: 0.88rem;
    }}
    @media (max-width: 680px) {{
      .track {{ grid-template-columns: 1fr; gap: 0.3rem; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <p class="eyebrow">Soundpack listener</p>
      <h1>Diaper/ABDL soundpack</h1>
      <p class="lede">
        Sounds by <a href="https://viscep.itch.io/diaperabdl">Viscep</a>.
        This page is a personal listener for the free pack published on
        <a href="https://viscep.itch.io/diaperabdl">itch.io</a>.
        Please follow Viscep’s terms: free to use in your own work; do not redistribute or resell the audio.
      </p>
      <p class="stats">{esc(manifest_note)} · MP3 versions (WAV originals are in the itch.io zip)</p>
    </header>
    <div class="toolbar">
      <label for="q" class="visually-hidden" style="position:absolute;left:-9999px">Search sounds</label>
      <input id="q" type="search" placeholder="Filter by name, category, or reverb…" autocomplete="off" />
      <p id="status"></p>
    </div>
    <main id="library">
{body_sections}
    </main>
    <footer>
      <p>All audio © Viscep. Source pack: <a href="https://viscep.itch.io/diaperabdl">viscep.itch.io/diaperabdl</a>. Credit is appreciated but not required by the author. Regenerated with <code>python3 build_site.py</code>.</p>
    </footer>
  </div>
  <script>
    const q = document.getElementById("q");
    const status = document.getElementById("status");
    const tracks = [...document.querySelectorAll(".track")];
    const total = tracks.length;

    function apply() {{
      const needle = q.value.trim().toLowerCase();
      let shown = 0;
      for (const el of tracks) {{
        const hay = [
          el.dataset.name,
          el.dataset.file,
          el.dataset.category,
          el.dataset.variant
        ].join(" ");
        const ok = !needle || hay.includes(needle);
        el.classList.toggle("hidden", !ok);
        if (ok) shown += 1;
      }}
      for (const variant of document.querySelectorAll(".variant")) {{
        const any = variant.querySelector(".track:not(.hidden)");
        variant.classList.toggle("hidden", !any);
      }}
      for (const cat of document.querySelectorAll(".category")) {{
        const any = cat.querySelector(".track:not(.hidden)");
        cat.classList.toggle("hidden", !any);
      }}
      status.textContent = needle
        ? (shown + " of " + total + " sounds match")
        : (total + " sounds");
    }}
    q.addEventListener("input", apply);
    apply();

    // Only one clip at a time so previews don't overlap.
    document.getElementById("library").addEventListener("play", (event) => {{
      const current = event.target;
      if (current.tagName !== "AUDIO") return;
      for (const audio of document.querySelectorAll("audio")) {{
        if (audio !== current) audio.pause();
      }}
    }}, true);
  </script>
</body>
</html>
"""


def main() -> None:
    items = collect()
    items.sort(key=sort_key)
    if not items:
        raise SystemExit("No audio files found under sounds/")
    (ROOT / "sounds.json").write_text(
        json.dumps(
            {
                "title": "Diaper/ABDL soundpack",
                "author": "Viscep",
                "source": "https://viscep.itch.io/diaperabdl",
                "count": len(items),
                "bytes": sum(i["bytes"] for i in items),
                "sounds": items,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    html = render(items)
    (ROOT / "index.html").write_text(html, encoding="utf-8")
    print(f"Wrote index.html and sounds.json ({len(items)} sounds)")


if __name__ == "__main__":
    main()
