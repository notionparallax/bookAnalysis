#%%
import requests as r
import json
import xmltodict
import pandas as pd
from dateutil import parser
import matplotlib.pyplot as plt
import datetime
import math


#%%
key = "Da3OYyq578zwEyfahDXRA"
base = "https://www.goodreads.com"
usernum = "115850746"

#%%
me_r = ("{b}/user/show/{u}.xml?key={k}".format(b=base, k=key, u=usernum))
content = Requests.get(url)
xml_data = me_r.content
me = xmltodict.parse(xml_data)

# print(json.dumps(me, indent=2))
shelves = me["GoodreadsResponse"]["user"]["user_shelves"]
shelf = [x for x in shelves["user_shelf"] if x["name"] == ["read"][0]]
shelf


6#%%
read_shelf = r.get(
    f"{base}/review/list/{usernum}.xml?" 
    f"key={key}&v=2" "&shelf=read" "&per_page=200"
)
xml_data = read_shelf.content
read_books = xmltodict.parse(xml_data)
rb = read_books["GoodreadsResponse"]["reviews"]["review"]
books = pd.DataFrame(rb)


#%%
books.sample(4)


#%%
books.columns


#%%
books.drop(
    [
        "votes",
        "spoiler_flag",
        "spoilers_state",
        "shelves",
        "recommended_for",
        "recommended_by",
        "read_count",
        "body",
        "comments_count",
        "link",
        "owned",
    ],
    axis=1,
    inplace=True,
)


#%%
dead_date = parser.parse("2017 12 01 00:00:00 -0800")


def parseDateSafe(date):
    try:
        if (type(date) is str) and (date is not None):
            if type(date) is datetime.datetime:
                return date
            else:
                return parser.parse(date).date()
        else:
            return dead_date.date()
    except Exception as e:
        print(date, e)
        return date


#%%
books["title"] = books.apply(lambda row: row.book["title_without_series"], axis=1)
books["author_1_id"] = books.apply(
    lambda row: row.book["authors"]["author"]["id"], axis=1
)
books["author_1_name"] = books.apply(
    lambda row: row.book["authors"]["author"]["name"], axis=1
)
books["dt_updated"] = books.apply(lambda row: parseDateSafe(row.date_updated), axis=1)
books["dt_started_at"] = books.apply(lambda row: parseDateSafe(row.started_at), axis=1)
books["dt_read_at"] = books.apply(lambda row: parseDateSafe(row.read_at), axis=1)
books["dt_added"] = books.apply(lambda row: parseDateSafe(row.date_added), axis=1)


#%%
books.sample(5)


#%%
fig, ax = plt.subplots()
badRows = []

for index, row in books.iterrows():
    marker = "x"
    if (row.dt_started_at != dead_date) and (row.dt_read_at != dead_date):
        marker = "-"
        ax.plot_date(
            [row.dt_started_at, row.dt_read_at],
            [index, index],
            fmt=marker,
            tz=None,
            xdate=True,
            ydate=False,
        )
        ax.text(
            row.dt_started_at, index, row.title, fontsize=1, verticalalignment="center"
        )

    else:
        badRows.append(row)


fig.autofmt_xdate()
ax.set_xlim([datetime.date(2016, 1, 1), datetime.date(2020, 1, 1)])

plt.show()

#%%
br = pd.DataFrame(badRows)
print(br.shape)
br.head()

#%%
books["html_link"] = books.apply(
    lambda row: f"""<tr><td><a href='{row.url}'>{row.title}</a></td></tr>""", axis=1
)

print("<table>\n", "\n".join(books.html_link), "\n</table>")


# %%
books.to_csv("raw_books.csv")

# def get_publication_year(row):
#     try:
#         if row["publication_year"]:
#             return row["publication_year"]
#         elif row.book_data:
#             if row.book_data["publication_year"]:
#                 return int(row.book_data["publication_year"])
#             elif row.book_data["published"]:
#                 return int(row.book_data["published"])
#             else:
#                 return 0
#         else:
#             return 0
#     except Exception as e:
#         print(e, row, "\n")


# def get_num_pages(row):
#     try:
#         if row["num_pages"] or row.book_data["num_pages"]:
#             return int(row.book_data["num_pages"])
#     except:
#         return 0

# tb["publication_year"] = tb.apply(get_publication_year, axis=1)
# tb["num_pages"] = tb.apply(get_num_pages, axis=1)
# tb["format"] = tb.apply(lambda x: x.book_data["format"], axis=1)
# tb["publisher"] = tb.apply(lambda x: x.book_data["publisher"], axis=1)
# tb.to_excel("modified_books.xlsx")
