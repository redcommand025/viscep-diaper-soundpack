# Diaper/ABDL soundpack listener

A simple static page for listening to [Viscep’s Diaper/ABDL soundpack](https://viscep.itch.io/diaperabdl).

All audio in this project was created by **[Viscep](https://viscep.itch.io/)**. The original pack is free on itch.io:

**https://viscep.itch.io/diaperabdl**

Fur Affinity: https://www.furaffinity.net/user/viscep

## Credit and terms

From Viscep’s `Info.txt` (included in the pack):

> All of these sounds are made by me (Viscep)
>
> All sounds within are free to use for your animations, games, or what-have-you, whether you use them as-is or edit them
>
> By using my sounds you are agreeing to the following terms:
> - Audio is not to be redistributed or resold
> - Audio may not be used as training data for public machine learning projects / data sets
> - Audio may not be used in any cryptocurrency or blockchain related media
> - Credit is not necessary, but is highly appreciated!

This GitHub repository is **private** on purpose. Do **not** make it public, enable GitHub Pages, or otherwise host the audio on a public site. That would redistribute the pack, which Viscep’s terms forbid. Keep this copy private and personal.

## What’s included

The itch.io zip is **876 MB** and unpacks to about **1.13 GB**:

| Version | Files | Size |
| --- | --- | --- |
| MP3 (used by this listener) | 1,095 | 186.5 MB |
| WAV 16-bit / 44.1 kHz (not copied here) | 1,095 | 941.3 MB |

The two versions are the same 1,095 clips. This listener only embeds the MP3s so the tree stays well under GitHub’s 100 MB per-file limit and the recommended ~1 GB repository size. The WAV set would add ~941 MB on its own.

Categories (each with clean, room reverb, and bathroom reverb variants): Filling, Slow filling, Wetting, Moving, Squish, Plap, Pullups, Stomach noises, Toots.

## Listening locally

You can open `index.html` directly, but some browsers restrict `file://` audio. Prefer a local server from this directory:

```bash
python3 -m http.server 8080
```

Then visit http://127.0.0.1:8080/

The page groups clips by folder, gives each one an `<audio controls preload="none">` player, and has a search box to filter by name, category, or reverb.

To regenerate `index.html` and `sounds.json` after adding or removing files under `sounds/`:

```bash
python3 build_site.py
```
