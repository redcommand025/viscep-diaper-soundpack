#!/usr/bin/env python3
"""Generate index.html and sounds.json from the vol. 1 and vol. 2 trees."""
from __future__ import annotations

import json
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AUDIO_EXTS = {".mp3", ".ogg", ".wav", ".m4a", ".opus", ".flac", ".aac"}

VOLUMES = [
    {
        "id": "vol1",
        "title": "Vol. 1",
        "dir": "sounds",
        "source": "https://viscep.itch.io/diaperabdl",
        "source_label": "Diaper/ABDL soundpack",
    },
    {
        "id": "vol2",
        "title": "Vol. 2",
        "dir": "vol2",
        "source": "https://viscep.itch.io/diaperabdl-soundpack-vol-2",
        "source_label": "Diaper/ABDL soundpack vol. 2",
    },
]

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
VOLUME_INDEX = {v["id"]: i for i, v in enumerate(VOLUMES)}


def collect() -> list[dict]:
    items = []
    for vol in VOLUMES:
        base = ROOT / vol["dir"]
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in AUDIO_EXTS:
                continue
            rel = path.relative_to(base)
            parts = rel.parts
            if len(parts) >= 3:
                category, variant = parts[0], parts[1]
            elif len(parts) == 2:
                category, variant = parts[0], ""
            else:
                category, variant = "Other", ""
            items.append(
                {
                    "file": f"{vol['dir']}/{rel.as_posix()}",
                    "name": path.stem,
                    "filename": path.name,
                    "volume": vol["id"],
                    "volume_title": vol["title"],
                    "source": vol["source"],
                    "category": category,
                    "variant": variant,
                    "ext": path.suffix.lower().lstrip("."),
                    "bytes": path.stat().st_size,
                }
            )
    return items


def sort_key(item: dict):
    cat = item["category"]
    var = item["variant"]
    vidx_vol = VOLUME_INDEX.get(item["volume"], 1000)
    cidx = CATEGORY_ORDER.index(cat) if cat in CATEGORY_ORDER else 1000
    ridx = REVERB_ORDER.index(var) if var in REVERB_ORDER else 1000
    return (vidx_vol, cidx, cat.lower(), ridx, var.lower(), item["name"].lower())


def group(items: list[dict]) -> OrderedDict:
    grouped: OrderedDict = OrderedDict()
    for item in items:
        grouped.setdefault(item["volume"], OrderedDict()).setdefault(
            item["category"], OrderedDict()
        ).setdefault(item["variant"], []).append(item)
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


def render_tracks(tracks: list[dict]) -> str:
    rows = []
    for t in tracks:
        var = t["variant"]
        rows.append(
            f"""            <li class="track" data-name="{esc(t['name'].lower())}" data-file="{esc(t['filename'].lower())}" data-category="{esc(t['category'].lower())}" data-variant="{esc(var.lower())}" data-volume="{esc(t['volume_title'].lower())}">
              <div class="track-meta">
                <span class="track-name">{esc(t['name'])}</span>
                <span class="track-file">{esc(t['filename'])} · {fmt_size(t['bytes'])}</span>
              </div>
              <audio controls preload="none" src="{esc(t['file'])}"></audio>
            </li>"""
        )
    return "\n".join(rows)


