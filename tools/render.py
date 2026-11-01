#!/usr/bin/env python3
"""Render Walsh Equity Design-canvas artboards to PNG.

Usage:
  python3 tools/render.py <canvas.dc.html> <out_dir> [--logo-blob <blob_path_or_id>]

- Finds every top-level artboard: a div with an inline `width: 1080px; height: 1350px`
  inside <x-dc> (or the whole <body> if there is no <x-dc>).
- Replaces Google Fonts links with the bundled fonts in assets/fonts.
- Replaces /_blob/... image sources with assets/logo-gold.png.
- Writes <out_dir>/1.png, 2.png, ... at 1080x1350 (device scale 1).
"""
import argparse, base64, pathlib, re, sys
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONTS = ROOT / "assets" / "fonts"
LOGO = ROOT / "assets" / "logo-gold.png"

FACES = [("Manrope", w, f"manrope-latin-{w}-normal.woff2") for w in (400, 500, 600, 700, 800)] + \
        [("Roboto Slab", w, f"roboto-slab-latin-{w}-normal.woff2") for w in (300, 400, 500)]


def font_css() -> str:
    out = []
    for fam, w, f in FACES:
        data = base64.b64encode((FONTS / f).read_bytes()).decode()
        out.append(f"@font-face{{font-family:'{fam}';font-weight:{w};font-style:normal;"
                   f"src:url(data:font/woff2;base64,{data}) format('woff2');}}")
    return "\n".join(out)


def extract(html: str):
    m = re.search(r"<x-dc>(.*)</x-dc>", html, re.S)
    body = m.group(1) if m else re.search(r"<body[^>]*>(.*)</body>", html, re.S).group(1)
    styles = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", body, re.S))
    body = re.sub(r"<helmet>.*?</helmet>", "", body, flags=re.S)
    body = re.sub(r"<script.*?</script>", "", body, flags=re.S)
    body = re.sub(r"<link[^>]*>", "", body)
    logo = "data:image/png;base64," + base64.b64encode(LOGO.read_bytes()).decode()
    body = re.sub(r'src="/_blob/[^"]*"', f'src="{logo}"', body)
    return styles, body


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("canvas")
    ap.add_argument("out_dir")
    a = ap.parse_args()
    styles, body = extract(pathlib.Path(a.canvas).read_text(encoding="utf-8"))
    page_html = (f"<!doctype html><html><head><meta charset='utf-8'><style>{font_css()}\n"
                 f"html,body{{margin:0;padding:0;background:#10231d}}\n{styles}</style></head>"
                 f"<body>{body}</body></html>")
    out = pathlib.Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"]) \
            if pathlib.Path("/usr/bin/google-chrome").exists() else p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
        pg.set_content(page_html, wait_until="load")
        pg.evaluate("document.fonts.ready")
        boards = pg.query_selector_all("body div[style*='width: 1080px'][style*='height: 1350px'], "
                                       "body div[style*='width:1080px'][style*='height:1350px']")
        boards = [x for x in boards if not x.evaluate(
            "e => !!e.parentElement.closest(\"div[style*='1350px']\")")]
        if not boards:
            sys.exit("no 1080x1350 artboards found")
        for i, el in enumerate(boards, 1):
            el.screenshot(path=str(out / f"{i}.png"))
            print(out / f"{i}.png")
        b.close()


if __name__ == "__main__":
    main()
