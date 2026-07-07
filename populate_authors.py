"""
populate_authors.py  --  build authors.xlsx from existing data + known author info

Run once (or re-run after adding new books) to merge:
  - my_author_inputs.xlsx  (your existing hand-curated data)
  - hard-coded known data for well-known authors
  - blank rows for anyone not yet known

Output: authors.xlsx in the OneDrive book_analysis folder
"""

import re
import pandas as pd

ONEDRIVE = r"C:\Users\bdoherty\OneDrive - BVN\book_analysis"


def normalise(name: str) -> str:
    """Collapse internal whitespace and strip."""
    return re.sub(r"\s+", " ", str(name)).strip()


# ── Known author data ─────────────────────────────────────────────────────────
# Fields: gender, ethnicity, LGBTQI_Authors, Nationality, DeadorAlive
# Ethnicity values in use: Asian | Black | Hispanic | Indigenous | White
# LGBTQI values:  Bisexual | Gay | Lesbian | Straight | Unknown
# Left blank ("") = not confident enough to guess

KNOWN = {
    "A.A. Milne":                   ("Male",   "White",      "Straight", "British",       "Dead"),
    "Ada Palmer":                   ("Female", "White",      "Bisexual", "American",      "Alive"),
    "Adrian Hon":                   ("Male",   "White",      "Unknown",  "British",       "Alive"),
    "Agatha Christie":              ("Female", "White",      "Straight", "British",       "Dead"),
    "Alan C. Martin":               ("Male",   "White",      "Unknown",  "British",       "Alive"),
    "Aldous Huxley":                ("Male",   "White",      "Straight", "British",       "Dead"),
    "Alex Pentland":                ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Alexandra Lange":              ("Female", "White",      "Unknown",  "American",      "Alive"),
    "Alison Page":                  ("Female", "Indigenous", "Unknown",  "Australian",    "Alive"),
    "Andrew F. Smith":              ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Andy Weir":                    ("Male",   "White",      "Straight", "American",      "Alive"),
    "Angélica Gorodischer":         ("Female", "White",      "Unknown",  "Argentine",     "Dead"),
    "Ann Leckie":                   ("Female", "White",      "Unknown",  "American",      "Alive"),
    "Apostolos Doxiadis":           ("Male",   "White",      "Unknown",  "Greek",         "Alive"),
    "Ari R. Meisel":                ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Art Spiegelman":               ("Male",   "White",      "Straight", "American",      "Alive"),
    "Arthur C. Clarke":             ("Male",   "White",      "Unknown",  "British",       "Dead"),
    "Arundhati Roy":                ("Female", "Asian",      "Straight", "Indian",        "Alive"),
    "Ash Maurya":                   ("Male",   "Asian",      "Unknown",  "American",      "Alive"),
    "Atul Gawande":                 ("Male",   "Asian",      "Unknown",  "American",      "Alive"),
    "Barnaby Bennett":              ("Male",   "White",      "Unknown",  "New Zealand",   "Alive"),
    "Beatrix Potter":               ("Female", "White",      "Unknown",  "British",       "Dead"),
    "Becky Chambers":               ("Female", "White",      "Bisexual", "American",      "Alive"),
    "Benjamin Aranda":              ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Benjamin Waber":               ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Ben Waber":                    ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Bertrand Russell":             ("Male",   "White",      "Straight", "British",       "Dead"),
    "Bill Bryson":                  ("Male",   "White",      "Straight", "American",      "Alive"),
    "Bill Moggridge":               ("Male",   "White",      "Unknown",  "British",       "Dead"),
    "BookRags":                     ("",       "",           "",         "",              ""),
    "Bora Chung":                   ("Female", "Asian",      "Unknown",  "Korean",        "Alive"),
    "Bradford Howland":             ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Brandon Keatley":              ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Branko Kolarevic":             ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Brian David Johnson":          ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Bruce Sterling":               ("Male",   "White",      "Straight", "American",      "Alive"),
    "Bryan Caplan":                 ("Male",   "White",      "Straight", "American",      "Alive"),
    "Bryan Lee O'Malley":           ("Male",   "Asian",      "Unknown",  "Canadian",      "Alive"),
    "C. Northcote Parkinson":       ("Male",   "White",      "Straight", "British",       "Dead"),
    "Cal Newport":                  ("Male",   "White",      "Straight", "American",      "Alive"),
    "Camper English":               ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Carlo Ratti":                  ("Male",   "White",      "Unknown",  "Italian",       "Alive"),
    "Carmen Maria Machado":         ("Female", "Hispanic",   "Lesbian",  "American",      "Alive"),
    "Cat Rambo":                    ("Female", "White",      "Bisexual", "American",      "Alive"),
    "Cecil Balmond":                ("Male",   "Asian",      "Unknown",  "British",       "Alive"),
    "Charles Sale":                 ("Male",   "White",      "Unknown",  "American",      "Dead"),
    "Charles Stross":               ("Male",   "White",      "Straight", "British",       "Alive"),
    "Charles Wheelan":              ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Charlotte Wood":               ("Female", "White",      "Unknown",  "Australian",    "Alive"),
    "Chimamanda Ngozi Adichie":     ("Female", "Black",      "Straight", "Nigerian",      "Alive"),
    "China Miéville":               ("Male",   "White",      "Straight", "British",       "Alive"),
    "Chinua Achebe":                ("Male",   "Black",      "Straight", "Nigerian",      "Dead"),
    "Chris Kraus":                  ("Female", "White",      "Unknown",  "American",      "Alive"),
    "Chris Sims":                   ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Christian Rudder":             ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Christopher Alexander":        ("Male",   "White",      "Unknown",  "British",       "Dead"),
    "Christopher Grey":             ("Male",   "White",      "Unknown",  "Unknown",       "Alive"),
    "Christopher Hight":            ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Christopher Ryan":             ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Christopher Yost":             ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Chuck Dixon":                  ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Claire Vaye Watkins":          ("Female", "White",      "Unknown",  "American",      "Alive"),
    "Cordelia Fine":                ("Female", "White",      "Unknown",  "British",       "Alive"),
    "Cormac McCarthy":              ("Male",   "White",      "Straight", "American",      "Dead"),
    "Cory Doctorow":                ("Male",   "White",      "Straight", "Canadian",      "Alive"),
    "Dagmar Richter":               ("Female", "White",      "Unknown",  "German",        "Alive"),
    "Dan Cederholm":                ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Dan Hill":                     ("Male",   "White",      "Unknown",  "Australian",    "Alive"),
    "Dan Roam":                     ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Daniel Kahneman":              ("Male",   "White",      "Straight", "Israeli",       "Dead"),
    "Daniel Keyes":                 ("Male",   "White",      "Straight", "American",      "Dead"),
    "Dave Arnold":                  ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Dave Eggers":                  ("Male",   "White",      "Straight", "American",      "Alive"),
    "David B. Fogel":               ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "David Deutsch":                ("Male",   "White",      "Straight", "British",       "Alive"),
    "David J.C. MacKay":            ("Male",   "White",      "Unknown",  "British",       "Dead"),
    "David Littlefield":            ("Male",   "White",      "Unknown",  "British",       "Alive"),
    "David Macaulay":               ("Male",   "White",      "Unknown",  "British",       "Alive"),
    "David Owen":                   ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "David Wolman":                 ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Deborah Schneiderman":         ("Female", "White",      "Unknown",  "American",      "Alive"),
    "Denis Diderot":                ("Male",   "White",      "Straight", "French",        "Dead"),
    "Donald A. Norman":             ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Douglas Adams":                ("Male",   "White",      "Straight", "British",       "Dead"),
    "Douglas R. Hofstadter":        ("Male",   "White",      "Straight", "American",      "Alive"),
    "Ed Finn":                      ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Edan Lepucki":                 ("Female", "White",      "Unknown",  "American",      "Alive"),
    "Edwin A. Abbott":              ("Male",   "White",      "Unknown",  "British",       "Dead"),
    "Eliezer Yudkowsky":            ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Eliyahu M. Goldratt":          ("Male",   "White",      "Unknown",  "Israeli",       "Dead"),
    "Emily St. John Mandel":        ("Female", "White",      "Unknown",  "Canadian",      "Alive"),
    "Eric Carle":                   ("Male",   "White",      "Unknown",  "American",      "Dead"),
    "Eric Ries":                    ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Eric S. Raymond":              ("Male",   "White",      "Straight", "American",      "Alive"),
    "Erik Brynjolfsson":            ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Erika Hall":                   ("Female", "White",      "Unknown",  "American",      "Alive"),
    "Ernest Cline":                 ("Male",   "White",      "Straight", "American",      "Alive"),
    "Ernest Hemingway":             ("Male",   "White",      "Straight", "American",      "Dead"),
    "Ethan Marcotte":               ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Francisco Laranjo":            ("Male",   "White",      "Unknown",  "Portuguese",    "Alive"),
    "Frank Herbert":                ("Male",   "White",      "Straight", "American",      "Dead"),
    "Frederick P. Brooks Jr.":      ("Male",   "White",      "Unknown",  "American",      "Dead"),
    "Frontinus":                    ("Male",   "White",      "Unknown",  "Roman",         "Dead"),
    "Fyodor Dostoevsky":            ("Male",   "White",      "Straight", "Russian",       "Dead"),
    "Gabriel García Márquez":       ("Male",   "Hispanic",   "Straight", "Colombian",     "Dead"),
    "Gaius Julius Caesar":          ("Male",   "White",      "Unknown",  "Roman",         "Dead"),
    "Gareth Lock":                  ("Male",   "White",      "Unknown",  "British",       "Alive"),
    "Gene Kim":                     ("Male",   "Asian",      "Unknown",  "American",      "Alive"),
    "George R.R. Martin":           ("Male",   "White",      "Straight", "American",      "Alive"),
    "Gianrico Carofiglio":          ("Male",   "White",      "Unknown",  "Italian",       "Alive"),
    "Graham Greene":                ("Male",   "White",      "Straight", "British",       "Dead"),
    "Graham Priest":                ("Male",   "White",      "Unknown",  "British",       "Alive"),
    "Greg Egan":                    ("Male",   "White",      "Unknown",  "Australian",    "Alive"),
    "Gretchen Felker-Martin":       ("Female", "White",      "Gay",      "American",      "Alive"),
    "Gwyn Headley":                 ("Male",   "White",      "Unknown",  "British",       "Alive"),
    "H.G. Wells":                   ("Male",   "White",      "Straight", "British",       "Dead"),
    "Hans Ibelings":                ("Male",   "White",      "Unknown",  "Dutch",         "Alive"),
    "Haruki Murakami":              ("Male",   "Asian",      "Straight", "Japanese",      "Alive"),
    "Harvey Molotch":               ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Heather Radke":                ("Female", "White",      "Unknown",  "American",      "Alive"),
    "Heinz Insu Fenkl":             ("Male",   "Asian",      "Unknown",  "American",      "Alive"),
    "Henry James":                  ("Male",   "White",      "Unknown",  "American",      "Dead"),
    "Herbert A. Simon":             ("Male",   "White",      "Straight", "American",      "Dead"),
    "Herman Melville":              ("Male",   "White",      "Unknown",  "American",      "Dead"),
    "Hermann Hesse":                ("Male",   "White",      "Straight", "German",        "Dead"),
    "Hervé This":                   ("Male",   "White",      "Unknown",  "French",        "Alive"),
    "Hilary Mantel":                ("Female", "White",      "Straight", "British",       "Dead"),
    "Homer":                        ("Male",   "White",      "Unknown",  "Greek",         "Dead"),
    "Iain M. Banks":                ("Male",   "White",      "Straight", "British",       "Dead"),
    "Ian Gilbert":                  ("Male",   "White",      "Unknown",  "British",       "Alive"),
    "Ian Stewart":                  ("Male",   "White",      "Unknown",  "British",       "Alive"),
    "Ingeborg Flagge":              ("Female", "White",      "Unknown",  "German",        "Alive"),
    "Isaac Asimov":                 ("Male",   "White",      "Straight", "American",      "Dead"),
    "Italo Calvino":                ("Male",   "White",      "Straight", "Italian",       "Dead"),
    "J.D. Salinger":                ("Male",   "White",      "Straight", "American",      "Dead"),
    "J.G. Ballard":                 ("Male",   "White",      "Straight", "British",       "Dead"),
    "J.R.R. Tolkien":               ("Male",   "White",      "Straight", "British",       "Dead"),
    "Jack Weatherford":             ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "James Martin":                 ("Male",   "White",      "Unknown",  "Unknown",       "Alive"),
    "James P. Carse":               ("Male",   "White",      "Unknown",  "American",      "Dead"),
    "James Smythe":                 ("Male",   "White",      "Unknown",  "British",       "Alive"),
    "Janet W. Hardy":               ("Female", "White",      "Bisexual", "American",      "Alive"),
    "Jason Fried":                  ("Male",   "White",      "Straight", "American",      "Alive"),
    "Jennifer Henshaw":             ("Female", "White",      "Unknown",  "Unknown",       "Alive"),
    "Jeremy Keith":                 ("Male",   "White",      "Unknown",  "Irish",         "Alive"),
    "Jesse Reiser":                 ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Jia Tolentino":                ("Female", "Asian",      "Straight", "American",      "Alive"),
    "Jill Heinerth":                ("Female", "White",      "Unknown",  "Canadian",      "Alive"),
    "Jim Ottaviani":                ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Joan Didion":                  ("Female", "White",      "Straight", "American",      "Dead"),
    "Joep van Lieshout":            ("Male",   "White",      "Unknown",  "Dutch",         "Alive"),
    "Johann David Wyss":            ("Male",   "White",      "Unknown",  "Swiss",         "Dead"),
    "John Allen Paulos":            ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "John Marsden":                 ("Male",   "White",      "Unknown",  "Australian",    "Alive"),
    "John Wyndham":                 ("Male",   "White",      "Unknown",  "British",       "Dead"),
    "Jonathan Glover":              ("Male",   "White",      "Unknown",  "British",       "Alive"),
    "Jonathan Swift":               ("Male",   "White",      "Straight", "Irish",         "Dead"),
    "Jorge Luis Borges":            ("Male",   "White",      "Straight", "Argentine",     "Dead"),
    "Joseph Brassey":               ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Joseph Heller":                ("Male",   "White",      "Straight", "American",      "Dead"),
    "Jules Verne":                  ("Male",   "White",      "Straight", "French",        "Dead"),
    "Jung Chang":                   ("Female", "Asian",      "Straight", "Chinese",       "Alive"),
    "K.A. Stroud":                  ("Male",   "White",      "Unknown",  "British",       "Dead"),
    "Kakuzō Okakura":               ("Male",   "Asian",      "Unknown",  "Japanese",      "Dead"),
    "Karel Čapek":                  ("Male",   "White",      "Straight", "Czech",         "Dead"),
    "Kathryn Allan":                ("Female", "White",      "Unknown",  "Canadian",      "Alive"),
    "Keanu Reeves":                 ("Male",   "Asian",      "Unknown",  "Canadian",      "Alive"),
    "Kelly Sue DeConnick":          ("Female", "White",      "Unknown",  "American",      "Alive"),
    "Ken MacLeod":                  ("Male",   "White",      "Straight", "British",       "Alive"),
    "Kid Koala":                    ("Male",   "Asian",      "Unknown",  "Canadian",      "Alive"),
    "Kim Stanley Robinson":         ("Male",   "White",      "Straight", "American",      "Alive"),
    "Knut Hamsun":                  ("Male",   "White",      "Straight", "Norwegian",     "Dead"),
    "Lars Spuybroek":               ("Male",   "White",      "Unknown",  "Dutch",         "Alive"),
    "Larry Gonick":                 ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Leonard Mlodinow":             ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Lewis Carroll":                ("Male",   "White",      "Unknown",  "British",       "Dead"),
    "Ling Ma":                      ("Female", "Asian",      "Unknown",  "American",      "Alive"),
    "Liu Cixin":                    ("Male",   "Asian",      "Straight", "Chinese",       "Alive"),
    "Luciano Floridi":              ("Male",   "White",      "Unknown",  "Italian",       "Alive"),
    "Lucy Hawking":                 ("Female", "White",      "Unknown",  "British",       "Alive"),
    "Luigi Serafini":               ("Male",   "White",      "Unknown",  "Italian",       "Alive"),
    "Luke Wroblewski":              ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "M. Hensel":                    ("Male",   "White",      "Unknown",  "German",        "Alive"),
    "Madeline Miller":              ("Female", "White",      "Bisexual", "American",      "Alive"),
    "Madeleine Ryan":               ("Female", "White",      "Unknown",  "Australian",    "Alive"),
    "Manu Cornet":                  ("Male",   "White",      "Unknown",  "French",        "Alive"),
    "Marcus Aurelius":              ("Male",   "White",      "Unknown",  "Roman",         "Dead"),
    "Margaret Mead":                ("Female", "White",      "Bisexual", "American",      "Dead"),
    "Margo Neale":                  ("Female", "White",      "Unknown",  "Australian",    "Alive"),
    "Maria Rita Perbellini":        ("Female", "White",      "Unknown",  "Italian",       "Alive"),
    "Marie Kondō":                  ("Female", "Asian",      "Straight", "Japanese",      "Alive"),
    "Mark Coeckelbergh":            ("Male",   "White",      "Unknown",  "Belgian",       "Alive"),
    "Mark Twain":                   ("Male",   "White",      "Straight", "American",      "Dead"),
    "Martin J. Rees":               ("Male",   "White",      "Unknown",  "British",       "Alive"),
    "Masaaki Imai":                 ("Male",   "Asian",      "Unknown",  "Japanese",      "Dead"),
    "Matt Wynne":                   ("Male",   "White",      "Unknown",  "British",       "Alive"),
    "Max Brooks":                   ("Male",   "White",      "Straight", "American",      "Alive"),
    "Maxine Beneba Clarke":         ("Female", "Black",      "Unknown",  "Australian",    "Alive"),
    "Meghan Doherty":               ("Female", "White",      "Unknown",  "American",      "Alive"),
    "Melanie Mitchell":             ("Female", "White",      "Unknown",  "American",      "Alive"),
    "Melissa Gregg":                ("Female", "White",      "Unknown",  "Australian",    "Alive"),
    "Michael Allingham":            ("Male",   "White",      "Unknown",  "British",       "Alive"),
    "Michael Green":                ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Michael J. Sandel":            ("Male",   "White",      "Straight", "American",      "Alive"),
    "Michael Ondaatje":             ("Male",   "Asian",      "Unknown",  "Canadian",      "Alive"),
    "Michel Ribera":                ("Male",   "White",      "Unknown",  "French",        "Alive"),
    "Michele Emmer":                ("Male",   "White",      "Unknown",  "Italian",       "Alive"),
    "Michelle Tam":                 ("Female", "Asian",      "Unknown",  "American",      "Alive"),
    "Milan Kundera":                ("Male",   "White",      "Straight", "Czech",         "Dead"),
    "Milo Manara":                  ("Male",   "White",      "Unknown",  "Italian",       "Alive"),
    "Mykaela Saunders":             ("Female", "Indigenous", "Unknown",  "Australian",    "Alive"),
    "N.K. Jemisin":                 ("Female", "Black",      "Straight", "American",      "Alive"),
    "Nadia Eghbal":                 ("Female", "White",      "Unknown",  "American",      "Alive"),
    "Naomi Alderman":               ("Female", "White",      "Lesbian",  "British",       "Alive"),
    "Neal Stephenson":              ("Male",   "White",      "Straight", "American",      "Alive"),
    "Neil Gaiman":                  ("Male",   "White",      "Straight", "British",       "Alive"),
    "Nevil Shute":                  ("Male",   "White",      "Straight", "British",       "Dead"),
    "Niccolò Machiavelli":          ("Male",   "White",      "Unknown",  "Italian",       "Dead"),
    "Nicholas Negroponte":          ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Nick Bostrom":                 ("Male",   "White",      "Straight", "Swedish",       "Alive"),
    "Nigel Lesmoir-Gordon":         ("Male",   "White",      "Unknown",  "British",       "Alive"),
    "Nnedi Okorafor":               ("Female", "Black",      "Unknown",  "American",      "Alive"),
    "Octavia E. Butler":            ("Female", "Black",      "Unknown",  "American",      "Dead"),
    "Olaf Breidbach":               ("Male",   "White",      "Unknown",  "German",        "Dead"),
    "Orson Scott Card":             ("Male",   "White",      "Straight", "American",      "Alive"),
    "P.W. Singer":                  ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Partha Dasgupta":              ("Male",   "Asian",      "Unknown",  "Indian",        "Alive"),
    "Pat Barker":                   ("Female", "White",      "Straight", "British",       "Alive"),
    "Pat Cadigan":                  ("Female", "White",      "Unknown",  "American",      "Alive"),
    "Paul Beatty":                  ("Male",   "Black",      "Straight", "American",      "Alive"),
    "Paul Coates":                  ("Male",   "White",      "Unknown",  "British",       "Alive"),
    "Paul Graham":                  ("Male",   "White",      "Unknown",  "British",       "Alive"),
    "Paul Oyer":                    ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Paul R. Halmos":               ("Male",   "White",      "Unknown",  "Hungarian",     "Dead"),
    "Peter Carey":                  ("Male",   "White",      "Straight", "Australian",    "Alive"),
    "Peter Drayton":                ("Male",   "White",      "Unknown",  "British",       "Alive"),
    "Peter F. Drucker":             ("Male",   "White",      "Straight", "Austrian",      "Dead"),
    "Peter Godfrey-Smith":          ("Male",   "White",      "Unknown",  "Australian",    "Alive"),
    "Philip E. Tetlock":            ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Philip K. Dick":               ("Male",   "White",      "Straight", "American",      "Dead"),
    "Philip Pullman":               ("Male",   "White",      "Straight", "British",       "Alive"),
    "R.D. Hanson":                  ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Ramez Naam":                   ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Ramsey Campbell":              ("Male",   "White",      "Unknown",  "British",       "Alive"),
    "Randall Munroe":               ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Ray Bradbury":                 ("Male",   "White",      "Straight", "American",      "Dead"),
    "Reay Tannahill":               ("Female", "White",      "Unknown",  "Scottish",      "Dead"),
    "René Redzepi":                 ("Male",   "White",      "Unknown",  "Danish",        "Alive"),
    "Renee Cooper":                 ("Female", "White",      "Unknown",  "Unknown",       "Alive"),
    "Richard Dawkins":              ("Male",   "White",      "Straight", "British",       "Alive"),
    "Richard H. Thaler":            ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Richard Matheson":             ("Male",   "White",      "Unknown",  "American",      "Dead"),
    "Richard P. Feynman":           ("Male",   "White",      "Straight", "American",      "Dead"),
    "Richard Powers":               ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Richard Sennett":              ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Roald Dahl":                   ("Male",   "White",      "Straight", "British",       "Dead"),
    "Robert A. Heinlein":           ("Male",   "White",      "Straight", "American",      "Dead"),
    "Robert B. Cialdini":           ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Robert Coram":                 ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Robert F. Burgess":            ("Male",   "White",      "Unknown",  "American",      "Dead"),
    "Robert H. Frank":              ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Robert Kirkman":               ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Robert M. Pirsig":             ("Male",   "White",      "Straight", "American",      "Dead"),
    "Robin Hanson":                 ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Robin J. Wilson":              ("Male",   "White",      "Unknown",  "British",       "Alive"),
    "Rory Hyde":                    ("Male",   "White",      "Unknown",  "Australian",    "Alive"),
    "Rudyard Kipling":              ("Male",   "White",      "Straight", "British",       "Dead"),
    "Scott McCloud":                ("Male",   "White",      "Straight", "American",      "Alive"),
    "Sean Lally":                   ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Seneca":                       ("Male",   "White",      "Unknown",  "Roman",         "Dead"),
    "Sheck Exley":                  ("Male",   "White",      "Unknown",  "American",      "Dead"),
    "Sidney W. Mintz":              ("Male",   "White",      "Unknown",  "American",      "Dead"),
    "Simon Pridmore":               ("Male",   "White",      "Unknown",  "British",       "Alive"),
    "Sophia Vyzoviti":              ("Female", "White",      "Unknown",  "Greek",         "Alive"),
    "Stefan Panis":                 ("Male",   "White",      "Unknown",  "Belgian",       "Alive"),
    "Stephen Fry":                  ("Male",   "White",      "Gay",      "British",       "Alive"),
    "Stephen King":                 ("Male",   "White",      "Straight", "American",      "Alive"),
    "Steve Grand":                  ("Male",   "White",      "Unknown",  "British",       "Alive"),
    "Steven D. Levitt":             ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Stewart Brand":                ("Male",   "White",      "Straight", "American",      "Alive"),
    "Stuart Sutherland":            ("Male",   "White",      "Unknown",  "British",       "Dead"),
    "Susan DeFreitas":              ("Female", "White",      "Unknown",  "American",      "Alive"),
    "T.P. Louise":                  ("Female", "White",      "Unknown",  "Australian",    "Alive"),
    "Terry Pratchett":              ("Male",   "White",      "Straight", "British",       "Dead"),
    "Thea von Harbou":              ("Female", "White",      "Unknown",  "German",        "Dead"),
    "Thomas S. Kuhn":               ("Male",   "White",      "Straight", "American",      "Dead"),
    "Tim Harford":                  ("Male",   "White",      "Straight", "British",       "Alive"),
    "Tim Mulgan":                   ("Male",   "White",      "Unknown",  "New Zealand",   "Alive"),
    "Tim Winton":                   ("Male",   "White",      "Straight", "Australian",    "Alive"),
    "Timothy Gowers":               ("Male",   "White",      "Unknown",  "British",       "Alive"),
    "Tom DeMarco":                  ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Tom McCarthy":                 ("Male",   "White",      "Unknown",  "British",       "Alive"),
    "Tom Porter":                   ("Male",   "White",      "Unknown",  "British",       "Alive"),
    "Tyler Kord":                   ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Tyler Page":                   ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Tyson Yunkaporta":             ("Male",   "Indigenous", "Unknown",  "Australian",    "Alive"),
    "Unknown":                      ("",       "",           "",         "",              ""),
    "Ursula K. Le Guin":            ("Female", "White",      "Straight", "American",      "Dead"),
    "Vaclav Smil":                  ("Male",   "White",      "Unknown",  "Czech",         "Alive"),
    "Vance Harlow":                 ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Venkatesh G. Rao":             ("Male",   "Asian",      "Unknown",  "Indian",        "Alive"),
    "Vladimir Nabokov":             ("Male",   "White",      "Straight", "Russian",       "Dead"),
    "Voltaire":                     ("Male",   "White",      "Straight", "French",        "Dead"),
    "Wayne C. Booth":               ("Male",   "White",      "Unknown",  "American",      "Dead"),
    "Will Durant":                  ("Male",   "White",      "Straight", "American",      "Dead"),
    "Will Larson":                  ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "William Gibson":               ("Male",   "White",      "Straight", "Canadian",      "Alive"),
    "William J. Mitchell":          ("Male",   "White",      "Unknown",  "Australian",    "Dead"),
    "William Zinsser":              ("Male",   "White",      "Unknown",  "American",      "Dead"),
    "Xia Jia":                      ("Female", "Asian",      "Unknown",  "Chinese",       "Alive"),
    "Yehuda E. Kalay":              ("Male",   "White",      "Unknown",  "Israeli",       "Alive"),
    "Yevgeny Zamyatin":             ("Male",   "White",      "Unknown",  "Russian",       "Dead"),
    "Yuval Noah Harari":            ("Male",   "White",      "Gay",      "Israeli",       "Alive"),
    "Zach Weinersmith":             ("Male",   "White",      "Unknown",  "American",      "Alive"),
    # whitespace variants that appear in raw data
    "leonard-mlodinow":             ("Male",   "White",      "Unknown",  "American",      "Alive"),
    # additional authors identified after first run
    "Anthony Burgess":              ("Male",   "White",      "Straight", "British",       "Dead"),
    "Christopher W. Alexander":     ("Male",   "White",      "Unknown",  "British",       "Dead"),
    "Damian Duffy":                 ("Male",   "Black",      "Unknown",  "American",      "Alive"),
    "Denise Scott Brown":           ("Female", "White",      "Unknown",  "American",      "Alive"),
    "Erik Davis":                   ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Julius Wiedermann":            ("Male",   "White",      "Unknown",  "German",        "Alive"),
    "Kostas Terzidis":              ("Male",   "White",      "Unknown",  "Greek",         "Alive"),
    "Stephen Randy Davis":          ("Male",   "White",      "Unknown",  "American",      "Alive"),
    "Stephen Wolfram":              ("Male",   "White",      "Straight", "British",       "Alive"),
    "Alberto T. Estévez":           ("Male",   "White",      "Unknown",  "Spanish",       "Alive"),
}

