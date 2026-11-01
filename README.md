# Walsh Equity — social graphics

Public, permanent image URLs for Walsh Equity social posts (Buffer pulls images from here at publish time).

- `posts/YYYY-MM-DD/N.png` — daily post graphics (1080×1350). **Never move, rename or delete** a file after its post is scheduled.
- `tools/render.py` — renders Design-canvas artboards (`.dc.html`) to PNG with bundled fonts/logo:
  `python3 tools/render.py canvas.dc.html posts/YYYY-MM-DD`
- `assets/` — Manrope + Roboto Slab (OFL, via Fontsource) and the gold logo.

Image URL pattern: `https://raw.githubusercontent.com/walshequity/social/main/posts/YYYY-MM-DD/N.png`

## Website feed
`posts/index.json` is the "Our market notes" feed on walshequity.com (read live by the site, no redeploy).
The daily task adds each day's entries with `python3 tools/notes.py add today.json`; `python3 tools/notes.py check` validates.
