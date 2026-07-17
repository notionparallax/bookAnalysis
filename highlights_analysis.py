"""
highlights_analysis.py  —  analysis of Kindle highlights/notes ("grass.json")

grass.json is part of the full Goodreads data export (Settings > Account >
Data > Export, unzipped into OneDrive). It holds every Kindle highlight
("citation") synced to your Goodreads profile: the highlighted text, any
note you attached, how far through the book it falls (0-100%), and which
book it's from.

Note: each citation's created_date is a bulk-sync timestamp (every highlight
in a book shares one identical value), not the moment you actually made the
highlight — so it's not usable for a timeline. Everything here is instead
built from per-book / per-highlight structure: counts, position in the book,
length, and notes.

Configure the settings below, then run:  python highlights_analysis.py

Inputs:
  <GOODREADS_EXPORT_DIR>\\grass\\grass.json   — Kindle highlights export
  books_annotated.csv                        — for rating / genre / author join

Outputs:
  out/<READER_NAME>_highlights_*.png
"""

import json
import os
import re
from collections import Counter

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import MaxNLocator

RNG = np.random.default_rng(42)

# ── Config ────────────────────────────────────────────────────────────────────
READER_NAME = "Ben"
GOODREADS_EXPORT_DIR = r"C:\Users\bdoherty\OneDrive - BVN\Goodreads"
BOOKS_FILE = "books_annotated.csv"
OUTPUT_DIR = "out"

SINGLE_COLOR = "steelblue"
os.makedirs(OUTPUT_DIR, exist_ok=True)
plt.rcParams.update(
    {
        "figure.figsize": (9, 5),
        "axes.spines.top": False,
        "axes.spines.right": False,
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.labelsize": 10,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 9,
    }
)


def save(name: str):
    base = f"{OUTPUT_DIR}/{READER_NAME}_highlights_{name}"
    plt.savefig(base, bbox_inches="tight")
    plt.close()
    print(f"  saved highlights_{name}")


def normalise(title: str) -> str:
    """Lowercase, collapse whitespace, normalise apostrophes -- for title matching."""
    s = str(title).lower().strip()
    s = s.replace("’", "'").replace("‘", "'")
    s = re.sub(r"\s+", " ", s)
    return s


# ── Load citations ────────────────────────────────────────────────────────────
print("Loading Kindle highlights from grass.json …")
grass_path = os.path.join(GOODREADS_EXPORT_DIR, "grass", "grass.json")
with open(grass_path, encoding="utf-8") as f:
    grass_data = json.load(f)
citations = next(b["citations"] for b in grass_data if "citations" in b)

cit = pd.DataFrame(citations)
cit["has_note"] = ~cit["note_text"].isin([None, "", "(not provided)"])
cit["word_count"] = cit["highlight_text"].fillna("").str.split().str.len()
cit["display_location"] = pd.to_numeric(cit["display_location"], errors="coerce")
cit["title_key"] = cit["book_title"].apply(normalise)

n_books = cit["book_title"].nunique()
print(f"  {len(cit)} highlights across {n_books} books")
print(f"  {cit['has_note'].sum()} have a personal note attached")

# ── Join against books_annotated.csv for rating / genre / author ────────────
books = pd.read_csv(BOOKS_FILE, dtype=str, keep_default_na=False)
books["title_key"] = books["title"].apply(normalise)
books["rating"] = pd.to_numeric(books["rating"], errors="coerce")
joined = cit.merge(books, on="title_key", how="left", suffixes=("", "_book"))
matched = joined["title_book"].notna().sum() if "title_book" in joined.columns else joined["title"].notna().sum()
print(f"  {matched} of {len(cit)} highlights matched to a book_annotated.csv row")

