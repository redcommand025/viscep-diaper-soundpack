# Diaper/ABDL soundpack listener

A simple static page for listening to Viscep’s Diaper/ABDL soundpacks, volumes 1 and 2.

All audio in this project was created by **[Viscep](https://viscep.itch.io/)**. The original packs are free on itch.io:

- **Vol. 1:** [https://viscep.itch.io/diaperabdl](https://viscep.itch.io/diaperabdl)
- **Vol. 2:** [https://viscep.itch.io/diaperabdl-soundpack-vol-2](https://viscep.itch.io/diaperabdl-soundpack-vol-2)

Fur Affinity: https://www.furaffinity.net/user/viscep

## Credit and terms

From Viscep’s `Info.txt` in each pack (see `sounds/Info.txt` and `vol2/Info.txt`):

> All of these sounds are made by me (Viscep)
>
> All sounds within are free to use for your animations, games, or what-have-you, whether you use them as-is or edit them
>
> By using my sounds you are agreeing to the following terms:
> - Audio is not to be redistributed or resold
> - Audio may not be used as training data for public machine learning projects / data sets
> - Audio may not be used in any cryptocurrency or blockchain related media
> - Credit is not necessary, but is highly appreciated!

This GitHub repository is **private** on purpose. Do **not** make it public, enable GitHub Pages, or otherwise host the audio on a public site. That would redistribute the packs, which Viscep’s terms forbid. Keep this copy private and personal.

## What’s included

This listener embeds the official MP3 versions only, so the tree stays well under GitHub’s 100 MB per-file limit and the recommended ~1 GB repository size.

| Pack | Location | MP3 files | Size in this repo | WAV set (not copied) |
| --- | --- | --- | --- | --- |
| Vol. 1 | `sounds/` | 1,095 | 186.5 MB | 941.3 MB (16-bit / 44.1 kHz), same clips |
| Vol. 2 | `vol2/` | 118 | 51.5 MB | separate 464 MB zip on itch.io, same clips |

Vol. 1 categories (each with clean, room reverb, and bathroom reverb variants): Filling, Slow filling, Wetting, Moving, Squish, Plap, Pullups, Stomach noises, Toots.

Vol. 2 categories (no reverb variants): Filling (70), Moving (24), Wetting (14), Toots (8), Pullups (2).

## Listening locally

You can open `index.html` directly, but some browsers restrict `file://` audio. Prefer a local server from this directory:

```bash
python3 -m http.server 8080
```

Then visit http://127.0.0.1:8080/

The page has Vol. 1 and Vol. 2 sections, groups clips by folder, gives each one an `<audio controls preload="none">` player, and has a search box that filters across both volumes.

To regenerate `index.html` and `sounds.json` after adding or removing files:

```bash
python3 build_site.py
```
