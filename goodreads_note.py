#%%
import datetime
from fractions import Fraction
import json
import math
import os

from dateutil import parser
import matplotlib.pyplot as plt
import pandas as pd
import requests
import xmltodict

# %%
tb = pd.read_excel(
    "combined_book_data.xlsx", 
    sheet_name="combined", 
    parse_dates=['started_at', 'read_at', 'date_added', 'date_updated']
    )
tb.sort_values(by="started_at", ascending=False, inplace=True)
tb.reset_index(drop=True, inplace=True)

#%%
tb.head()
#%%
tb.dtypes
#%%
tb["started_at"] = pd.to_datetime(tb["started_at"])
tb["started_at"]
#%%
tb["read_at"] = pd.to_datetime(tb["read_at"])
tb["read_at"]
#%%
tb_dates = tb.set_index('started_at')
tb_dates.head(3)
#%%
tb_dates.index
#%%
tb_dates['Year'] = tb_dates.index.year
tb_dates['Month'] = tb_dates.index.month
tb_dates.head(3)
#%%
date_start_range = tb[tb["started_at"].between('2012-01-01', '2020-12-31')]
known_start = date_start_range['started_at']
date_end_range = tb[tb["read_at"].between('2012-01-01', '2020-12-31')]
known_end = date_end_range['read_at']
# #%%
# plt.rcParams["figure.figsize"] = (8.27, 11.69)
# fig, ax = plt.subplots()
# marker = "-"
# for index, row in tb.iterrows():        
#     ax.plot_date(
#         [known_start, known_end],
#         [index, index],
#         fmt=marker,
#         tz=None,
#         xdate=True,
#         ydate=False,
#         lw=2.5,
#     )
            
#     ax.text(
#         known_start,
#         index,
#         f"{row.title}",
#         fontsize=1.5,
#         verticalalignment="center",
#     )

# fig.autofmt_xdate()
# ax.set_xlim([datetime.date(2019, 1, 1), datetime.date(2020, 8, 1)])
# plt.tick_params(axis="y", which="both", left=False, right=False, labelleft=False)
# plt.grid(True)
# plt.title("Books and Duration of 2020")
# # plt.savefig(f"out/bookWaterfall", bbox_inches="tight")
# # plt.savefig(f"out/bookWaterfall.pdf", bbox_inches="tight")
#%%
plt.rcParams["figure.figsize"] = (8.27, 11.69)
fig, ax = plt.subplots()

for index, row in tb.iterrows():
    marker = "-"
    ax.plot_date(
        [row.started_at, row.read_at],
        [index, index],
        fmt=marker,
        tz=None,
        xdate=True,
        ydate=False,
        lw=2.5,
    )
    ax.text(
        row.started_at,
        index,
        f"{row.title}",
        fontsize=1.5,
        verticalalignment="center",
    )

fig.autofmt_xdate()
ax.set_xlim([datetime.date(2012, 1, 1), datetime.date(2020, 8, 1)])
plt.tick_params(axis="y", which="both", left=False, right=False, labelleft=False)
plt.grid(True)
plt.title("Books and Duration Since 2012")
# plt.savefig(f"out/bookWaterfall", bbox_inches="tight")
# plt.savefig(f"out/bookWaterfall.pdf", bbox_inches="tight")
#%%
cols_to_drop = [
    "Unnamed: 0",
    # "started_at",
    "read_at",
    "date_added",
    "date_updated",
    "html_link",
]
for c in cols_to_drop:
    try:
        tb.drop(c, axis=1, inplace=True)
    except Exception as e:
        print(e)
try:
    tb["book"] = tb.apply(
        lambda x: eval(x.book.replace("OrderedDict", "dict")), axis=1
    )
except:
    pass
    # must have already done this step
#%%
def dataise(d):
    if type(d) is str:
        return eval(d)
    else:
        return d


