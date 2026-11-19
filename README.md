# Walsh Equity — social graphics

Public, permanent image URLs for Walsh Equity social posts (Buffer pulls images from here at publish time).

- `posts/YYYY-MM-DD/N.png` — daily post graphics (1080×1350). **Never move, rename or delete** a file after its post is scheduled.
- `tools/render.py` — renders Design-canvas artboards (`.dc.html`) to PNG with bundled fonts/logo:
  `python3 tools/render.py canvas.dc.html posts/YYYY-MM-DD`
- `assets/` — Manrope + Roboto Slab (OFL, via Fontsource) and the gold logo.

Image URL pattern: `https://raw.githubusercontent.com/walshequity/social/main/posts/YYYY-MM-DD/N.png`

## Website feed
`posts/index.json` is the "Our market notes" feed on walshequity.com (read live by the site, no redeploy).
Whoever schedules a LinkedIn post adds its entry with `python3 tools/notes.py add note.json` in the same commit as the graphic,
with `publishAt` = the scheduled time so the site hides it until the post goes out. `python3 tools/notes.py check` validates.
Nothing else writes this file: if a post isn't added here, it never shows on the site.
