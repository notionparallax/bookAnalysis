"""
ingest.py  —  Goodreads CSV export → books_annotated.xlsx

Steps:
  1. Export your Goodreads library:
       Goodreads → My Books → Import and Export → Export Library
  2. Save the downloaded file as  goodreads_export.csv  in this folder
     (or update EXPORT_FILE below)
  3. Run:  python ingest.py

Outputs:
  books_annotated.xlsx  — all books on the 'read' shelf with blank annotation
                          columns ready for you to fill in manually
"""

import os

import pandas as pd
from dateutil import parser as dateparser

# ── Config ────────────────────────────────────────────────────────────────────
EXPORT_FILE = "goodreads_library_export.csv"
OLD_RAW_FILE = "raw_books"        # legacy API snapshot used to recover started_at dates

ONEDRIVE_DIR = r"C:\Users\bdoherty\OneDrive - BVN\book_analysis"
OUTPUT_CSV = "books_annotated.csv"          # system output → CSV in repo
AUTHORS_XLSX = rf"{ONEDRIVE_DIR}\authors.xlsx"  # manually edited → xlsx in OneDrive

# ── Goodreads CSV column → internal name ──────────────────────────────────────
GR_COLUMN_MAP = {
    "Book Id": "book_id",
    "Title": "title",
    "Author": "author_1_name",
    "ISBN": "isbn",
    "ISBN13": "isbn13",
    "My Rating": "rating",
    "Average Rating": "avg_rating",
    "Publisher": "publisher",
    "Binding": "format",
    "Number of Pages": "num_pages",
    "Original Publication Year": "publication_year",
    "Date Read": "read_at",
    "Date Added": "date_added",
    "Bookshelves": "bookshelves",
    "Exclusive Shelf": "shelf",
    "Read Count": "read_count",
}


def _safe_parse_date(value) -> pd.Timestamp:
    """Parse a date string to a Timestamp; return NaT on failure or blank."""
    if pd.isna(value) or str(value).strip() == "":
        return pd.NaT
    try:
        return pd.Timestamp(dateparser.parse(str(value)))
    except Exception:
        return pd.NaT


