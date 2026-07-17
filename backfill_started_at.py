"""
backfill_started_at.py  --  fill missing started_at dates from the Goodreads data export

analysis.py currently guesses started_at = read_at - 14 days whenever it's blank.
The full Goodreads data export (Settings > Account > Data > Export, unzipped into
OneDrive) has one reliable source for a better date:

  activity.json  -- newsfeed events. A "BookStatusReading" entry fires the moment
                     a book is marked as currently-reading, with an exact
                     timestamp. Goodreads only retains a couple of years of this
                     feed though, so coverage is sparse (recent books only).

Note: grass.json (Kindle highlights/"citations") looked promising -- each
citation carries a created_date -- but every highlight for a given book shares
exactly one identical timestamp (e.g. all 14 Dune citations = the same
second). That's a bulk-sync/import timestamp for when Goodreads pulled the
book's notes from Amazon, not when you actually made each highlight, so it's
not usable as a reading-start proxy. Confirmed by many resulting dates falling
*after* the book's read_at, which is impossible. Left out entirely.

Only fills started_at cells that are currently blank; never touches a value
that's already there (mirrors annotate_books.py's fill-only-if-blank rule), and
never touches any other column.

Run:  python backfill_started_at.py
"""

import json
import os
import re
from datetime import datetime

import pandas as pd

BOOKS_FILE = "books_annotated.csv"
GOODREADS_EXPORT_DIR = r"C:\Users\bdoherty\OneDrive - BVN\Goodreads"


def _parse_gr_timestamp(s: str):
    """Parse the export's 'YYYY-MM-DD HH:MM:SS UTC' timestamp strings."""
    if not s:
        return None
    try:
        return datetime.strptime(s.replace(" UTC", ""), "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None


def normalise(title: str) -> str:
    """Lowercase, collapse whitespace, normalise apostrophes -- for title matching."""
    s = str(title).lower().strip()
    s = s.replace("’", "'").replace("‘", "'")
    s = re.sub(r"\s+", " ", s)
    return s


def _earliest_by_title(records, title_key: str, date_key: str) -> dict:
    result = {}
    for r in records:
        title = normalise(r.get(title_key, ""))
        ts = _parse_gr_timestamp(r.get(date_key, ""))
        if not title or ts is None:
            continue
        if title not in result or ts < result[title]:
            result[title] = ts
    return result


def load_activity_started_at(export_dir: str) -> dict:
    """title (normalised) -> earliest 'BookStatusReading' timestamp."""
    path = os.path.join(export_dir, "activity", "activity.json")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    activities = next((block["activities"] for block in data if "activities" in block), [])
    reading_events = [a for a in activities if a.get("activity_type") == "BookStatusReading"]
    return _earliest_by_title(reading_events, "product", "created_at")


def main():
    books = pd.read_csv(BOOKS_FILE, dtype=str, keep_default_na=False)

    print(f"Loading Goodreads export from '{GOODREADS_EXPORT_DIR}' …")
    activity_map = load_activity_started_at(GOODREADS_EXPORT_DIR)
    print(f"  {len(activity_map)} titles with a 'started reading' activity event")

    filled_activity = 0
    for idx, row in books.iterrows():
        if row["started_at"].strip():
            continue
        key = normalise(row["title"])
        if key in activity_map:
            books.at[idx, "started_at"] = activity_map[key].strftime("%Y-%m-%d")
            filled_activity += 1

    print(f"\n  filled {filled_activity} started_at from activity log (exact)")
    still_missing = (books["started_at"].str.strip() == "") & (books["read_at"].str.strip() != "")
    print(f"  {still_missing.sum()} still blank -- analysis.py will fall back to read_at - 14 days for these")

    books.to_csv(BOOKS_FILE, index=False)
    print(f"\nWrote '{BOOKS_FILE}'")


if __name__ == "__main__":
    main()