COLS = ["name", "gender", "ethnicity", "LGBTQI_Authors", "Nationality", "DeadorAlive"]


def main():
    # ── Load existing hand-curated data ───────────────────────────────────────
    existing = pd.read_excel(f"{ONEDRIVE}/my_author_inputs.xlsx")[COLS]
    # Drop junk rows (names that are "0" or blank)
    existing = existing[
        existing["name"].apply(lambda x: str(x).strip() not in ("", "0", "nan"))
    ].copy()
    existing["_key"] = existing["name"].apply(normalise)

    existing_by_key = existing.set_index("_key").to_dict("index")

    # ── Load all unique authors from books ────────────────────────────────────
    books = pd.read_csv("books_annotated.csv")
    raw_names = books["author_1_name"].dropna().unique()

    records = []
    matched_existing = 0
    matched_known = 0
    blank = 0

    for raw in sorted(raw_names):
        key = normalise(raw)
        display = key  # use normalised name as canonical display name

        if key in existing_by_key:
            row = existing_by_key[key]
            records.append({
                "name":           display,
                "gender":         row.get("gender", ""),
                "ethnicity":      row.get("ethnicity", ""),
                "LGBTQI_Authors": row.get("LGBTQI_Authors", ""),
                "Nationality":    row.get("Nationality", ""),
                "DeadorAlive":    row.get("DeadorAlive", ""),
            })
            matched_existing += 1
        elif key in KNOWN:
            g, e, s, n, d = KNOWN[key]
            records.append({
                "name":           display,
                "gender":         g,
                "ethnicity":      e,
                "LGBTQI_Authors": s,
                "Nationality":    n,
                "DeadorAlive":    d,
            })
            matched_known += 1
        else:
            records.append({
                "name":           display,
                "gender":         "",
                "ethnicity":      "",
                "LGBTQI_Authors": "",
                "Nationality":    "",
                "DeadorAlive":    "",
            })
            blank += 1

    result = pd.DataFrame(records, columns=COLS)
    out = f"{ONEDRIVE}/authors.xlsx"
    result.to_excel(out, index=False)

    print(f"Written {len(result)} authors to {out}")
    print(f"  from existing data:  {matched_existing}")
    print(f"  from known dict:     {matched_known}")
    print(f"  left blank:          {blank}")
    if blank:
        blanks = [r["name"] for r in records if not r["gender"]]
        print("\nAuthors with no data (fill in manually):")
        for n in blanks:
            print(f"  {n}")


if __name__ == "__main__":
    main()