tb.book = tb.book.apply(dataise)
tb.head()
#%%
plt.rcParams["figure.figsize"] = (8, 8)
# %%
print(
    f"Median year: {int(tb.publication_year.median())}, mean year: {int(tb.publication_year.mean())}"
)
#%%
tb_dates.Month.value_counts().sort_index().plot(kind="bar")
plt.title("Books Read During Each Month")
plt.ylabel("Count of books")
plt.xlabel("Month")
plt.savefig(f"out/publicationYearBar", bbox_inches="tight")
#%%
tb.publication_year.value_counts().sort_index().plot(kind="bar")
plt.title("Publication year of books read in the last 6 years")
plt.ylabel("Count of books")
plt.xlabel("Year")
plt.savefig(f"out/publicationYearBar", bbox_inches="tight")
#%%
tb.publication_year.hist(bins=50)
plt.title("Publication year of books read in the last 6 years")
plt.ylabel("Count of books")
plt.xlabel("Year")
plt.savefig(f"out/publicationYearHist", bbox_inches="tight")

# %%
print(
    f"Median pages: {int(tb.num_pages.median())}, "
    f"mean pages: {int(tb.num_pages.mean())}"
)
tb.num_pages.hist(bins=45)
plt.title("Number of pages in these books")
plt.ylabel("Count of books")
plt.xlabel("Number of pages")
plt.savefig(f"out/numPages", bbox_inches="tight")

#%%
tb.format.value_counts().plot(kind="bar", rot=20)
plt.title(
    "Number of books read, split by format,\nof books read in the last 6ish years"
)
plt.ylabel("Count of books")
plt.xlabel("Format of book")
plt.savefig(f"out/format", bbox_inches="tight")
#%%
tb.publisher.value_counts().plot.barh()
plt.title("Publisher - very unfinished")
plt.xlabel("Count of books")
plt.ylabel("Publisher of book")
plt.savefig(f"out/publisher", bbox_inches="tight")

#%%
tb.rating.hist(bins=4)
plt.title("My rating")
plt.ylabel("Count of books")
plt.xlabel("What I've rated this book")
plt.savefig(f"out/rating", bbox_inches="tight")

#%%
tb.ficOrNonFic.value_counts().plot(kind="bar", rot=20)
plt.title("Fiction vs Non-Fiction")
plt.ylabel("Count of Books")
plt.xlabel("Type of Book")
plt.savefig(f"out/ficnonfic", bbox_inches="tight")

#%%
tb.SeriesOrStandalone.value_counts().plot(kind="bar", rot=20)
plt.title("Series vs Stand-Alone")
plt.ylabel("Count of Books")
plt.xlabel("Type of Book")
plt.savefig(f"out/seriesstandalone", bbox_inches="tight")

#%%
tb.LGBTQIA_Characters.value_counts().plot(kind="bar", rot=20)
plt.title("LGBTQIA Characters in Books")
plt.ylabel("Count of Books")
plt.xlabel("Type of Book")
plt.savefig(f"out/seriesstandalone", bbox_inches="tight")

#%%
all_authors = []
for index, row in tb.iterrows():
    all_authors.append(row.book["authors"]["author"])
authors_df = pd.DataFrame(all_authors)
authors_df.drop_duplicates(subset="name", inplace=True)
authors_df.reset_index(drop=True, inplace=True)
authors_df.average_rating = authors_df.average_rating.apply(float)
cols_to_drop = ["image_url", "role", "small_image_url"]
for c in cols_to_drop:
    try:
        authors_df.drop(c, axis=1, inplace=True)
    except Exception as e:
        print(e)
authors_df.to_excel("temp_authors.xlsx")
authors_df.head()
#%%
authors_df.average_rating.hist()
plt.title("Average Rating of Books")
plt.ylabel("Amount of books")
plt.xlabel("Rating")

