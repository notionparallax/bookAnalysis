#%%
from dateutil import parser
import datetime
import json
import math
import matplotlib.pyplot as plt
import os
import pandas as pd
import requests as r
import xmltodict

# %%
tb = pd.read_excel("modified_books.xlsx")

tb.sort_values(by="dt_started_at", ascending=False, inplace=True)
tb.reset_index(drop=True, inplace=True)
#%%
plt.rcParams["figure.figsize"] = (8.27, 11.69)
fig, ax = plt.subplots()
for index, row in tb.iterrows():
    marker = "-"

    ax.plot_date(
        [row.dt_started_at, row.dt_read_at],
        [index, index],
        fmt=marker,
        tz=None,
        xdate=True,
        ydate=False,
        lw=2.5,
    )
    ax.text(
        row.dt_started_at,
        index,
        f"{row.author_1_name}: {row.title}",
        fontsize=1.5,
        verticalalignment="center",
    )

fig.autofmt_xdate()
ax.set_xlim([datetime.date(2013, 1, 1), datetime.date(2021, 1, 1)])
plt.tick_params(axis="y", which="both", left=False, right=False, labelleft=False)
plt.grid(True)
plt.title("Books that Ben has read")
plt.savefig(f"out/bookWaterfall", bbox_inches="tight")
plt.savefig(f"out/bookWaterfall.pdf", bbox_inches="tight")
#%%
cols_to_drop = [
    "Unnamed: 0",
    "book",
    "started_at",
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
    tb["book_data"] = tb.apply(
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


tb.book_data = tb.book_data.apply(dataise)
tb.head()
#%%
plt.rcParams["figure.figsize"] = (8, 8)
# %%
print(
    f"Median year: {int(tb.publication_year.median())}, mean year: {int(tb.publication_year.mean())}"
)
#%%
tb.publication_year.value_counts().sort_index().plot(kind="bar")
plt.title("Publication year of books read in the last 6ish years")
plt.ylabel("Count of books")
plt.xlabel("Year")
plt.savefig(f"out/publicationYearBar", bbox_inches="tight")
#%%
tb.publication_year.hist(bins=50)
plt.title("Publication year of books read in the last 6ish years")
plt.ylabel("Count of books")
plt.xlabel("Year")
plt.savefig(f"out/publicationYearHist", bbox_inches="tight")

# %%
print(
    f"Median pages: {int(tb.num_pages.median())}, mean pages: {int(tb.num_pages.mean())}"
)
#%%
tb.num_pages.hist(bins=45)
plt.title("Number of pages in these books")
plt.ylabel("Count of books")
plt.xlabel("Number of pages")
plt.savefig(f"out/numPages", bbox_inches="tight")

#%%
tb.format.value_counts().plot(kind="bar", rot=20)
plt.title("Format")
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
tb.author_1_name.value_counts()[:30].plot.barh()
plt.title("First named author, top 30")
plt.xlabel("Count of books")
plt.ylabel("Name of first-listed author")
plt.savefig(f"out/author_top_30", bbox_inches="tight")
#%%
tb.rating.hist(bins=4)
plt.title("My rating")
plt.ylabel("Count of books")
plt.xlabel("What I've rated this book")
plt.savefig(f"out/rating", bbox_inches="tight")
#%%
all_authors = []
for index, row in tb.iterrows():
    all_authors.append(row.book_data["authors"]["author"])
authors_df = pd.DataFrame(all_authors)
authors_df.drop_duplicates(subset="name", inplace=True)
authors_df.reset_index(drop=True, inplace=True)
authors_df["image"] = authors_df.apply(lambda x: x.image_url["#text"], axis=1)
authors_df.average_rating = authors_df.average_rating.apply(float)
authors_df.ratings_count = authors_df.ratings_count.apply(int)
authors_df.text_reviews_count = authors_df.text_reviews_count.apply(int)
cols_to_drop = ["image_url", "role", "small_image_url"]
for c in cols_to_drop:
    try:
        authors_df.drop(c, axis=1, inplace=True)
    except Exception as e:
        print(e)
# authors_df.to_excel("authors.xlsx")
authors_df.head()
#%%
authors_df.average_rating.hist()

# %%
authors_df.ratings_count.hist()
#%%
authors_df.text_reviews_count.hist()

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
adf = pd.read_excel("authors.xlsx")
adf.head()
#%%
adf.sexygendery.value_counts().plot(kind="bar", rot=0)
plt.title("Gender of unique first authors")
plt.ylabel("Count of authors")
plt.xlabel("The gender I've guessed")
plt.savefig(f"out/Gender_count_of_unique_first_authors", bbox_inches="tight")
#%%
adf.ethnicity.value_counts().plot(kind="bar", rot=0)
plt.title("Ethnicity of unique first authors")
plt.ylabel("Count of authors")
plt.xlabel("The ethnicity I've guessed")
plt.savefig(f"out/first_author_ethnicity", bbox_inches="tight")
#%%
adf["compound_diversity"] = adf.apply(
    lambda x: f"{x.ethnicity}-{x.sexygendery}", axis=1
)
adf.compound_diversity.value_counts().plot(kind="bar")
plt.title('"Compound" diversity of unique first authors')
plt.ylabel("Count of authors")
plt.xlabel("joined together")
plt.savefig(f"out/compundDiversity", bbox_inches="tight")
#%%
all_df = tb.merge(adf, right_on="name", left_on="author_1_name")
all_df.sample(4)
#%%
all_df.sexygendery.value_counts().plot(kind="bar", rot=0)
plt.title("Books read, split by Gender of unique first author")
plt.ylabel("Count of books")
plt.xlabel("The gender I've guessed")
plt.savefig(f"out/gender_of_books_read", bbox_inches="tight")
#%%
all_df.ethnicity.value_counts().plot(kind="bar", rot=0)
plt.title("Ethnicity of unique first authors")
plt.ylabel("Count of books")
plt.xlabel("The ethnicity I've guessed")
plt.savefig(f"out/Ethnicity_of_books_read", bbox_inches="tight")
#%%
all_df["reading_year"] = all_df.dt_started_at.apply(lambda x: x.year)
#%%
# from : https://stackoverflow.com/a/34919066/1835727
diversity_data = all_df.groupby(["reading_year", "compound_diversity"]).size().unstack()
#%%
diversity_data = diversity_data[
    [
        "Asian-Woman",
        "Black-Woman",
        "White-Woman",
        "Asian-Man",  #
        "Black-Man",
        "White-Man",
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


# %%
from fractions import Fraction

fic_data = fic_data = all_df.groupby(["reading_year", "ficOrNonFic"]).size().unstack()
fic_data["ratio"] = fic_data.apply(
    lambda x: Fraction((x.NonFiction / x.Fiction) / 2).limit_denominator(10), axis=1
)
fic_data.ratio
