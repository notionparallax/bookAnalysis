"""
analysis.py  —  reading analysis and chart generation

Configure the settings below, then run:  python analysis.py

Inputs (produced by ingest.py + manual editing):
  books_annotated.xlsx   — book data with manual annotations
  authors.xlsx           — author demographic data

Outputs:
  out/<READER_NAME>_*.png and .pdf
"""

import datetime
import math
import os

import matplotlib.pyplot as plt
import pandas as pd

# ── Config ────────────────────────────────────────────────────────────────────
READER_NAME = "Ben"
ONEDRIVE_DIR = r"C:\Users\bdoherty\OneDrive - BVN\book_analysis"
BOOKS_FILE = "books_annotated.csv"              # system output CSV, lives in repo
AUTHORS_FILE = rf"{ONEDRIVE_DIR}\authors.xlsx"  # manually edited xlsx, lives in OneDrive
OUTPUT_DIR = "out"

# Earliest date for the full-history waterfall chart
HISTORY_START = datetime.date(2014, 1, 1)

# ── Setup ─────────────────────────────────────────────────────────────────────
SINGLE_COLOR = "steelblue"
os.makedirs(OUTPUT_DIR, exist_ok=True)
plt.rcParams.update({
    "figure.figsize":    (9, 5),
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "font.size":         10,
    "axes.titlesize":    11,
    "axes.labelsize":    10,
    "xtick.labelsize":   9,
    "ytick.labelsize":   9,
    "legend.fontsize":   9,
})


def save(name: str):
    """Save current figure as PNG, then close it."""
    base = f"{OUTPUT_DIR}/{READER_NAME}_{name}"
    plt.savefig(base, bbox_inches="tight")
    plt.close()
    print(f"  saved {name}")


def has_data(series: pd.Series) -> bool:
    """True if the series has at least one non-null, non-blank value."""
    return series.notna().any() and series.astype(str).str.strip().ne("").any()


# ── Chart helpers ─────────────────────────────────────────────────────────────
MONTH_ABBR = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
              7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}


def short_year_index(obj):
    """Reformat a Year-indexed DataFrame/Series: 2014 → '14."""
    out = obj.copy()
    out.index = [f"'{str(int(y))[-2:]}" for y in out.index]
    return out


import re as _re

PUBLISHER_GROUPS = [
    (r"Puffin|Cornerstone",                     "Penguin"),
    (r"Penguin",                                 "Penguin"),
    (r"\bAce\b",                                "Penguin"),
    (r"Tordotcom|Tor\s+Fantasy|Tor\s+UK|\bTor\b", "Tor"),
    (r"HarperCollins|HarperVoyager|HarperPerennial|Harpertorch"
     r"|Harper Perennial|Harper & Row|Fourth Estate", "HarperCollins"),
    (r"\bOrbit\b",                               "Orbit"),
    (r"Hachette|Hodder|Virago|Little,? Brown",   "Hachette"),
    (r"Random House|Crown\b|\bBantam\b|Ballantine"
     r"|Del Rey|\bVintage\b|\bKnopf\b|Anchor Books|Doubleday|\bSpectra\b", "Random House"),
    (r"Scribner|Simon & Schuster|Avid Reader",   "Simon & Schuster"),
    (r"Pan Macmillan|Picador|\bMacmillan\b",     "Pan Macmillan"),
    (r"MIT Press|Mit Pr",                        "MIT Press"),
    (r"Oxford University|OUP Oxford",            "Oxford University Press"),
    (r"Routledge|Taylor & Francis",              "Routledge"),
    (r"Wiley",                                   "Wiley"),
    (r"Taschen|TASCHEN",                         "Taschen"),
    (r"Birkhäuser",                              "Birkhäuser"),
    (r"Faber",                                   "Faber & Faber"),
    (r"Bloomsbury",                              "Bloomsbury"),
    (r"Gateway|Gollancz|\bOrion\b",              "Orion"),
    (r"Angry Robot",                             "Angry Robot"),
    (r"\bTitan\b",                              "Titan"),
    (r"Head of Zeus",                            "Head of Zeus"),
    (r"A Book Apart",                            "A Book Apart"),
    (r"Stripe Press",                            "Stripe Press"),
    (r"Strelka Press",                           "Strelka Press"),
    (r"BOOM",                                    "BOOM! Studios"),
]