#%%
"""
This tries to quantify diversity, clumsily!

Ethnicities from: [Racial and Ethnic Categories and Definitions for NIH Diversity Programs and for Other Reporting Purposes](https://grants.nih.gov/grants/guide/notice-files/not-od-15-089.html)
American Indian or Alaska Native. A person having origins in any of the original peoples of North and South America (including Central America), and who maintains tribal affiliation or community attachment.
Asian. A person having origins in any of the original peoples of the Far East, Southeast Asia, or the Indian subcontinent including, for example, Cambodia, China, India, Japan, Korea, Malaysia, Pakistan, the Philippine Islands, Thailand, and Vietnam.
Black or African American. A person having origins in any of the black racial groups of Africa. Terms such as "Haitian" or "Negro" can be used in addition to "Black or African American."
Hispanic or Latino. A person of Cuban, Mexican, Puerto Rican, South or Central American, or other Spanish culture or origin, regardless of race. The term, "Spanish origin," can be used in addition to "Hispanic or Latino."
Native Hawaiian or Other Pacific Islander. A person having origins in any of the original peoples of Hawaii, Guam, Samoa, or other Pacific Islands.
White.
"""
authors_df = pd.read_excel("Combined_Authors.xlsx")
authors_df.head()
#%%
authors_df.gender.value_counts().plot(kind="bar", rot=0)
plt.title("Gender of unique first authors")
plt.ylabel("Count of authors")
plt.xlabel("The gender I've guessed")
plt.savefig(f"out/Gender_count_of_unique_first_authors", bbox_inches="tight")
#%%
authors_df.ethnicity.value_counts().plot(kind="bar", rot=0)
plt.title("Ethnicity of unique first authors")
plt.ylabel("Count of authors")
plt.xlabel("The ethnicity I've guessed")
plt.savefig(f"out/first_author_ethnicity", bbox_inches="tight")

#%%
authors_df.Nationality.value_counts()[:30].plot.barh()
plt.title("Nationality of unique first authors")
plt.ylabel("Count of authors")
plt.xlabel("The Nationality I've guessed")
plt.savefig(f"out/first_author_nationality", bbox_inches="tight")

#%%
authors_df.LGBTQI_Authors.value_counts().plot(kind="bar", rot=0)
plt.title("Sexuality of unique first authors")
plt.ylabel("Count of authors")
plt.xlabel("The Sexuality I've guessed")
plt.savefig(f"out/first_author_sexuality", bbox_inches="tight")

#%%
authors_df["compound_diversity"] = authors_df.apply(
    lambda x: f"{x.ethnicity}-{x.gender}", axis=1
)
authors_df.compound_diversity.value_counts().plot(kind="bar")
plt.title('"Compound" diversity of unique first authors')
plt.ylabel("Count of authors")
plt.xlabel("joined together")
plt.savefig(f"out/compundDiversity", bbox_inches="tight")

#%%
authors_df["compound_sexuality"] = authors_df.apply(
    lambda x: f"{x.gender}-{x.LGBTQI_Authors}", axis=1
)
authors_df.compound_sexuality.value_counts().plot(kind="bar")
plt.title('"Compound" Sexuality of unique first authors')
plt.ylabel("Count of authors")
plt.xlabel("joined together")
plt.savefig(f"out/compundSexuality", bbox_inches="tight")

#%%
all_df = tb.merge(authors_df, right_on="name", left_on="author_1_name")
all_df.sample(4)
#%%
all_df.gender.value_counts().plot(kind="bar", rot=0)
plt.title("Books read, split by Gender of unique first author")
plt.ylabel("Count of books")
plt.xlabel("Gender")
plt.savefig(f"out/gender_of_books_read", bbox_inches="tight")
#%%
all_df.ethnicity.value_counts().plot(kind="bar", rot=0)
plt.title("Ethnicity of unique first authors")
plt.ylabel("Count of books")
plt.xlabel("The ethnicity I've guessed")
plt.savefig(f"out/Ethnicity_of_books_read", bbox_inches="tight")

#%%
all_df["reading_year"] = all_df.started_at.apply(lambda x: x.year)
#%%
# from : https://stackoverflow.com/a/34919066/1835727
diversity_data = all_df.groupby(["reading_year", "compound_diversity"]).size().unstack()
#%%
diversity_data = diversity_data[
    [
        "Asian-Female",
        "Black-Male",
        "White-Female",
        "Asian-Male",
        "White-Male",
    ]
]
diversity_data.plot(kind="bar", stacked=True, rot=0)