# ── Most-highlighted books ────────────────────────────────────────────────────
top_books = cit["book_title"].value_counts().head(20).sort_values()
fig, ax = plt.subplots(figsize=(9, 7))
ax.hlines(top_books.index, 0, top_books.values, color="lightgray", linewidth=1.5)
ax.scatter(top_books.values, top_books.index, s=50, color=SINGLE_COLOR, zorder=3)
ax.set_title("Most-highlighted books (top 20)")
ax.set_xlabel("Number of highlights")
plt.tight_layout()
save("topBooks")

# ── Do highlights cluster positionally? (observed vs. random-scatter null) ──
# For each book with >=5 highlights, compare the real gaps between consecutive
# highlights (sorted by position) to gaps you'd see if the same number of
# highlights were scattered uniformly at random through the book.
books_multi = {
    title: sorted(locs)
    for title, locs in cit.dropna(subset=["display_location"])
    .groupby("book_title")["display_location"]
    .apply(list)
    .items()
    if len(locs) >= 5
}

observed_gaps = [
    locs[i] - locs[i - 1] for locs in books_multi.values() for i in range(1, len(locs))
]
sim_gaps = []
for _ in range(300):
    for locs in books_multi.values():
        rand_locs = np.sort(RNG.integers(0, 101, size=len(locs)))
        sim_gaps.extend(np.diff(rand_locs).tolist())

obs_mean = float(np.mean(observed_gaps))
sim_mean = float(np.mean(sim_gaps))
print(f"\n  clustering check: observed avg gap between highlights = {obs_mean:.2f}%")
print(f"                     random-scatter avg gap             = {sim_mean:.2f}%")
print(
    f"                     -> highlights land {(1 - obs_mean / sim_mean) * 100:.0f}% "
    "closer together than random chance would predict"
)

fig, ax = plt.subplots()
bins = np.arange(0, 41, 2)
ax.hist(
    np.clip(sim_gaps, 0, 40), bins=bins, density=True, histtype="step",
    color="darkgray", linewidth=1.5,
)
ax.hist(
    np.clip(observed_gaps, 0, 40), bins=bins, density=True, histtype="step",
    color=SINGLE_COLOR, linewidth=2,
)
ax.grid(False)
ax.set_title("Do highlights cluster? Gap to the next highlight")
ax.set_xlabel("Gap to next highlight in the book (% through, capped at 40)")
ax.set_ylabel("Density")
ax.text(9, 0.16, "observed", color=SINGLE_COLOR, fontsize=9, fontweight="bold")
ax.text(15, 0.075, "random scatter", color="darkgray", fontsize=9, fontweight="bold")
ax.text(
    0.4, 0.55,
    f"highlights land {(1 - obs_mean / sim_mean) * 100:.0f}% closer together\nthan random chance would predict",
    transform=ax.transAxes, fontsize=8.5, color="dimgray",
)
save("clustering")

# ── Individual shape of the most-highlighted books ───────────────────────────
# The aggregate "where do you highlight" histogram is a sum across books --
# this shows each top book's own shape, since they needn't (and don't) match.
top_titles = cit["book_title"].value_counts().head(9).index
fig, axes = plt.subplots(3, 3, figsize=(11, 7.5), sharex=True, sharey=False)
for ax, title in zip(axes.flat, top_titles):
    locs = books_multi.get(title, cit.loc[cit["book_title"] == title, "display_location"].dropna().tolist())
    ax.hist(locs, bins=np.arange(0, 101, 10), color=SINGLE_COLOR)
    ax.grid(False)
    ax.set_title(title[:35] + ("…" if len(title) > 35 else ""), fontsize=8, pad=3)
    ax.set_xticks([0, 50, 100])
    ax.yaxis.set_major_locator(MaxNLocator(nbins=3, integer=True))
    ax.tick_params(labelsize=7)
    ax.label_outer()
for ax in axes.flat[len(top_titles):]:
    ax.set_visible(False)
plt.suptitle("Where each of your top 9 most-highlighted books gets highlighted", fontsize=10)
plt.tight_layout()
save("topBooksLocationGrid")