def normalise_publisher(name) -> str:
    if pd.isna(name) or not str(name).strip():
        return str(name)
    n = str(name).strip()
    for pattern, canonical in PUBLISHER_GROUPS:
        if _re.search(pattern, n, _re.IGNORECASE):
            return canonical
    return n


FORMAT_GROUPS = [
    (r"Kindle|ebook|Digital|e-book",  "Ebook"),
    (r"Mass Market|Paperback",         "Paperback"),
    (r"Hardcover|Hardback",            "Hardcover"),
    (r"Audio|Audible",                 "Audiobook"),
    (r"Board book",                    "Board book"),
]


def normalise_format(name) -> str:
    if pd.isna(name) or not str(name).strip():
        return "Unknown"
    n = str(name).strip()
    for pattern, canonical in FORMAT_GROUPS:
        if _re.search(pattern, n, _re.IGNORECASE):
            return canonical
    return n


def small_multiples_annual(pivot_df, title, filename, extra_panels=None):
    """
    Small multiple line charts from a Year x Category pivot DataFrame.
    extra_panels: list of (pd.Series, str, str) -- (data, panel_title, color).
                  These panels have their own y-scale (0-1) and a tinted background.
    """
    extras = extra_panels or []
    cats = sorted(str(c) for c in pivot_df.columns)
    n = len(cats) + len(extras)
    ncols = min(4, n)
    nrows = -(-n // ncols)
    fig, axes = plt.subplots(nrows, ncols,
                             figsize=(3.2 * ncols, 2.8 * nrows),
                             sharex=True,
                             squeeze=False)
    axes_flat = axes.flatten()
    main_ymax = (pivot_df.values.max() * 1.15) or 1
    for i, cat in enumerate(cats):
        ax = axes_flat[i]
        series = pivot_df[cat]
        ax.plot(series.index, series.values, "o-", lw=1.5, ms=4, color=SINGLE_COLOR)
        ax.fill_between(series.index, series.values, alpha=0.1, color=SINGLE_COLOR)
        ax.set_title(str(cat).replace("\n", " / "), fontsize=8, pad=3)
        ax.set_ylim(0, main_ymax)
        step = max(1, len(series) // 4)
        ticks = series.index[::step]
        ax.set_xticks(ticks)
        ax.set_xticklabels([f"'{str(int(y))[-2:]}" for y in ticks], fontsize=7)
        ax.tick_params(axis="y", labelsize=7)
    for j, (series, ptitle, color) in enumerate(extras):
        ax = axes_flat[len(cats) + j]
        ax.plot(series.index, series.values, "o-", lw=1.5, ms=4, color=color)
        ax.fill_between(series.index, series.values, alpha=0.12, color=color)
        ax.set_title(ptitle, fontsize=8, pad=3)
        ax.set_ylim(0, 1.05)
        step = max(1, len(series) // 4)
        ticks = series.index[::step]
        ax.set_xticks(ticks)
        ax.set_xticklabels([f"'{str(int(y))[-2:]}" for y in ticks], fontsize=7)
        ax.tick_params(axis="y", labelsize=7)
        ax.set_facecolor("#f7f7f7")
    for k in range(n, len(axes_flat)):
        axes_flat[k].set_visible(False)
    plt.suptitle(title, fontsize=10)
    plt.tight_layout()
    save(filename)


def _row_entropy(row):
    """Normalized Shannon entropy for one row of category counts (0=all one group, 1=equal)."""
    total = row.sum()
    if total == 0:
        return 0
    p = row[row > 0] / total
    h = -sum(pi * math.log2(pi) for pi in p)
    k = int((row > 0).sum())
    return h / math.log2(k) if k > 1 else 0


# ── Load books ────────────────────────────────────────────────────────────────
print(f"Loading books from '{BOOKS_FILE}' …")
tb = pd.read_csv(BOOKS_FILE)
# Normalise author name whitespace so the merge with authors.xlsx is reliable
tb["author_1_name"] = tb["author_1_name"].astype(str).str.strip().str.replace(r"\s+", " ", regex=True)
for col in ("started_at", "read_at", "date_added"):
    if col in tb.columns:
        tb[col] = pd.to_datetime(tb[col], errors="coerce")

# Fill missing started_at: assume 2 weeks before finish
missing_start = tb["started_at"].isna() & tb["read_at"].notna()
tb.loc[missing_start, "started_at"] = tb.loc[missing_start, "read_at"] - pd.Timedelta(weeks=2)
print(f"  {missing_start.sum()} missing started_at filled as read_at - 14 days")

tb.sort_values(by="read_at", ascending=False, na_position="last", inplace=True)
tb.reset_index(drop=True, inplace=True)
print(f"  {len(tb)} books loaded")

# Re-reads (read_count > 1)
if "read_count" in tb.columns:
    rereads = tb[tb["read_count"].notna() & (tb["read_count"] > 1)][
        ["title", "author_1_name", "read_count"]
    ].sort_values("read_count", ascending=False)
    if not rereads.empty:
        print("\nBooks read more than once:")
        for _, r in rereads.iterrows():
            print(f"  {r['title']} ({r['author_1_name']}) x{int(r['read_count'])}")
    else:
        print("  No re-reads found.")

# ── Dated view (books with a known finish date) ───────────────────────────────
dated = tb.dropna(subset=["read_at"]).copy()
dated["Year"] = dated["read_at"].dt.year
dated["Month"] = dated["read_at"].dt.month

# ── Waterfall: full reading history ───────────────────────────────────────────
has_duration = tb.dropna(subset=["started_at", "read_at"]).copy()
if has_duration.empty:
    print("  No started_at + read_at pairs found yet — waterfall chart skipped.")
    print("  Fill in 'started_at' in books_annotated.xlsx and re-run.")
else:
    fig, ax = plt.subplots(figsize=(9, 10))
    hist_start = pd.Timestamp(HISTORY_START)
    for idx, row in has_duration.iterrows():
        start = max(row.started_at, hist_start)
        ax.plot(
            [start, row.read_at],
            [idx, idx],
            "-",
            lw=2.5,
        )
        ax.text(
            start,
            idx,
            str(row.title),
            fontsize=1.5,
            verticalalignment="center",
        )
    fig.autofmt_xdate()
    ax.set_xlim([HISTORY_START, datetime.date.today()])
    ax.spines["left"].set_visible(False)
    plt.tick_params(axis="y", which="both", left=False, right=False, labelleft=False)
    plt.title(f"Books and Duration — {HISTORY_START.year}–present")
    save("bookWaterfall_allTime")
    plt.savefig(f"{OUTPUT_DIR}/{READER_NAME}_bookWaterfall_allTime.pdf", bbox_inches="tight")

# ── Reading cadence ───────────────────────────────────────────────────────────
month_data = dated["Month"].value_counts().sort_index()
month_data.index = [MONTH_ABBR.get(m, m) for m in month_data.index]
month_data.plot(kind="bar", rot=0, color=SINGLE_COLOR)
plt.title("Books Finished Each Month")
plt.ylabel("Count of books")
save("booksPerMonth")

year_counts = dated["Year"].value_counts().sort_index()
fig, ax = plt.subplots()
ax.plot(year_counts.index, year_counts.values, "o-", lw=2, color=SINGLE_COLOR)
ax.set_xticks(year_counts.index[::2])
ax.set_xticklabels([f"'{str(int(y))[-2:]}" for y in year_counts.index[::2]])
plt.title("Books Finished Each Year")
plt.ylabel("Count of books")
save("booksPerYear")

# ── Publication year ──────────────────────────────────────────────────────────
if has_data(tb["publication_year"]):
    print(
        f"Median publication year: {int(tb.publication_year.median())},  "
        f"mean: {int(tb.publication_year.mean())}"
    )
    fig, ax = plt.subplots()
    tb.publication_year.hist(bins=50, ax=ax, color=SINGLE_COLOR)
    ax.grid(False)
    ax.set_title("Publication year of books read")
    ax.set_ylabel("Count of books")
    ax.set_xlabel("Year published")

    # Inset in the empty ancient-years space: shows 1900+ in detail
    ax_ins = ax.inset_axes([-500, 50, 2000, 300], transform=ax.transData)
    tb.publication_year[tb.publication_year >= 1900].hist(bins=40, ax=ax_ins, color=SINGLE_COLOR, alpha=0.8)
    ax_ins.grid(False)
    ax_ins.set_title("Since 1900", fontsize=8, pad=3)
    ax_ins.tick_params(labelsize=7)
    ax_ins.set_facecolor("#f5f5f5")

    save("publicationYearHist")

    # Publication lag: how old were books when read?
    lag_df = tb.dropna(subset=["publication_year", "read_at"]).copy()
    lag_df["lag"] = lag_df["read_at"].dt.year - lag_df["publication_year"]
    lag = lag_df.loc[lag_df["lag"].between(0, 500), "lag"]
    if not lag.empty:
        fig, ax = plt.subplots()
        lag.hist(bins=30, ax=ax, color=SINGLE_COLOR, alpha=0.8)
        ax.grid(False)
        ax.axvline(lag.median(), color="red", linestyle="--", lw=1.5,
                   label=f"Median: {int(lag.median())} yrs")
        ax.set_title("How old were books when you read them?")
        ax.set_xlabel("Years since publication")
        ax.set_ylabel("Count of books")
        ax.legend()

        # Inset: detail of the 0–100 year range
        ax_ins = ax.inset_axes([0.45, 0.35, 0.52, 0.58])
        lag[lag <= 100].hist(bins=25, ax=ax_ins, color=SINGLE_COLOR, alpha=0.8)
        ax_ins.grid(False)
        ax_ins.set_title("First 100 years", fontsize=8, pad=3)
        ax_ins.set_xlabel("Years since publication", fontsize=7)
        ax_ins.tick_params(labelsize=7)
        ax_ins.set_facecolor("#f5f5f5")

        save("publicationLag")

        med_lag = lag_df.loc[lag_df["lag"].between(0, 500)].groupby(
            lag_df["read_at"].dt.year)["lag"].median()
        fig, ax = plt.subplots()
        ax.plot(med_lag.index, med_lag.values, "o-", color=SINGLE_COLOR, lw=2)
        ax.set_title("Median publication age of books read per year")
        ax.set_xlabel("Year")
        ax.set_ylabel("Median years since publication")
        save("publicationLagTrend")
if has_data(tb["num_pages"]):
    print(
        f"Median pages: {int(tb.num_pages.median())},  "
        f"mean: {int(tb.num_pages.mean())}"
    )
    fig, ax = plt.subplots()
    tb.num_pages.hist(bins=45, ax=ax, color=SINGLE_COLOR)
    ax.grid(False)
    plt.title("Page count of books read")
    plt.ylabel("Count of books")
    plt.xlabel("Number of pages")
    save("numPages")

# ── Format ────────────────────────────────────────────────────────────────────
if has_data(tb["format"]):
    tb.format.value_counts().plot(kind="bar", rot=20, color=SINGLE_COLOR)
    plt.title("Books read by format")
    plt.ylabel("Count of books")
    plt.xlabel("Format")
    save("format")

    # Format mix by year (%)
    fmt_dated = dated.dropna(subset=["format"]).copy()
    fmt_dated["format_norm"] = fmt_dated["format"].apply(normalise_format)
    pivot_fmt = fmt_dated.groupby(["Year", "format_norm"]).size().unstack(fill_value=0)
    pct_fmt = pivot_fmt.div(pivot_fmt.sum(axis=1), axis=0) * 100
    short_year_index(pct_fmt).plot(kind="bar", stacked=True, rot=0)
    plt.title("Format mix by year (%)")
    plt.ylabel("% of books read")
    plt.legend(title="Format", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    save("formatOverTime")

# ── Publisher ─────────────────────────────────────────────────────────────────
if has_data(tb["publisher"]):
    tb["publisher"].apply(normalise_publisher).value_counts().head(20).plot.barh(color=SINGLE_COLOR)
    plt.title("Top publishers (20)")
    plt.xlabel("Count of books")
    save("publisher")

# ── Rating ────────────────────────────────────────────────────────────────────
if has_data(tb["rating"]):
    tb.rating.value_counts().sort_index().plot(kind="bar", rot=0, color=SINGLE_COLOR)
    plt.title("My ratings")
    plt.ylabel("Count of books")
    plt.xlabel("Rating (1–5)")
    save("rating")

    # Average rating by year (line chart)
    rated_dated = dated[(dated["rating"].notna()) & (dated["rating"] > 0)].copy()
    if not rated_dated.empty:
        avg_rating = rated_dated.groupby("Year")["rating"].mean()
        fig, ax = plt.subplots()
        ax.plot(avg_rating.index, avg_rating.values, "o-", lw=2, color="steelblue")
        ax.set_ylim(1, 5.5)
        ax.set_xlabel("Year")
        ax.set_ylabel("Average rating")
        ax.set_title("Average rating by year")
        ax.grid(True, alpha=0.3)
        save("ratingByYear")

# ── Prolific authors ─────────────────────────────────────────────────────────────
author_counts = tb["author_1_name"].value_counts()
prolific = author_counts[author_counts > 1].sort_values()
if not prolific.empty:
    fig, ax = plt.subplots(figsize=(9, max(2, len(prolific) * 0.18)))
    ax.hlines(prolific.index, 0, prolific.values, color="lightgray", linewidth=1.5)
    ax.scatter(prolific.values, prolific.index, s=50, color=SINGLE_COLOR, zorder=3)
    plt.title("Authors read more than once")
    plt.xlabel("Books read")
    plt.tight_layout()
    save("prolificAuthors")
if "ficOrNonFic" in tb.columns and has_data(tb["ficOrNonFic"]):
    tb.ficOrNonFic.value_counts().plot(kind="bar", rot=20, color=SINGLE_COLOR)
    plt.title("Fiction vs Non-Fiction")
    plt.ylabel("Count of books")
    save("ficNonfic")

if "SeriesOrStandalone" in tb.columns and has_data(tb["SeriesOrStandalone"]):
    tb.SeriesOrStandalone.value_counts().plot(kind="bar", rot=20, color=SINGLE_COLOR)
    plt.title("Series vs Stand-Alone")
    plt.ylabel("Count of books")
    save("seriesStandalone")

if "LGBTQIA_Characters" in tb.columns and has_data(tb["LGBTQIA_Characters"]):
    tb.LGBTQIA_Characters.value_counts().plot(kind="bar", rot=20, color=SINGLE_COLOR)
    plt.title("LGBTQIA Characters in Books")
    plt.ylabel("Count of books")
    save("lgbtqiaCharacters")

# ── Author diversity analysis ─────────────────────────────────────────────────
if not os.path.exists(AUTHORS_FILE):
    print(f"\nNo authors file found at '{AUTHORS_FILE}' — diversity analysis skipped.")
    print("Create authors.xlsx with columns: name, gender, ethnicity, DeadorAlive, Nationality, LGBTQI_Authors")
else:
    print(f"\nLoading authors from '{AUTHORS_FILE}' …")
    authors_df = pd.read_excel(AUTHORS_FILE)
    print(f"  {len(authors_df)} unique authors loaded")

    # Derived compound columns (newline separator for readable chart labels)
    authors_df["compound_diversity"] = (
        authors_df["ethnicity"].astype(str) + "\n" + authors_df["gender"].astype(str)
    )
    authors_df["compound_sexuality"] = (
        authors_df["gender"].astype(str) + "\n" + authors_df["LGBTQI_Authors"].astype(str)
    )
    authors_df["compound_genderalive"] = (
        authors_df["gender"].astype(str) + "\n" + authors_df["DeadorAlive"].astype(str)
    )

    # Unique-author charts
    authors_df.gender.value_counts().plot(kind="bar", rot=0, color=SINGLE_COLOR)
    plt.title("Gender of unique first authors")
    plt.ylabel("Count of authors")
    save("uniqueAuthors_gender")

    authors_df.ethnicity.value_counts().plot(kind="bar", rot=0, color=SINGLE_COLOR)
    plt.title("Ethnicity of unique first authors")
    plt.ylabel("Count of authors")
    save("uniqueAuthors_ethnicity")

    authors_df.DeadorAlive.value_counts().plot(kind="bar", rot=0, color=SINGLE_COLOR)
    plt.title("Authors: dead or alive")
    plt.ylabel("Count of authors")
    save("uniqueAuthors_lifeStatus")

    authors_df.Nationality.value_counts().head(30).plot.barh()
    plt.title("Nationality of unique first authors (top 30)")
    plt.xlabel("Count of authors")
    save("uniqueAuthors_nationality")

    authors_df.LGBTQI_Authors.value_counts().plot(kind="bar", rot=0, color=SINGLE_COLOR)
    plt.title("Sexuality of unique first authors")
    plt.ylabel("Count of authors")
    save("uniqueAuthors_sexuality")

    authors_df.compound_diversity.value_counts().plot(kind="bar", figsize=(12, 6), rot=0, color=SINGLE_COLOR)
    plt.title("Compound diversity of unique first authors")
    plt.ylabel("Count of authors")
    plt.tight_layout()
    save("uniqueAuthors_compoundDiversity")

    authors_df.compound_sexuality.value_counts().plot(kind="bar", figsize=(10, 6), rot=0, color=SINGLE_COLOR)
    plt.title("Compound sexuality of unique first authors")
    plt.ylabel("Count of authors")
    plt.tight_layout()
    save("uniqueAuthors_compoundSexuality")

    authors_df.compound_genderalive.value_counts().plot(kind="bar", figsize=(10, 6), rot=0, color=SINGLE_COLOR)
    plt.title("Compound life status + gender of unique first authors")
    plt.ylabel("Count of authors")
    plt.tight_layout()
    save("uniqueAuthors_compoundGenderAlive")

    # Join books + authors
    all_df = tb.merge(authors_df, left_on="author_1_name", right_on="name", how="inner")
    print(f"  {len(all_df)} of {len(tb)} books matched to author records")

    if all_df.empty:
        print("  No matched books — skipping per-book diversity charts.")
    else:
        all_df["reading_year"] = all_df["read_at"].dt.year

        all_df.gender.value_counts().plot(kind="bar", rot=0, color=SINGLE_COLOR)
        plt.title("Books read by gender of first author")
        plt.ylabel("Count of books")
        save("booksRead_gender")

        all_df.ethnicity.value_counts().plot(kind="bar", rot=0, color=SINGLE_COLOR)
        plt.title("Books read by ethnicity of first author")
        plt.ylabel("Count of books")
        save("booksRead_ethnicity")

        # ── Breakdown small multiples (lollipop grid) ──────────────────────────
        panels = []
        for col, label in [("ficOrNonFic", "Fiction /\nNon-Fiction"),
                           ("SeriesOrStandalone", "Series /\nStandalone"),
                           ("LGBTQIA_Characters", "LGBTQIA\nChars")]:
            if col in tb.columns and has_data(tb[col]):
                panels.append((tb[col].value_counts(), label))
        panels.append((all_df["gender"].value_counts(), "Author\nGender"))
        panels.append((all_df["ethnicity"].value_counts(), "Author\nEthnicity"))
        if panels:
            fig, axes = plt.subplots(1, len(panels), figsize=(2.5 * len(panels), 2))
            if len(panels) == 1:
                axes = [axes]
            for ax, (data, ptitle) in zip(axes, panels):
                ax.hlines(data.index, 0, data.values, color="lightgray", linewidth=1.5)
                ax.scatter(data.values, data.index, s=60, color=SINGLE_COLOR, zorder=3)
                ax.set_title(ptitle, fontsize=9)
                ax.tick_params(labelsize=8)
            plt.suptitle("Reading breakdown", fontsize=10)
            plt.tight_layout()
            save("breakdownSM")

        # ── Diversity bubble: gender × ethnicity ─────────────────────────────────
        counts_2d = all_df.groupby(["ethnicity", "gender"]).size().reset_index(name="n")
        if not counts_2d.empty:
            genders = sorted(counts_2d["gender"].unique())
            ethnicities = sorted(counts_2d["ethnicity"].unique())
            fig, ax = plt.subplots(figsize=(max(5, len(ethnicities) * 1.2), max(3, len(genders) * 0.9)))
            for _, row in counts_2d.iterrows():
                xi = ethnicities.index(row["ethnicity"])
                yi = genders.index(row["gender"])
                ax.scatter(xi, yi, s=row["n"] * 20, color=SINGLE_COLOR, alpha=0.7, zorder=3)
                ax.text(xi, yi, str(row["n"]), ha="center", va="center",
                        fontsize=8, color="white", fontweight="bold", zorder=4)
            ax.set_xticks(range(len(ethnicities)))
            ax.set_xticklabels(ethnicities)
            ax.set_yticks(range(len(genders)))
            ax.set_yticklabels(genders)
            ax.set_title("Books read: author gender × ethnicity")
            ax.grid(True, alpha=0.15, zorder=0)
            ax.set_axisbelow(True)
            plt.tight_layout()
            save("diversityBubble")

        # Rating by author demographic
        rated_all = all_df[(all_df["rating"].notna()) & (all_df["rating"] > 0)].copy()
        if not rated_all.empty:
            fig, axes = plt.subplots(1, 3, figsize=(13, 5))
            for ax, col, title in zip(
                axes,
                ["gender", "ethnicity", "LGBTQI_Authors"],
                ["Gender", "Ethnicity", "Sexuality"],
            ):
                means = rated_all.groupby(col)["rating"].mean().sort_values()
                ax.hlines(means.index, 0, means.values, color="lightgray", linewidth=1.5)
                ax.scatter(means.values, means.index, s=70, color=SINGLE_COLOR, zorder=3)
                ax.set_title(f"Avg rating by {title}")
                ax.set_xlabel("Mean rating")
                ax.set_xlim(0, 5)
            plt.suptitle("Your average rating by author demographic")
            plt.tight_layout()
            save("ratingByDemographic")
        dated_authors = dated.merge(
            authors_df, left_on="author_1_name", right_on="name", how="inner"
        )
        if not dated_authors.empty:
            short_year_index(dated_authors.groupby(["Year", "compound_diversity"]).size().unstack(fill_value=0)).plot(
                kind="bar", stacked=True, rot=0
            )
            plt.title("Author diversity by year")
            plt.ylabel("Count of books")
            save("annualDiversity")

            short_year_index(dated_authors.groupby(["Year", "compound_genderalive"]).size().unstack(fill_value=0)).plot(
                kind="bar", stacked=True, rot=0
            )
            plt.title("Gender and life status by year")
            plt.ylabel("Count of books")
            save("annualGenderAlive")

            if "ficOrNonFic" in dated_authors.columns and has_data(dated_authors["ficOrNonFic"]):
                short_year_index(dated_authors.groupby(["Year", "ficOrNonFic"]).size().unstack(fill_value=0)).plot(
                    kind="bar", stacked=True, rot=0
                )
                plt.title("Fiction vs non-fiction by year")
                plt.ylabel("Count of books")
                save("annualFicNonfic")

            # Small multiples versions of the annual stacked charts
            div_pivot = dated_authors.groupby(["Year", "compound_diversity"]).size().unstack(fill_value=0)
            entropy_series = div_pivot.apply(_row_entropy, axis=1)
            small_multiples_annual(
                div_pivot,
                "Author diversity by year", "annualDiversity_sm",
                extra_panels=[(entropy_series, "Diversity\nindex (0–1)", "coral")],
            )
            small_multiples_annual(
                dated_authors.groupby(["Year", "compound_genderalive"]).size().unstack(fill_value=0),
                "Gender and life status by year", "annualGenderAlive_sm"
            )
            if "ficOrNonFic" in dated_authors.columns and has_data(dated_authors["ficOrNonFic"]):
                small_multiples_annual(
                    dated_authors.groupby(["Year", "ficOrNonFic"]).size().unstack(fill_value=0),
                    "Fiction vs non-fiction by year", "annualFicNonfic_sm"
                )
            dy = dated_authors.copy()
            dy["is_female"]   = dy["gender"] == "Female"
            dy["is_nonwhite"] = dy["ethnicity"] != "White"
            dy["is_lgbtqia"]  = ~dy["LGBTQI_Authors"].isin(["Straight", "Unknown", ""])
            trend = dy.groupby("Year").agg(
                total=("title",       "count"),
                female=("is_female",   "sum"),
                nonwhite=("is_nonwhite", "sum"),
                lgbtqia=("is_lgbtqia",  "sum"),
            )
            trend["% Female"]   = trend["female"]   / trend["total"] * 100
            trend["% Non-white"] = trend["nonwhite"] / trend["total"] * 100
            trend["% LGBTQIA+"] = trend["lgbtqia"]  / trend["total"] * 100
            fig, ax = plt.subplots()
            for col, marker in zip(["% Female", "% Non-white", "% LGBTQIA+"], ["o", "s", "^"]):
                ax.plot(trend.index, trend[col], f"{marker}-", lw=2, label=col)
            ax.set_ylim(0, 100)
            ax.set_ylabel("% of books read")
            ax.set_title("Author diversity trends over time")
            ax.legend()
            ax.grid(True, alpha=0.3)
            save("diversityTrends")
        fig, ax = plt.subplots(figsize=(12, 6))
        all_df.groupby(["compound_diversity", "DeadorAlive"]).size().unstack(fill_value=0).plot(
            kind="bar", stacked=True, rot=0, ax=ax
        )
        plt.title("Compound diversity by author life status")
        plt.ylabel("Count of books")
        plt.tight_layout()
        save("compoundDiversity_lifeStatus")

        if "ficOrNonFic" in all_df.columns and has_data(all_df["ficOrNonFic"]):
            fig, ax = plt.subplots(figsize=(12, 6))
            all_df.groupby(["compound_diversity", "ficOrNonFic"]).size().unstack(fill_value=0).plot(
                kind="bar", stacked=True, rot=0, ax=ax
            )
            plt.title("Fiction/non-fiction by compound diversity")
            plt.ylabel("Count of books")
            plt.tight_layout()
            save("compoundDiversity_ficNonfic")

        # Pages by attribute
        if has_data(all_df["num_pages"]):
            s_pub = all_df.dropna(subset=["publication_year"]).groupby("publication_year")["num_pages"].sum().sort_index()
            fig, ax = plt.subplots()
            ax.bar(s_pub.index.astype(int), s_pub.values, width=0.8, color=SINGLE_COLOR)
            ax.grid(False)
            ax.set_title("Pages read by publication year")
            ax.set_ylabel("Pages read")
            ax.set_xlabel("Year published")

            # Inset: 1900+ pages, placed in the empty ancient-years zone
            ymax = s_pub.values.max()
            ax_ins2 = ax.inset_axes([-500, ymax * 0.35, 2000, ymax * 0.58], transform=ax.transData)
            s_1900 = s_pub[s_pub.index >= 1900]
            ax_ins2.bar(s_1900.index.astype(int), s_1900.values, width=0.8, color=SINGLE_COLOR, alpha=0.8)
            ax_ins2.grid(False)
            ax_ins2.set_title("Since 1900", fontsize=8, pad=3)
            ax_ins2.tick_params(labelsize=7)
            ax_ins2.set_facecolor("#f5f5f5")

            save("pages_byPublicationYear")

            s_read = all_df.groupby("reading_year")["num_pages"].sum().sort_index()
            fig, ax = plt.subplots()
            ax.plot(s_read.index.astype(int), s_read.values, "o-", lw=2, color=SINGLE_COLOR)
            ax.set_xticks(s_read.index[::2])
            ax.set_xticklabels([f"'{str(int(y))[-2:]}" for y in s_read.index[::2]])
            ax.set_title("Pages read per calendar year")
            ax.set_ylabel("Pages read")
            save("pages_byReadingYear")

            if has_data(all_df["format"]):
                fmt_pages = all_df.groupby("format")["num_pages"].sum().sort_values()
                fig, ax = plt.subplots()
                ax.hlines(fmt_pages.index, 0, fmt_pages.values, color="lightgray", linewidth=1.5)
                ax.scatter(fmt_pages.values, fmt_pages.index, s=60, color=SINGLE_COLOR, zorder=3)
                plt.title("Pages read by format")
                plt.tight_layout()
                save("pages_byFormat")

            if "ficOrNonFic" in all_df.columns and has_data(all_df["ficOrNonFic"]):
                all_df.groupby(["compound_diversity", "ficOrNonFic"])["num_pages"].sum().unstack(
                    fill_value=0
                ).plot(kind="bar", stacked=True, rot=0, figsize=(12, 6))
                plt.title("Pages read: fiction/non-fiction by compound diversity")
                plt.ylabel("Pages read")
                plt.tight_layout()
                save("pages_compoundDiversity_ficNonfic")

print(f"\nAll charts written to '{OUTPUT_DIR}/'")