def load_goodreads_export(path: str) -> pd.DataFrame:
    """Read a Goodreads CSV export and normalise to the internal schema."""
    df = pd.read_csv(path, dtype=str)

    rename = {k: v for k, v in GR_COLUMN_MAP.items() if k in df.columns}
    df = df.rename(columns=rename)
    keep = [v for k, v in GR_COLUMN_MAP.items() if v in df.columns]
    df = df[keep].copy()

    # Strip Excel formula wrapper from ISBN columns: ="9780123..." → 9780123...
    for col in ("isbn", "isbn13"):
        if col in df.columns:
            df[col] = df[col].str.replace(r'^="?(.*?)"?$', r'\1', regex=True)
            df[col] = df[col].where(df[col].str.fullmatch(r"[0-9X]{10,13}"), other=None)

    # Coerce numerics
    for col in ("rating", "avg_rating", "num_pages", "publication_year", "read_count"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Normalise author name whitespace
    if "author_1_name" in df.columns:
        df["author_1_name"] = df["author_1_name"].str.strip().str.replace(r"\s+", " ", regex=True)

    # Parse dates
    for col in ("read_at", "date_added"):
        if col in df.columns:
            df[col] = df[col].apply(_safe_parse_date)

    # Keep only books on the 'read' shelf
    if "shelf" in df.columns:
        df = df[df["shelf"] == "read"].copy()
        df = df.drop(columns=["shelf"])

    df = df.reset_index(drop=True)
    return df


def load_legacy_started_at(path: str) -> dict:
    """
    Extract {title: started_at Timestamp} from the old API-exported raw_books file
    so we can backfill start dates that aren't in the Goodreads CSV export.
    Only returns rows that have a genuine (non-blank, post-2010) start date.
    """
    if not os.path.exists(path):
        return {}
    try:
        old = pd.read_csv(path, dtype=str, on_bad_lines="skip")
    except TypeError:
        # pandas < 1.3 used error_bad_lines
        old = pd.read_csv(path, dtype=str, error_bad_lines=False)  # noqa: FBT003

    if "started_at" not in old.columns or "title" not in old.columns:
        return {}

    result = {}
    cutoff = pd.Timestamp("2010-01-01")
    for _, row in old.iterrows():
        title = str(row.get("title", "")).strip()
        raw = row.get("started_at", "")
        if not title or not raw or str(raw).strip() == "":
            continue
        ts = _safe_parse_date(raw)
        if ts is pd.NaT:
            continue
        # Normalise to tz-naive for comparison
        ts_naive = ts.tz_localize(None) if ts.tzinfo is not None else ts
        if ts_naive > cutoff:
            result[title] = ts_naive
    return result


def build_annotated(df: pd.DataFrame, started_at_map: dict) -> pd.DataFrame:
    """
    Insert the started_at column (pre-filled from legacy data where available)
    and add blank manual-annotation columns.
    """
    df = df.copy()

    # Insert started_at just before read_at
    read_at_pos = df.columns.get_loc("read_at")
    df.insert(read_at_pos, "started_at", df["title"].map(started_at_map))

    # Manual annotation columns — fill these in Excel before running analysis.py
    for col in ("ficOrNonFic", "SeriesOrStandalone", "LGBTQIA_Characters"):
        df[col] = ""

    return df


def write_authors_template(path: str):
    """
    If no authors xlsx exists yet in OneDrive, write a blank template.
    """
    if os.path.exists(path):
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    template = pd.DataFrame(
        columns=["name", "gender", "ethnicity", "DeadorAlive", "Nationality", "LGBTQI_Authors"]
    )
    template.to_excel(path, index=False)
    print(f"  Created blank authors template at '{path}'")


def main():
    if not os.path.exists(EXPORT_FILE):
        raise FileNotFoundError(
            f"Goodreads export not found: '{EXPORT_FILE}'\n\n"
            "To export your library:\n"
            "  Goodreads → My Books → Import and Export → Export Library\n"
            "Save the downloaded file as 'goodreads_export.csv' in this folder."
        )

    print(f"Loading Goodreads export from '{EXPORT_FILE}' …")
    books = load_goodreads_export(EXPORT_FILE)
    print(f"  {len(books)} books on 'read' shelf")

    print(f"Loading legacy started_at dates from '{OLD_RAW_FILE}' …")
    started_at_map = load_legacy_started_at(OLD_RAW_FILE)
    matched = sum(1 for t in books["title"] if t in started_at_map)
    print(f"  {len(started_at_map)} legacy dates available, {matched} matched to current titles")

    books = build_annotated(books, started_at_map)

    print(f"Writing '{OUTPUT_CSV}' …")
    books.to_csv(OUTPUT_CSV, index=False, date_format="%Y-%m-%d")

    print("Checking authors template …")
    write_authors_template(AUTHORS_XLSX)

    print("\nDone!")
    print()
    print("Next steps:")
    print(f"  1. Open {OUTPUT_CSV} and fill in the annotation columns:")
    print("       ficOrNonFic        — e.g. Fiction / Non-Fiction")
    print("       SeriesOrStandalone — e.g. Series / Standalone")
    print("       LGBTQIA_Characters — e.g. Yes / No")
    print("       started_at         — fill in any missing start dates")
    print()
    print(f"  2. Open {AUTHORS_XLSX} (OneDrive) and add rows for each unique author:")
    print("       name, gender, ethnicity, DeadorAlive, Nationality, LGBTQI_Authors")
    print("       (Tip: copy from the existing Combined_Authors.xlsx if it has your data)")
    print()
    print("  3. Run:  python analysis.py")


if __name__ == "__main__":
    main()