# ── Where in the book do you highlight? (aggregate across all books) ────────
fig, ax = plt.subplots()
cit["display_location"].dropna().hist(bins=20, ax=ax, color=SINGLE_COLOR)
ax.grid(False)
ax.set_title("Where in a book do you highlight? (all books combined)")
ax.set_xlabel("Position in book (% through)")
ax.set_ylabel("Number of highlights")
save("locationDist")

# ── Highlight length ──────────────────────────────────────────────────────────
fig, ax = plt.subplots()
cit.loc[cit["word_count"] <= cit["word_count"].quantile(0.99), "word_count"].hist(
    bins=40, ax=ax, color=SINGLE_COLOR
)
ax.grid(False)
median_len = cit["word_count"].median()
ax.axvline(median_len, color="red", linestyle="--", lw=1.5, label=f"Median: {int(median_len)} words")
ax.set_title("Highlight length")
ax.set_xlabel("Words per highlight")
ax.set_ylabel("Number of highlights")
ax.legend()
save("length")

# ── Highlights vs your rating & fiction/non-fiction (small multiples) ───────
# Same measure (avg. highlights per book) sliced two ways; shown side by side
# on a shared y-axis, as vertical lollipops, so the two are directly comparable.
panels = []
if "rating" in joined.columns:
    per_book = joined.dropna(subset=["rating"]).groupby("title_key").agg(
        n_highlights=("highlight_text", "count"), rating=("rating", "first")
    )
    per_book = per_book[per_book["rating"] > 0]
    if not per_book.empty:
        avg_by_rating = per_book.groupby("rating")["n_highlights"].mean()
        labels = [f"{r:g}★" for r in avg_by_rating.index]
        panels.append(("By your rating", labels, avg_by_rating.values))

if "ficOrNonFic" in joined.columns:
    fnf = joined[joined["ficOrNonFic"].notna() & (joined["ficOrNonFic"] != "")]
    if not fnf.empty:
        per_book_fnf = fnf.groupby("title_key").agg(
            n_highlights=("highlight_text", "count"), ficOrNonFic=("ficOrNonFic", "first")
        )
        avg_fnf = per_book_fnf.groupby("ficOrNonFic")["n_highlights"].mean().sort_values()
        panels.append(("Fiction vs non-fiction", list(avg_fnf.index), avg_fnf.values))

if panels:
    fig, axes = plt.subplots(1, len(panels), figsize=(3.2 * len(panels) + 1, 4.5), sharey=True)
    axes = np.atleast_1d(axes)
    for ax, (title, labels, values) in zip(axes, panels):
        ax.vlines(labels, 0, values, color="lightgray", linewidth=1.5)
        ax.scatter(labels, values, s=70, color=SINGLE_COLOR, zorder=3)
        ax.set_title(title, fontsize=10)
        ax.grid(False)
    axes[0].set_ylabel("Avg. highlights per book")
    plt.suptitle("Average highlights per book, by rating and genre", fontsize=11)
    plt.tight_layout()
    save("avgHighlights")

# ── Top authors by total highlight count ──────────────────────────────────────
if "author_1_name" in joined.columns:
    by_author = (
        joined[joined["author_1_name"].notna() & (joined["author_1_name"] != "")]
        .groupby("author_1_name")
        .size()
        .sort_values()
        .tail(15)
    )
    if not by_author.empty:
        fig, ax = plt.subplots(figsize=(9, 6))
        ax.hlines(by_author.index, 0, by_author.values, color="lightgray", linewidth=1.5)
        ax.scatter(by_author.values, by_author.index, s=50, color=SINGLE_COLOR, zorder=3)
        ax.set_title("Most-highlighted authors (top 15)")
        ax.set_xlabel("Number of highlights")
        plt.tight_layout()
        save("topAuthors")

print(f"\nAll highlight charts written to '{OUTPUT_DIR}/'")
