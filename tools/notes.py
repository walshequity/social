#!/usr/bin/env python3
"""Add a day's posts to posts/index.json — the feed walshequity.com reads for "Our market notes".

Usage:
  python3 tools/notes.py add posts.json        # posts.json = list of entries (see below)
  python3 tools/notes.py check                 # validate index.json and that every image file exists

Entry fields: date (YYYY-MM-DD, Eastern date the post goes out), order (1, 2, ... within that date),
slot ("Florida"/"National"), headline, summary (1–2 sentences), image (raw.githubusercontent.com URL of a .png/.gif
in posts/), alt, sourceName, sourceUrl, publishAt (optional ISO 8601 with offset, e.g. 2026-11-20T12:15:00-05:00:
the site hides the note until then, so add it when the post is scheduled).
Entries are keyed by (date, order): re-adding the same day replaces those entries, nothing else is touched.
Keeps the newest 180 entries.
"""
import datetime, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
INDEX = ROOT / "posts" / "index.json"
RAW = "https://raw.githubusercontent.com/walshequity/social/main/"
REQUIRED = ("date", "order", "headline", "image")
KEEP = 180


def load():
    return json.loads(INDEX.read_text()) if INDEX.exists() else {"updated": None, "posts": []}


def validate(e):
    for k in REQUIRED:
        if not e.get(k):
            raise SystemExit(f"entry missing {k}: {e}")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", e["date"]):
        raise SystemExit(f"bad date: {e['date']}")
    if not e["image"].startswith(RAW + "posts/"):
        raise SystemExit(f"image must be a {RAW}posts/... URL: {e['image']}")
    if not (ROOT / e["image"][len(RAW):]).exists():
        raise SystemExit(f"image file not in repo: {e['image'][len(RAW):]}")
    if e.get("publishAt"):
        try:
            datetime.datetime.fromisoformat(e["publishAt"].replace("Z", "+00:00"))
        except ValueError:
            raise SystemExit(f"bad publishAt: {e['publishAt']}")
    for k in ("sourceUrl",):
        if e.get(k) and not e[k].startswith("https://"):
            raise SystemExit(f"{k} must be https: {e[k]}")


def save(doc):
    doc["posts"].sort(key=lambda p: (p["date"], -int(p.get("order", 0))), reverse=True)
    doc["posts"] = doc["posts"][:KEEP]
    doc["updated"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    INDEX.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("add", "check"):
        raise SystemExit(__doc__)
    doc = load()
    if sys.argv[1] == "check":
        for e in doc["posts"]:
            validate(e)
        print(f"ok: {len(doc['posts'])} entries")
        return
    new = json.loads(pathlib.Path(sys.argv[2]).read_text())
    for e in new:
        e["order"] = int(e["order"])
        validate(e)
    keys = {(e["date"], e["order"]) for e in new}
    doc["posts"] = [p for p in doc["posts"] if (p["date"], int(p.get("order", 0))) not in keys] + new
    save(doc)
    print(f"index.json: {len(doc['posts'])} entries ({len(new)} added/replaced)")


if __name__ == "__main__":
    main()