plt.title(
    "Clumsy analysis of diversity of authors\nfor books read over the last few years"
)
plt.ylabel("Count of books")
plt.xlabel("Year")
plt.savefig(f"out/clumsyDiversity", bbox_inches="tight")


# %%
fic_data = (
    all_df.groupby(["reading_year", "ficOrNonFic"])
    .size()
    .unstack()
    .plot(kind="bar", stacked=True, rot=0)
)
plt.title("Split between fiction and non fiction by year")
plt.ylabel("Count of books")
plt.xlabel("Year")
plt.savefig(f"out/anualFic_Nonfic", bbox_inches="tight")

# %%
fic_data = (
    all_df.groupby(["compound_diversity", "ficOrNonFic"])
    .size()
    .unstack()
    .plot(kind="bar", stacked=True, rot=0)
)
plt.title('Split between fiction and non fiction by "compound diversity"')
plt.ylabel("Count of books")
plt.xlabel("Somewhat arbitrary Buckets")
plt.savefig(f"out/compound_diversity_Fic_Nonfic", bbox_inches="tight")


# %%
os.listdir("out")


# # %%
# fic_data = fic_data = all_df.groupby(["reading_year", "ficOrNonFic"]).size().unstack()
# fic_data["ratio"] = fic_data.apply(
#     lambda x: Fraction((x.NonFiction / x.Fiction) / 2).limit_denominator(10), axis=1
# )
# fic_data.ratio


# %%
all_df.columns


#%%
all_df.groupby("publication_year").sum().num_pages.sort_index().plot(kind="bar")
plt.title(
    "Number of pages read, split by publication year,"
    "\nof books read in the last 6ish years"
)
plt.ylabel("Pages read")
plt.xlabel("Year")
plt.savefig(f"out/publication_yearBarByPages", bbox_inches="tight")

# %%
all_df.groupby("format").sum().num_pages.sort_index().plot(kind="bar", rot=20)
plt.title(
    "Number of pages read, split by format,\nof books read in the last 6ish years"
)
plt.ylabel("Pages read")
plt.xlabel("Year")
plt.savefig(f"out/formatBarByPages", bbox_inches="tight")
#%%
(
    all_df.groupby(["compound_diversity", "ficOrNonFic"])
    .sum()
    .num_pages.unstack()
    .plot(kind="bar", stacked=True, rot=0)
)
plt.title(
    'Split between fiction and non fiction,\nsplit by "compound diversity", measured by page count'
)
plt.ylabel("Count of pages")
plt.xlabel("Somewhat arbitrary Buckets")
plt.savefig(f"out/compound_diversity_Fic_Nonfic_byPages", bbox_inches="tight")

#%%
all_df.groupby("reading_year").sum().num_pages.sort_index().plot(kind="bar")
plt.title(
    "Number of pages read, split by reading year,"
    "\nof books read in the last 6ish years"
)
plt.ylabel("Pages read")
plt.xlabel("Year")
plt.savefig(f"out/reading_yearBarByPages", bbox_inches="tight")

#%%
all_df.groupby("reading_year").count().num_pages.sort_index().plot(kind="bar")
plt.title(
    "Number of books read, split by reading year,"
    "\nof books read in the last 6ish years"
)
plt.ylabel("Pages read")
plt.xlabel("Year")
plt.savefig(f"out/reading_yearBarByBookCount", bbox_inches="tight")


# %%
(
    all_df.groupby("compound_diversity")
    .mean()
    .num_pages.plot(kind="bar", stacked=True, rot=20)
)
plt.title("Mean number of pages per book by each diversity bucket")
plt.ylabel("pages")
plt.xlabel("Somewhat arbitrary Buckets")
plt.savefig(f"out/compound_diversityAvePages", bbox_inches="tight")
# %%
(all_df.groupby("gender").mean().num_pages.plot(kind="bar", stacked=True, rot=20))
plt.title("Mean number of pages per book by [guessed] gender")
plt.ylabel("pages")
plt.xlabel("Somewhat arbitrary Buckets")
plt.savefig(f"out/sexygenderyAvePages", bbox_inches="tight")