def render(items: list[dict]) -> str:
    grouped = group(items)
    total = len(items)
    total_bytes = sum(i["bytes"] for i in items)
    vol_meta = {v["id"]: v for v in VOLUMES}

    volume_blocks = []
    toc = []
    for vol_id, categories in grouped.items():
        meta = vol_meta[vol_id]
        vol_count = sum(
            len(tracks)
            for variants in categories.values()
            for tracks in variants.values()
        )
        vol_bytes = sum(
            t["bytes"]
            for variants in categories.values()
            for tracks in variants.values()
            for t in tracks
        )
        toc.append(
            f'<a href="#{esc(vol_id)}">{esc(meta["title"])} <span class="count">{vol_count}</span></a>'
        )
        cat_sections = []
        for cat, variants in categories.items():
            cat_count = sum(len(v) for v in variants.values())
            real_variants = [v for v in variants if v]
            if real_variants:
                inner_parts = []
                for var, tracks in variants.items():
                    label = var or "Default"
                    inner_parts.append(
                        f"""        <details class="variant" open>
          <summary><span class="variant-name">{esc(label)}</span><span class="count">{len(tracks)}</span></summary>
          <ul class="tracks">
{render_tracks(tracks)}
          </ul>
        </details>"""
                    )
                inner = "\n".join(inner_parts)
            else:
                only = next(iter(variants.values()))
                inner = f"""        <ul class="tracks">
{render_tracks(only)}
        </ul>"""
            cat_sections.append(
                f"""      <section class="category" data-category="{esc(cat.lower())}" data-volume="{esc(meta['title'].lower())}" data-label="{esc(cat)}">
        <h3>{esc(cat)} <span class="count">{cat_count}</span></h3>
{inner}
      </section>"""
            )
        volume_blocks.append(
            f"""    <section class="volume" id="{esc(vol_id)}" data-volume="{esc(meta['title'].lower())}">
      <div class="volume-head">
        <h2>{esc(meta['title'])} <span class="count">{vol_count}</span></h2>
        <p class="volume-meta">{fmt_size(vol_bytes)} · source: <a href="{esc(meta['source'])}">{esc(meta['source_label'])}</a></p>
      </div>
{chr(10).join(cat_sections)}
    </section>"""
        )

    body_sections = "\n".join(volume_blocks)
    toc_html = " · ".join(toc)
    vol_count = len(grouped)
    manifest_note = f"{total} sounds · {vol_count} volumes · {fmt_size(total_bytes)}"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Diaper/ABDL soundpack — Viscep</title>
  <meta name="description" content="Listener for Viscep's Diaper/ABDL soundpacks, volumes 1 and 2. All sounds by Viscep." />
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
      max-width: 42rem;
    }}
    .stats, .toc {{
      font-family: ui-sans-serif, system-ui, sans-serif;
      font-size: 0.8rem;
      color: var(--muted);
    }}
    .toc {{ margin: 0.4rem 0 0; }}
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
    .volume {{
      margin: 0 0 2rem;
    }}
    .volume-head {{
      margin: 0 0 0.85rem;
      padding-bottom: 0.6rem;
      border-bottom: 1px solid var(--line);
    }}
    .volume-head h2 {{
      font-size: 1.55rem;
      font-weight: 600;
      margin: 0 0 0.25rem;
      display: flex;
      align-items: baseline;
      gap: 0.55rem;
    }}
    .volume-meta {{
      margin: 0;
      color: var(--muted);
      font-size: 0.9rem;
    }}
    .category {{
      background: var(--bg-raise);
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 1rem 1rem 0.4rem;
      margin: 0 0 1rem;
    }}
    .category h3 {{
      font-size: 1.2rem;
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
        Sounds by <a href="https://viscep.itch.io/">Viscep</a>.
        This page is a personal listener for the free packs published on itch.io:
        <a href="https://viscep.itch.io/diaperabdl">Vol. 1</a>
        and
        <a href="https://viscep.itch.io/diaperabdl-soundpack-vol-2">Vol. 2</a>.
        Please follow Viscep’s terms: free to use in your own work; do not redistribute or resell the audio.
      </p>
      <p class="stats">{esc(manifest_note)} · MP3 versions (WAV originals stay in the itch.io zips)</p>
      <p class="toc">{toc_html}</p>
    </header>
    <div class="toolbar">
      <label for="q" class="visually-hidden" style="position:absolute;left:-9999px">Search sounds</label>
      <input id="q" type="search" placeholder="Filter by name, volume, category, or reverb…" autocomplete="off" />
      <p id="status"></p>
    </div>
    <main id="library">
{body_sections}
    </main>
    <footer>
      <p>All audio © Viscep. Sources:
        <a href="https://viscep.itch.io/diaperabdl">vol. 1</a>
        and
        <a href="https://viscep.itch.io/diaperabdl-soundpack-vol-2">vol. 2</a>.
        Credit is appreciated but not required by the author. Regenerated with <code>python3 build_site.py</code>.</p>
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
          el.dataset.variant,
          el.dataset.volume
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
      for (const vol of document.querySelectorAll(".volume")) {{
        const any = vol.querySelector(".track:not(.hidden)");
        vol.classList.toggle("hidden", !any);
      }}
      status.textContent = needle
        ? (shown + " of " + total + " sounds match")
        : (total + " sounds");
    }}
    q.addEventListener("input", apply);
    apply();

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
        raise SystemExit("No audio files found")
    (ROOT / "sounds.json").write_text(
        json.dumps(
            {
                "title": "Diaper/ABDL soundpack",
                "author": "Viscep",
                "sources": [
                    {"id": v["id"], "title": v["title"], "url": v["source"]}
                    for v in VOLUMES
                ],
                "count": len(items),
                "bytes": sum(i["bytes"] for i in items),
                "sounds": items,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (ROOT / "index.html").write_text(render(items), encoding="utf-8")
    by_vol = {}
    for i in items:
        by_vol.setdefault(i["volume"], 0)
        by_vol[i["volume"]] += 1
    print(f"Wrote index.html and sounds.json ({len(items)} sounds: {by_vol})")


if __name__ == "__main__":
    main()
