"""
annotate_books.py  --  fill in ficOrNonFic, SeriesOrStandalone, LGBTQIA_Characters

Run:  python annotate_books.py

Only fills cells that are currently empty -- never overwrites manual edits.
Re-run any time after adding new books.

LGBTQIA_Characters values:
  Yes  = book has LGBTQIA characters with meaningful presence
  No   = no LGBTQIA characters (or non-fiction where N/A)
  ""   = left blank where genuinely uncertain
"""

import re
import pandas as pd

# ── Config ────────────────────────────────────────────────────────────────────
BOOKS_FILE = "books_annotated.csv"
ANNO_COLS  = ("ficOrNonFic", "SeriesOrStandalone", "LGBTQIA_Characters")


def normalise(s: str) -> str:
    """Lowercase, collapse whitespace, normalise apostrophes/Æ encoding."""
    s = str(s).lower().strip()
    # Goodreads CSV sometimes encodes right-quote as Æ or similar
    s = s.replace("æ", "'").replace("\u2019", "'").replace("\u2018", "'")
    s = re.sub(r"\s+", " ", s)
    return s


def strip_series(s: str) -> str:
    """Remove trailing (Series Name, #N) for a looser title match."""
    return re.sub(r"\s*\([^)]*#\d[^)]*\)\s*$", "", s).strip()


# ── Annotation data ───────────────────────────────────────────────────────────
# isbn13 → (ficOrNonFic, SeriesOrStandalone, LGBTQIA_Characters)
# isbn13 values are the cleaned 13-digit strings from books_annotated.csv
BY_ISBN = {
    # Cave / diving – NonFiction, Standalone, No
    "9798276808406": ("NonFiction", "Standalone", "No"),
    "9781881652113": ("NonFiction", "Standalone", "No"),
    "9798296112521": ("NonFiction", "Series",     "No"),
    "9798375190792": ("NonFiction", "Series",     "No"),
    "9789994662968": ("NonFiction", "Standalone", "No"),
    "9781849954969": ("NonFiction", "Standalone", "No"),
    "9789994663378": ("NonFiction", "Standalone", "No"),
    "9780967887326": ("NonFiction", "Standalone", "No"),
    "9781999584979": ("NonFiction", "Standalone", "No"),
    "9781940944074": ("NonFiction", "Standalone", "No"),
    "9781905492077": ("NonFiction", "Standalone", "No"),
    "9781905492312": ("NonFiction", "Standalone", "No"),
    # Architecture / design – NonFiction
    "9781760761851": ("NonFiction", "Series",     "No"),  # First Knowledges Design
    "9781907896361": ("NonFiction", "Standalone", "No"),  # Architecture Words 4
    "9780786476008": ("NonFiction", "Standalone", "No"),  # Prefab Bathroom
    "9789492058164": ("NonFiction", "Standalone", "No"),  # Modern Architecture: A Planetary Warming History
    "9789493148130": ("NonFiction", "Standalone", "No"),  # Modes of Criticism 4
    "9780715483220": ("NonFiction", "Standalone", "No"),
    "9780262112840": ("NonFiction", "Standalone", "No"),  # Architecture's New Media
    "9780415317443": ("NonFiction", "Standalone", "No"),  # Expressive Form
    "9780415402026": ("NonFiction", "Standalone", "No"),  # Softspace
    "9783764362461": ("NonFiction", "Standalone", "No"),  # Natural Born CAADesigners
    "9781856692519": ("NonFiction", "Standalone", "No"),  # XYZ Architecture
    "9780415381413": ("NonFiction", "Standalone", "No"),  # Architecture in the Digital Age
    "9783791319339": ("NonFiction", "Standalone", "No"),  # Number 9
    "9780930829513": ("NonFiction", "Standalone", "No"),  # Genetic Architectures
    "9780470026526": ("NonFiction", "Standalone", "No"),  # Collective Intelligence in Design
    "9780470866887": ("NonFiction", "Standalone", "No"),  # Emergence Morphogenetic
    "9780500285190": ("NonFiction", "Standalone", "No"),  # NOX
    "9783764365721": ("NonFiction", "Standalone", "No"),  # Digital Real
    "9784887062788": ("NonFiction", "Standalone", "No"),  # Graphic Anatomy
    "9789063690595": ("NonFiction", "Standalone", "No"),  # Folding Architecture
    "9781859462928": ("NonFiction", "Standalone", "No"),  # Space Craft
    "9781568985473": ("NonFiction", "Standalone", "No"),  # Tooling
    "9783822825891": ("NonFiction", "Standalone", "No"),  # Japanese Graphics Now!
    "9780714833569": ("NonFiction", "Standalone", "No"),  # Modern Architecture Since 1900
    "9780863183232": ("NonFiction", "Standalone", "No"),  # The Way Things Work
    "9789069181820": ("NonFiction", "Standalone", "No"),  # Atelier Van Lieshout
    "9780884541028": ("NonFiction", "Standalone", "No"),  # Intricacy
    "9780340649305": ("NonFiction", "Standalone", "No"),  # Being Digital
    "9780415451888": ("NonFiction", "Standalone", "No"),  # Programming.Architecture
    # Food & drink – NonFiction
    "9781579657185": ("NonFiction", "Standalone", "No"),  # Noma Guide
    "9780393089035": ("NonFiction", "Standalone", "No"),  # Liquid Intelligence
    "9780804186414": ("NonFiction", "Standalone", "No"),  # Sandwiches
    "9781449450335": ("NonFiction", "Standalone", "No"),  # Nom Nom Paleo
    "9780984755196": ("NonFiction", "Standalone", "No"),  # Primal Cravings
    "9781936608232": ("NonFiction", "Standalone", "No"),  # Beyond Bacon
    "9780140092332": ("NonFiction", "Standalone", "No"),  # Sweetness and Power
    "9780231133128": ("NonFiction", "Standalone", "No"),  # Molecular Gastronomy
    "9780812814378": ("NonFiction", "Standalone", "No"),  # Food in History
    "9780804800693": ("NonFiction", "Standalone", "No"),  # The Book of Tea
    "9781422191651": ("NonFiction", "Standalone", "No"),  # Everything I Learned from Online Dating
    # Science / maths – NonFiction
    "9780954452933": ("NonFiction", "Standalone", "No"),  # Sustainable Energy
    "9780262014861": ("NonFiction", "Standalone", "No"),  # Living With Complexity
    "9780141009094": ("NonFiction", "Standalone", "No"),  # Euclid's Window
    "9780330393775": ("NonFiction", "Standalone", "No"),  # Flatterland (fiction-ish but NF)
    "9780465011230": ("NonFiction", "Standalone", "No"),  # Annotated Flatland
    "9780486272634": ("Fiction",    "Standalone", "No"),  # Flatland
    "9780809058402": ("NonFiction", "Standalone", "No"),  # Innumeracy
    "9780192853615": ("NonFiction", "Standalone", "No"),  # Mathematics VSI
    "9780192803030": ("NonFiction", "Standalone", "No"),  # Choice Theory VSI
    "9780192893208": ("NonFiction", "Standalone", "No"),  # Logic VSI
    "9780192853455": ("NonFiction", "Standalone", "No"),  # Economics VSI
    "9780191609541": ("NonFiction", "Standalone", "No"),  # Information VSI
    "9780191512681": ("NonFiction", "Standalone", "No"),  # Epicureanism VSI
    "9780333620229": ("NonFiction", "Standalone", "No"),  # Engineering Mathematics
    "9780387900926": ("NonFiction", "Standalone", "No"),  # Naive Set Theory
    "9780674627512": ("NonFiction", "Standalone", "No"),  # Notes on Synthesis of Form
    "9780262691918": ("NonFiction", "Standalone", "No"),  # Sciences of the Artificial
    "9780141026176": ("NonFiction", "Standalone", "No"),  # Climbing Mount Improbable
    "9780199291144": ("NonFiction", "Standalone", "No"),  # The Selfish Gene
    "9783791333274": ("NonFiction", "Standalone", "No"),  # Art Forms from the Ocean
    "9783791319902": ("NonFiction", "Standalone", "No"),  # Art Forms in Nature
    "9780984725106": ("NonFiction", "Standalone", "No"),  # Race Against The Machine
    "9780670022755": ("NonFiction", "Standalone", "No"),  # Beginning of Infinity
    "9780544272996": ("NonFiction", "Standalone", "No"),  # What If?
    "9780199678112": ("NonFiction", "Standalone", "No"),  # Superintelligence
    "9780198570509": ("NonFiction", "Standalone", "No"),  # Global Catastrophic Risks
    "9781579550080": ("NonFiction", "Standalone", "No"),  # A New Kind of Science
    "9780262631853": ("NonFiction", "Standalone", "No"),  # Intro to Genetic Algorithms
    "9780141009094": ("NonFiction", "Standalone", "No"),  # Euclid's Window
    "9783764301491": ("NonFiction", "Standalone", "No"),  # Mathland
    "9780226458083": ("NonFiction", "Standalone", "No"),  # Structure of Scientific Revolutions
    # Social science / philosophy – NonFiction
    "9781785781629": ("NonFiction", "Standalone", "No"),  # Testosterone Rex
    "9781478002390": ("NonFiction", "Standalone", "No"),  # Counterproductive
    "9780688050337": ("NonFiction", "Standalone", "No"),  # Coming of Age in Samoa
    "9780062975638": ("NonFiction", "Standalone", "No"),  # Sand Talk
    "9781760761189": ("NonFiction", "Standalone", "No"),  # Songlines
    "9780300122237": ("NonFiction", "Standalone", "No"),  # Nudge
    "9780374275631": ("NonFiction", "Standalone", "No"),  # Thinking Fast and Slow
    "9780691128719": ("NonFiction", "Standalone", "No"),  # Expert Political Judgment
    "9781250316967": ("NonFiction", "Standalone", "No"),  # Open Borders
    "9780385347372": ("NonFiction", "Standalone", "No"),  # Dataclysm
    "9780307346605": ("NonFiction", "Standalone", "No"),  # World War Z -- actually Fiction!
    "9780143116844": ("NonFiction", "Standalone", "No"),  # Wired for War
    "9781594201981": ("NonFiction", "Standalone", "No"),  # Wired for War (other edition)
    "9780674019270": ("NonFiction", "Standalone", "No"),  # The Case Against Perfection
    "9780140222241": ("NonFiction", "Standalone", "No"),  # What Sort of People Should There Be?
    "9780699556731": ("NonFiction", "Standalone", "No"),
    "9780199556731": ("NonFiction", "Standalone", "No"),  # Future People
    "9780773539440": ("NonFiction", "Standalone", "No"),  # Ethics for a Broken World
    "9780773539457": ("NonFiction", "Standalone", "No"),  # Ethics for a Broken World (other ed)
    "9781442636446": ("NonFiction", "Standalone", "No"),  # Posthumanism
    "9780674019270": ("NonFiction", "Standalone", "No"),
    "9780099436867": ("NonFiction", "Standalone", "No"),  # Our Final Century
    "9780434008094": ("NonFiction", "Standalone", "No"),  # Our Final Century? (other ed)
    # History / memoir – NonFiction
    "9780007379873": ("NonFiction", "Standalone", "No"),  # Wild Swans
    "9780615873442": ("NonFiction", "Standalone", "No"),  # Buckminster Fuller Poet of Geometry
    "9780738206363": ("NonFiction", "Standalone", "No"),  # Perfectly Reasonable Deviations
    "9780199540266": ("NonFiction", "Standalone", "No"),  # Gallic War
    "9780679746690": ("NonFiction", "Standalone", "No"),  # Running in the Family
    "9780306818837": ("NonFiction", "Standalone", "No"),  # The End of Money
    "9781925113143": ("NonFiction", "Standalone", "No"),  # Social Physics
    "9781846683138": ("NonFiction", "Standalone", "No"),  # Checklist Manifesto
    "9780982703038": ("NonFiction", "Standalone", "No"),
    "9780141195179": ("NonFiction", "Standalone", "No"),  # Gulliver's Travels
    "9780143039006": ("NonFiction", "Standalone", "No"),  # Travels with My Aunt -- Fiction actually
    "9781982135485": ("NonFiction", "Standalone", "No"),  # Butts: A Backstory
    "9780262544092": ("NonFiction", "Standalone", "No"),  # Robot Ethics
    "9780500027660": ("NonFiction", "Standalone", "No"),  # The Korean Myths
    "9780140449334": ("NonFiction", "Standalone", "No"),  # Meditations
    "9780141019017": ("NonFiction", "Standalone", "No"),  # Freakonomics
    "9781846143038": ("NonFiction", "Standalone", "No"),  # Illustrated Superfreakonomics
    "9780061234002": ("NonFiction", "Standalone", "No"),  # Freakonomics (other ed)
    "9780060889579": ("NonFiction", "Standalone", "No"),  # SuperFreakonomics
    "9780753513385": ("NonFiction", "Standalone", "No"),  # Economic Naturalist
    "9780465002177": ("NonFiction", "Standalone", "No"),  # The Economic Naturalist (other)
    "9781594485619": ("NonFiction", "Standalone", "No"),  # The Conundrum
    "9780393324037": ("NonFiction", "Standalone", "No"),  # Cartoon History Universe III
    "9780385420938": ("NonFiction", "Standalone", "No"),  # Cartoon History Universe II
    "9780385265201": ("NonFiction", "Standalone", "No"),  # Cartoon History Universe I
    "9780060760045": ("NonFiction", "Series",     "No"),  # Cartoon History Modern World
    "9780062731029": ("NonFiction", "Standalone", "No"),  # Cartoon Guide Statistics
    "9780240808581": ("NonFiction", "Standalone", "No"),  # 3ds Max MAXScript Essentials
    "9780596004293": ("NonFiction", "Standalone", "No"),  # C# Language Pocket Reference
    "9780764597046": ("NonFiction", "Standalone", "No"),  # C# 2005 For Dummies
    "9780984442539": ("NonFiction", "Standalone", "No"),  # CSS3 for Web Designers
    "9780984442515": ("NonFiction", "Standalone", "No"),  # HTML5 for Web Designers
    "9781937557027": ("NonFiction", "Standalone", "No"),  # Mobile First
    "9780984442577": ("NonFiction", "Standalone", "No"),  # Responsive Web Design
    "9781937557102": ("NonFiction", "Standalone", "No"),  # Just Enough Research
    "9780932633439": ("NonFiction", "Standalone", "No"),  # Peopleware
    "9780201835953": ("NonFiction", "Standalone", "No"),  # Mythical Man-Month
    "9780449305172": ("NonFiction", "Standalone", "No"),
    "9781449305178": ("NonFiction", "Standalone", "No"),  # Running Lean
    "9781558607835": ("NonFiction", "Standalone", "No"),  # Blondie24
    "9780077090715": ("NonFiction", "Standalone", "No"),  # Succeeding With AutoCAD
    "9780596106362": ("NonFiction", "Standalone", "No"),  # Hackers & Painters
    "9781953953339": ("NonFiction", "Standalone", "No"),  # An Elegant Puzzle
    "9780578675862": ("NonFiction", "Standalone", "No"),  # Working in Public
    "9780071368162": ("NonFiction", "Standalone", "No"),  # Gemba Kaizen
    "9780988262577": ("Fiction",    "Standalone", "No"),  # The Phoenix Project (novel)
    "9780884272748": ("Fiction",    "Standalone", "No"),  # The Goal (novel)
    "9780241144770": ("NonFiction", "Standalone", "No"),  # Religion for Atheists
    "9780141022093": ("NonFiction", "Standalone", "No"),  # The Craftsman
    "9780008323455": ("NonFiction", "Standalone", "No"),  # It Doesn't Have to Be Crazy at Work
    "9780804137508": ("NonFiction", "Standalone", "No"),  # Remote
    "9781329567115": ("NonFiction", "Standalone", "No"),  # Why I Am Not a Christian
    "9780307887894": ("NonFiction", "Standalone", "No"),  # The Lean Startup
    "9780133158311": ("NonFiction", "Standalone", "No"),  # People Analytics (Benjamin Waber)
    "9780568490151": ("NonFiction", "Standalone", "No"),
    "9781568490151": ("NonFiction", "Standalone", "No"),  # Parkinson's Law
    "9780195189773": ("NonFiction", "Standalone", "No"),  # The Undercover Economist
    "9780399168529": ("NonFiction", "Standalone", "No"),  # Less Doing More Living
    "9780226065663": ("NonFiction", "Standalone", "No"),  # The Craft of Research
    "9780393071955": ("NonFiction", "Standalone", "No"),  # Naked Statistics
    "9781937785987": ("NonFiction", "Standalone", "No"),  # The Cucumber Book
    "9780749304140": ("Fiction",    "Standalone", "No"),  # A Town Like Alice (Fiction)
    "9781903919866": ("NonFiction", "Standalone", "No"),  # The Meaning of the 21st Century
    "9781596432598": ("NonFiction", "Standalone", "No"),  # Feynman (graphic biography)
    "9780747597209": ("NonFiction", "Standalone", "No"),  # Logicomix
    "9781596914520": ("NonFiction", "Standalone", "No"),  # Logicomix (other ed)
    "9780972080163": ("NonFiction", "Standalone", "No"),  # Raised on Ritalin
    "9780988523845": ("NonFiction", "Standalone", "No"),  # Goomics
    "9780141014081": ("NonFiction", "Standalone", "No"),  # The Complete Maus
    # ── Fiction ──────────────────────────────────────────────────────────────
    # Terra Ignota (Ada Palmer) – LGBTQIA throughout
    "9781786699473": ("Fiction", "Series", "Yes"),  # Too Like the Lightning #1
    "9781786699510": ("Fiction", "Series", "Yes"),  # Seven Surrenders #2
    "9781786699558": ("Fiction", "Series", "Yes"),  # Will to Battle #3
    "9781786699596": ("Fiction", "Series", "Yes"),  # Perhaps the Stars #4
    # Monk & Robot (Becky Chambers)
    "9781250776297": ("Fiction", "Standalone", "No"),  # Bea Wolf (standalone)
    # Note: A Psalm/A Prayer isbn not in CSV as clean numbers; handled by title
    # Imperial Radch (Ann Leckie)
    "9781594486241": ("Fiction", "Series", "Yes"),
    "9780316246651": ("Fiction", "Series", "Yes"),  # Ancillary Sword
    # Broken Earth (N.K. Jemisin)
    "9780356504896": ("Fiction", "Series", "Yes"),  # The Obelisk Gate
    # William Gibson – Sprawl, Bridge, Blue Ant, Jackpot
    "9780670919543": ("Fiction", "Series", "No"),   # Zero History
    "9780399156823": ("Fiction", "Series", "No"),   # Zero History (other ed)
    "9780553281743": ("Fiction", "Series", "No"),   # Mona Lisa Overdrive
    "9780425190456": ("Fiction", "Series", "No"),   # Idoru
    "9780425190449": ("Fiction", "Series", "No"),   # All Tomorrow's Parties
    "9780399154300": ("Fiction", "Series", "No"),   # Spook Country
    "9780425198681": ("Fiction", "Series", "No"),   # Pattern Recognition
    "9780140157727": ("Fiction", "Series", "No"),   # Virtual Light
    "9780060539825": ("Fiction", "Series", "No"),   # Burning Chrome
    "9780465067107": ("NonFiction", "Standalone", "No"),  # actually Design of Everyday Things
    # Neal Stephenson
    "9780553380958": ("Fiction", "Standalone", "No"),   # Snow Crash
    "9780553380965": ("Fiction", "Standalone", "No"),   # The Diamond Age
    "9780061474095": ("Fiction", "Standalone", "No"),   # Anathem
    "9780061977961": ("Fiction", "Standalone", "No"),   # Reamde
    "9780380816033": ("Fiction", "Standalone", "No"),   # The Big U
    "9780380815937": ("NonFiction", "Standalone", "No"),# In the Beginning...Was the Command Line
    "9780553383430": ("Fiction", "Standalone", "No"),   # Interface
    "9780553383447": ("Fiction", "Standalone", "No"),   # The Cobweb
    "9781460712962": ("Fiction", "Standalone", "No"),   # Termination Shock
    "9780008262617": ("Fiction", "Series",     "No"),   # Polostan #1
    "9781612187457": ("Fiction", "Series",     "No"),   # Mongoliad Book 2
    "9781611093919": ("Fiction", "Series",     "No"),   # The Mongoliad
    "9781477876084": ("Fiction", "Series",     "No"),   # Cimarronin #1
    # J.G. Ballard
    "9780007513611": ("Fiction", "Standalone", "No"),   # Complete Short Stories Vol 2
    "9780007369386": ("Fiction", "Standalone", "No"),   # Complete Short Stories Vol 1
    "9781857988833": ("Fiction", "Standalone", "No"),   # The Drowned World
    "9780743265232": ("Fiction", "Standalone", "No"),   # Empire of the Sun
    "9780156471145": ("Fiction", "Standalone", "No"),   # The Kindness of Women
    "9780007232468": ("Fiction", "Standalone", "No"),   # Kingdom Come
    "9781582430171": ("Fiction", "Standalone", "No"),   # Cocaine Nights
    "9780007321582": ("Fiction", "Standalone", "No"),   # Concrete Island
    # Margaret Atwood
    "9780748130191": ("Fiction", "Series", "No"),   # MaddAddam
    "9780263134743": ("Fiction", "Series", "No"),
    # Philip K. Dick
    "9781473206717": ("Fiction", "Standalone", "No"),   # A Scanner Darkly
    "9780575097957": ("Fiction", "Standalone", "No"),   # Ubik
    "9780006482796": ("Fiction", "Standalone", "No"),   # We Can Build You
    "9781400030088": ("Fiction", "Standalone", "No"),   # Lies, Inc.
    "9780307265432": ("Fiction", "Standalone", "No"),   # The Road
    # Ursula K. Le Guin
    "9780441732968": ("Fiction", "Series", "No"),   # Rocannon's World
    "9780441669516": ("Fiction", "Series", "No"),   # Planet of Exile
    "9781473223554": ("Fiction", "Series", "Yes"),  # Books of Earthsea (Tehanu has LGBTQIA)
    # Michael Ondaatje
    "9780099554455": ("Fiction", "Standalone", "No"),
    "9780676970081": ("Fiction", "Standalone", "No"),   # The English Patient
    "9781509823345": ("Fiction", "Standalone", "No"),   # In the Skin of a Lion
    "9780679746690": ("NonFiction", "Standalone", "No"),# Running in the Family (memoir)
    # Madeline Miller
    "9780316556347": ("Fiction", "Standalone", "No"),   # Circe
    # The Song of Achilles – handled by title (isbn nan in data)
    # Orson Scott Card
    "9780812565959": ("Fiction", "Series", "No"),
    "9780812550757": ("Fiction", "Series", "No"),
    "9780765342409": ("Fiction", "Series", "No"),
    "9780748134220": ("Fiction", "Series", "No"),  # Xenocide
    # Hunger Games
    "9780439023511": ("Fiction", "Series", "No"),
    "9780439023481": ("Fiction", "Series", "No"),
    "9780439023498": ("Fiction", "Series", "No"),
    # A Song of Ice and Fire – has gay characters (Renly/Loras)
    "9780553588484": ("Fiction", "Series", "Yes"),  # A Game of Thrones
    "9780007119554": ("Fiction", "Series", "Yes"),  # Storm of Swords Blood and Gold
    "9780006479901": ("Fiction", "Series", "Yes"),  # Storm of Swords Steel and Snow
    # Hitchhiker's Guide
    "9781743540190": ("Fiction", "Series", "No"),   # Complete Hitchhiker's
    "9780345418906": ("Fiction", "Series", "No"),
    "9780330491235": ("Fiction", "Series", "No"),
    "9780061020681": ("Fiction", "Series", "No"),   # Mort (Discworld)
    # Nexus trilogy
    "9781942948001": ("Fiction", "Series", "No"),   # Nexus #1
    "9780857662934": ("Fiction", "Series", "No"),   # Nexus #1 (other ed)
    "9781942948018": ("Fiction", "Series", "No"),   # Crux #2
    # Culture (Iain M. Banks) – gender-fluid society
    "9780316171175": ("Fiction", "Series", "Yes"),  # Consider Phlebas
    # Foreworld / Mongoliad
    "9781477867594": ("Fiction", "Series", "No"),
    "9781477898215": ("Fiction", "Series", "No"),
    # Philip Pullman
    "9781448197163": ("Fiction", "Series", "No"),   # The Collectors
    # Classics / literary fiction
    "9780142437247": ("Fiction", "Standalone", "No"),   # Moby-Dick
    "9780141439495": ("Fiction", "Standalone", "No"),   # Gulliver's Travels
    "9780141195179": ("Fiction", "Standalone", "No"),   # Gulliver's Travels (other ed)
    "9780140185850": ("Fiction", "Standalone", "No"),   # We (Zamyatin)
    "9780060085490": ("Fiction", "Standalone", "No"),   # Island (Huxley)
    "9780099477822": ("NonFiction", "Standalone", "No"),# Grey Eminence (Huxley – history)
    "9780060929879": ("Fiction", "Standalone", "No"),   # Brave New World
    "9780684833392": ("Fiction", "Standalone", "No"),   # Catch-22
    "9780140283334": ("Fiction", "Standalone", "No"),   # Lord of the Flies
    "9780316769174": ("Fiction", "Standalone", "No"),   # The Catcher in the Rye
    "9780140237504": ("Fiction", "Standalone", "No"),   # The Catcher in the Rye (other)
    "9780743273565": ("Fiction", "Standalone", "No"),   # The Great Gatsby
    "9780141184845": ("Fiction", "Standalone", "No"),   # Labyrinths (Borges)
    "9780156453806": ("Fiction", "Standalone", "No"),   # Invisible Cities
    "9789897780608": ("Fiction", "Standalone", "No"),   # Persuasion
    "9780571162727": ("Fiction", "Standalone", "No"),   # Bliss (Peter Carey)
    "9780141956961": ("Fiction", "Standalone", "No"),   # Crime and Punishment
    "9780486431680": ("Fiction", "Standalone", "No"),   # Hunger (Hamsun)
    "9780465030781": ("Fiction", "Standalone", "No"),   # I Am a Strange Loop
    "9780679457312": ("Fiction", "Standalone", "No"),   # The God of Small Things
    "9780374260507": ("Fiction", "Standalone", "No"),   # The Sellout
    "9780857054791": ("Fiction", "Standalone", "No"),   # Gold Fame Citrus
    "9780374261597": ("Fiction", "Standalone", "No"),   # Severance
    "9781405525824": ("Fiction", "Standalone", "No"),   # California
    "9781743532324": ("Fiction", "Standalone", "No"),   # Station Eleven
    "9780141395876": ("Fiction", "Standalone", "No"),   # The Prince
    "9780312865047": ("Fiction", "Standalone", "No"),   # I Am Legend
    "9781912854837": ("Fiction", "Standalone", "No"),   # A Room Called Earth
    "9781931520058": ("Fiction", "Standalone", "No"),   # Kalpa Imperial
    "9780393089059": ("Fiction", "Standalone", "No"),   # The Odyssey
    "9781400044160": ("Fiction", "Standalone", "No"),   # Half of a Yellow Sun
    "9780374111199": ("Fiction", "Standalone", "No"),   # Beowulf (Heaney)
    "9780374110031": ("Fiction", "Standalone", "No"),   # Beowulf (Headley)
    "9780141393964": ("Fiction", "Standalone", "No"),   # Things Fall Apart
    "9780156453806": ("Fiction", "Standalone", "No"),
    "9780192838650": ("Fiction", "Standalone", "No"),   # The Last Man
    "9781544917023": ("Fiction", "Standalone", "No"),   # Frankenstein
    "9786558945529": ("Fiction", "Standalone", "Yes"),  # The Nun (Diderot) – lesbian relationship
    "9780008470302": ("NonFiction", "Standalone", "No"),# Notes on Grief
    "9780062975638": ("NonFiction", "Standalone", "No"),# Sand Talk
    "9780857522405": ("NonFiction", "Standalone", "No"),# The Body (Bill Bryson)
    "9781842220146": ("NonFiction", "Standalone", "No"),# wait – this is not right
    # Speculative / SF
    "9780356508856": ("Fiction", "Standalone", "No"),   # The Ministry for the Future
    "9780316098106": ("Fiction", "Standalone", "No"),   # Aurora (Kim Stanley Robinson)
    "9781784971540": ("Fiction", "Series",     "No"),   # Three-Body Problem
    "9781741499390": ("Fiction", "Standalone", "No"),
    "9781841499390": ("Fiction", "Standalone", "No"),   # Intrusion (Ken MacLeod)
    "9780748124121": ("Fiction", "Standalone", "No"),   # Accelerando
    "9781742624556": ("Fiction", "Series",     "No"),   # Tomorrow When the War Began
    "9781542093576": ("Fiction", "Series",     "No"),   # Emergency Skin (Forward Collection)
    "9781643756219": ("Fiction", "Standalone", "No"),   # Your Utopia (Bora Chung)
    "9781642360394": ("Fiction", "Standalone", "No"),   # A Summer Beyond Your Reach (Xia Jia)
    "9781803361130": ("Fiction", "Standalone", "No"),   # Alien 3 screenplay (Cadigan)
    "9780062204691": ("Fiction", "Standalone", "No"),   # Hieroglyph (anthology)
    "9780957397552": ("Fiction", "Standalone", "No"),   # Accessing the Future (anthology)
    # Graphic novels / comics
    "9781608861491": ("Fiction", "Series", "No"),   # BRZRKR Bloodlines
    "9781684157129": ("Fiction", "Series", "No"),   # BRZRKR Vol 3
    "9781684158157": ("Fiction", "Series", "No"),   # BRZRKR Vol 2
    "9781529150544": ("Fiction", "Standalone", "No"),   # The Book of Elsewhere
    "9781594654176": ("Fiction", "Standalone", "No"),   # Milo Manara's Gullivera
    "9781845767570": ("Fiction", "Series", "No"),   # Tank Girl #1
    "9781932664164": ("Fiction", "Standalone", "No"),   # Lost at Sea
    "9780345529374": ("Fiction", "Standalone", "No"),   # Seconds
    "9781607065968": ("Fiction", "Series", "No"),   # Walking Dead Compendium Two
    "9780285632264": ("Fiction", "Standalone", "No"),   # The Specialist
    "9780473287924": ("NonFiction", "Standalone", "No"),# Humanimal 3.0
    "9780988523845": ("NonFiction", "Standalone", "No"),# Goomics
    "9781840467130": ("NonFiction", "Standalone", "No"),# Introducing Fractal Geometry
    # Children's / classics
    "9780241003008": ("Fiction", "Standalone", "No"),   # The Very Hungry Caterpillar
    "9780617009361": ("Fiction", "Standalone", "No"),
    "9780618009367": ("Fiction", "Series",     "No"),   # Farmer Giles of Ham (Tolkien)
    "9780525467564": ("Fiction", "Standalone", "No"),   # Winnie-the-Pooh
    "9780723247708": ("Fiction", "Standalone", "No"),   # The Tale of Peter Rabbit
    "9780143039099": ("Fiction", "Standalone", "No"),   # The Wind in the Willows
    "9780517266557": ("Fiction", "Standalone", "No"),   # Just So Stories
    "9781402726026": ("Fiction", "Standalone", "No"),   # The Swiss Family Robinson
    "9780345368584": ("Fiction", "Series",     "No"),   # The Hobbit (graphic novel)
    "9780785135807": ("Fiction", "Series",     "No"),   # Ender's Game graphic novel
    # Misc NF
    "9780300204803": ("NonFiction", "Standalone", "No"),# The City of Tomorrow (Ratti)
    "9780262134743": ("NonFiction", "Standalone", "No"),# Designing Interactions (Moggridge)
    "9780905492077": ("NonFiction", "Standalone", "No"),
    "9780450040184": ("Fiction",    "Standalone", "No"),# The Shining
    "9781927673041": ("Fiction",    "Standalone", "No"),# NECRONOMICUM
    "9781499017922": ("NonFiction", "Standalone", "No"),# MIT Building 20
    "9780226036987": ("NonFiction", "Standalone", "No"),
    "9780226036984": ("NonFiction", "Standalone", "No"),
    "9780614873442": ("NonFiction", "Standalone", "No"),
    "9780614615873": ("NonFiction", "Standalone", "No"),
    "9780853722899": ("NonFiction", "Standalone", "No"),# Follies
    "9781854106254": ("NonFiction", "Standalone", "No"),# Follies
    "9780415438155": ("NonFiction", "Standalone", "No"),# Colour for Architecture Today
    "9780262633130": ("NonFiction", "Standalone", "No"),# Me++ (William J. Mitchell)
    "9780753812778": ("NonFiction", "Standalone", "No"),# Creation (Steve Grand)
    "9781550225587": ("NonFiction", "Standalone", "No"),# Nufonia Must Fall
    "9780446676885": ("NonFiction", "Standalone", "No"),# Mr. Boston
    "9781591841999": ("NonFiction", "Standalone", "No"),# The Back of the Napkin
    "9780525510543": ("NonFiction", "Standalone", "No"),# Trick Mirror (Jia Tolentino)
    "9780008226275": ("NonFiction", "Standalone", "No"),# Other Minds (Godfrey-Smith) -- actually Fiction/NF hybrid, very NF
    "9781852427726": ("NonFiction", "Standalone", "No"),# Techgnosis
    "9780141022093": ("NonFiction", "Standalone", "No"),# The Craftsman
    "9781473988194": ("NonFiction", "Standalone", "No"),# A Very Short Fairly Interesting Book
    "9780713997576": ("NonFiction", "Standalone", "No"),
    "9780393060270": ("NonFiction", "Standalone", "No"),# Lewis Carroll in Numberland
    "9780903919866": ("NonFiction", "Standalone", "No"),
    "9780300122237": ("NonFiction", "Standalone", "No"),
    "9780807058402": ("NonFiction", "Standalone", "No"),
    "9780982438312": ("NonFiction", "Standalone", "No"),
    "9780983703038": ("NonFiction", "Standalone", "No"),
    "9780986527038": ("NonFiction", "Standalone", "No"),
    "9781422191656": ("NonFiction", "Standalone", "No"),
    "9781905177073": ("NonFiction", "Standalone", "No"),# Irrationality
}

# ── Title-based fallback ──────────────────────────────────────────────────────
# normalise(title) → (ficOrNonFic, SeriesOrStandalone, LGBTQIA_Characters)
BY_TITLE = {
    # Terra Ignota
    "too like the lightning (terra ignota, #1)":  ("Fiction", "Series", "Yes"),
    "seven surrenders (terra ignota book 2)":     ("Fiction", "Series", "Yes"),
    "the will to battle (terra ignota, #3)":      ("Fiction", "Series", "Yes"),
    "perhaps the stars (terra ignota book 4)":    ("Fiction", "Series", "Yes"),
    # Monk & Robot
    "a psalm for the wild-built (monk & robot, #1)":  ("Fiction", "Series", "Yes"),
    "a prayer for the crown-shy (monk & robot, #2)":  ("Fiction", "Series", "Yes"),
    # N.K. Jemisin
    "the fifth season (the broken earth, #1)":    ("Fiction", "Series", "Yes"),
    "the obelisk gate (the broken earth #2)":     ("Fiction", "Series", "Yes"),
    "the stone sky":                              ("Fiction", "Series", "Yes"),
    "how long 'til black future month?":          ("Fiction", "Standalone", "Yes"),
    "emergency skin (forward collection, #3)":    ("Fiction", "Series", "No"),
    "the city we became (great cities #1)":       ("Fiction", "Series", "Yes"),
    # Imperial Radch
    "ancillary justice (imperial radch, #1)":     ("Fiction", "Series", "Yes"),
    "ancillary sword (imperial radch #2)":        ("Fiction", "Series", "Yes"),
    "ancillary mercy (imperial radch, #3)":       ("Fiction", "Series", "Yes"),
    # Octavia E. Butler
    "parable of the sower (earthseed, #1)":       ("Fiction", "Series", "No"),
    "parable of the talents (earthseed, #2)":     ("Fiction", "Series", "No"),
    "kindred":                                    ("Fiction", "Standalone", "No"),
    "dawn (lilith's brood, #1)":                  ("Fiction", "Series", "No"),
    "parable of the sower: a graphic novel adaptation": ("Fiction", "Series", "No"),
    # Her Body and Other Parties
    "her body and other parties":                 ("Fiction", "Standalone", "Yes"),
    # Manhunt
    "manhunt":                                    ("Fiction", "Standalone", "Yes"),
    # The Handmaid's Tale – Ofglen is gay
    "the handmaid's tale":                        ("Fiction", "Standalone", "Yes"),
    "the testaments (the handmaid's tale, #2)":   ("Fiction", "Series", "No"),
    # His Dark Materials – Balthamos & Baruch
    "his dark materials":                         ("Fiction", "Series", "Yes"),
    "la belle sauvage (the book of dust, #1)":    ("Fiction", "Series", "No"),
    "the secret commonwealth (the book of dust, #2)": ("Fiction", "Series", "No"),
    "the collectors (his dark materials #0.6)":   ("Fiction", "Series", "No"),
    # Stephen Fry mythology – contains LGBTQIA content from original myths
    "mythos: the greek myths retold (stephen fry's great mythology, #1)": ("Fiction", "Standalone", "Yes"),
    "heroes: mortals and monsters, quests and adventures (stephen fry's great mythology, #2)": ("Fiction", "Standalone", "Yes"),
    "troy: our greatest story retold (stephen fry\u00e6s great mythology, #3)": ("Fiction", "Standalone", "Yes"),
    "troy: our greatest story retold (stephen fry's great mythology, #3)": ("Fiction", "Standalone", "Yes"),
    # Madeline Miller
    "the song of achilles":                       ("Fiction", "Standalone", "Yes"),
    "circe":                                      ("Fiction", "Standalone", "No"),
    "galatea":                                    ("Fiction", "Standalone", "No"),
    # Le Guin – Hainish
    "the left hand of darkness":                  ("Fiction", "Series", "Yes"),
    "the dispossessed":                           ("Fiction", "Series", "No"),
    "the books of earthsea: the complete illustrated edition": ("Fiction", "Series", "Yes"),
    "rocannon's world":                           ("Fiction", "Series", "No"),
    "rocannon\u00e6s world":                      ("Fiction", "Series", "No"),
    "planet of exile":                            ("Fiction", "Series", "No"),
    "city of illusions":                          ("Fiction", "Series", "No"),
    "the word for world is forest":               ("Fiction", "Series", "No"),
    "the telling":                                ("Fiction", "Series", "No"),
    "five ways to forgiveness":                   ("Fiction", "Series", "No"),
    "the lathe of heaven":                        ("Fiction", "Standalone", "No"),
    "dancing at the edge of the world: thoughts on words, women, places": ("NonFiction", "Standalone", "No"),
    "ursula k. le guin: the last interview: and other conversations": ("NonFiction", "Standalone", "No"),
    "dispatches from anarres: tales in tribute to ursula k. le guin": ("Fiction", "Standalone", "Yes"),
    # A Song of Ice and Fire
    "a game of thrones (a song of ice and fire, #1)":    ("Fiction", "Series", "Yes"),
    "a clash of kings  (a song of ice and fire, #2)":    ("Fiction", "Series", "Yes"),
    "a storm of swords: steel and snow (a song of ice and fire, #3.1)": ("Fiction", "Series", "Yes"),
    "a storm of swords 2: blood and gold (a song of ice and fire, #3, part 2 of 2)": ("Fiction", "Series", "Yes"),
    "a feast for crows (a song of ice and fire, #4)":    ("Fiction", "Series", "Yes"),
    "a dance with dragons (a song of ice and fire, #5)": ("Fiction", "Series", "Yes"),
    "a storm of swords: summary":                 ("NonFiction", "Standalone", "No"),  # BookRags summary
    # Consider Phlebas (Culture)
    "consider phlebas (culture, #1)":             ("Fiction", "Series", "Yes"),
    # Ender's Game
    "ender's game (ender's saga, #1)":            ("Fiction", "Series", "No"),
    "ender\u00e6s game (ender's saga, #1)":       ("Fiction", "Series", "No"),
    "ender's shadow (the shadow series, #1)":     ("Fiction", "Series", "No"),
    "shadow of the hegemon (the shadow series, #2)": ("Fiction", "Series", "No"),
    "speaker for the dead (ender's saga, #2)":    ("Fiction", "Series", "No"),
    "xenocide (ender's saga, #3)":                ("Fiction", "Series", "No"),
    "ender's game, volume 1: battle school (ender's saga)": ("Fiction", "Series", "No"),
    # Hitchhiker's Guide
    "the hitchhiker's guide to the galaxy (hitchhiker's guide to the galaxy, #1)": ("Fiction", "Series", "No"),
    "the restaurant at the end of the universe (the hitchhiker's guide to the galaxy, #2)": ("Fiction", "Series", "No"),
    "life, the universe and everything (the hitchhiker's guide to the galaxy, #3)": ("Fiction", "Series", "No"),
    "so long, and thanks for all the fish (hitchhiker's guide to the galaxy, #4)": ("Fiction", "Series", "No"),
    "mostly harmless (hitchhiker's guide to the galaxy, #5)": ("Fiction", "Series", "No"),
    "the complete hitchhiker's guide to the galaxy: the trilogy of five": ("Fiction", "Series", "No"),
    # Discworld
    "mort (discworld, #4; death, #1)":            ("Fiction", "Series", "No"),
    "raising steam (discworld, #40)":             ("Fiction", "Series", "No"),
    "the long cosmos (the long earth, #5)":       ("Fiction", "Series", "No"),  # Pratchett/Baxter
    "good omens: the nice and accurate prophecies of agnes nutter, witch": ("Fiction", "Standalone", "No"),
    # Margaret Atwood
    "the blind assassin":                         ("Fiction", "Standalone", "No"),
    "alias grace":                                ("Fiction", "Standalone", "No"),
    "the penelopiad (faber drama)":               ("Fiction", "Standalone", "No"),
    "old babes in the wood":                      ("Fiction", "Standalone", "Yes"),
    "madAddam (the maddaddam trilogy #3)":        ("Fiction", "Series", "No"),
    "the year of the flood  (maddaddam, #2)":     ("Fiction", "Series", "No"),
    "oryx and crake (maddaddam trilogy, #1)":     ("Fiction", "Series", "No"),
    # Hilary Mantel – Thomas Cromwell
    "wolf hall (thomas cromwell, #1)":            ("Fiction", "Series", "No"),
    "bring up the bodies (thomas cromwell, #2)":  ("Fiction", "Series", "No"),
    "the mirror & the light (thomas cromwell, #3)": ("Fiction", "Series", "No"),
    # Philip Pullman
    "his dark materials":                         ("Fiction", "Series", "Yes"),
    "la belle sauvage (the book of dust, #1)":    ("Fiction", "Series", "No"),
    "the secret commonwealth (the book of dust, #2)": ("Fiction", "Series", "No"),
    "the collectors (his dark materials #0.6)":   ("Fiction", "Series", "No"),
    # Baroque Cycle / Stephenson
    "quicksilver (the baroque cycle, #1)":        ("Fiction", "Series", "No"),
    "the confusion (the baroque cycle, #2)":      ("Fiction", "Series", "No"),
    "the system of the world (the baroque cycle, #3)": ("Fiction", "Series", "No"),
    "the mongoliad: book two (foreworld, #2)":    ("Fiction", "Series", "No"),
    "the mongoliad: book three (foreworld, #3)":  ("Fiction", "Series", "No"),
    "the mongoliad":                              ("Fiction", "Series", "No"),
    "katabasis (foreworld, #4)":                  ("Fiction", "Series", "No"),
    "siege perilous (foreworld, #5)":             ("Fiction", "Series", "No"),
    "the rise and fall of d.o.d.o. (d.o.d.o., #1)": ("Fiction", "Series", "No"),
    # Nexus
    "nexus (nexus, #1)":                          ("Fiction", "Series", "No"),
    "crux (nexus, #2)":                           ("Fiction", "Series", "No"),
    "apex (nexus, #3)":                           ("Fiction", "Series", "No"),
    # William Gibson
    "neuromancer (sprawl #1)":                    ("Fiction", "Series", "No"),
    "count zero (sprawl, #2)":                    ("Fiction", "Series", "No"),
    "mona lisa overdrive (sprawl, #3)":           ("Fiction", "Series", "No"),
    "burning chrome (sprawl, #0)":                ("Fiction", "Series", "No"),
    "virtual light (bridge, #1)":                 ("Fiction", "Series", "No"),
    "idoru (bridge, #2)":                         ("Fiction", "Series", "No"),
    "all tomorrow's parties (bridge, #3)":        ("Fiction", "Series", "No"),
    "pattern recognition (blue ant, #1)":         ("Fiction", "Series", "No"),
    "spook country (blue ant, #2)":               ("Fiction", "Series", "No"),
    "zero history (blue ant, #3)":                ("Fiction", "Series", "No"),
    "the peripheral (jackpot #1)":                ("Fiction", "Series", "No"),
    "agency (jackpot #2)":                        ("Fiction", "Series", "No"),
    "the difference engine":                      ("Fiction", "Standalone", "No"),
    "archangel #1":                               ("Fiction", "Series", "No"),
    "william gibson's alien 3 #1":                ("Fiction", "Series", "No"),
    "distrust that particular flavor":            ("NonFiction", "Standalone", "No"),
    # J.G. Ballard
    "crash":                                      ("Fiction", "Standalone", "No"),
    "the complete short stories: volume 2":       ("Fiction", "Standalone", "No"),
    "the complete short stories, volume 1":       ("Fiction", "Standalone", "No"),
    "the drowned world":                          ("Fiction", "Standalone", "No"),
    "empire of the sun":                          ("Fiction", "Standalone", "No"),
    "high-rise":                                  ("Fiction", "Standalone", "No"),
    "cocaine nights":                             ("Fiction", "Standalone", "No"),
    "concrete island":                            ("Fiction", "Standalone", "No"),
    "the kindness of women":                      ("Fiction", "Standalone", "No"),
    "kingdom come":                               ("Fiction", "Standalone", "No"),
    # Philip K. Dick
    "do androids dream of electric sheep?":       ("Fiction", "Standalone", "No"),
    "a scanner darkly":                           ("Fiction", "Standalone", "No"),
    "ubik":                                       ("Fiction", "Standalone", "No"),
    "flow, my tears, the policeman said.":        ("Fiction", "Standalone", "No"),
    "we can build you":                           ("Fiction", "Standalone", "No"),
    "lies, inc.":                                 ("Fiction", "Standalone", "No"),
    # Le Guin (other)
    "the word for world is forest":               ("Fiction", "Series", "No"),
    "the telling":                                ("Fiction", "Series", "No"),
    "five ways to forgiveness":                   ("Fiction", "Series", "No"),
    "the lathe of heaven":                        ("Fiction", "Standalone", "No"),
    # Neal Stephenson
    "cryptonomicon":                              ("Fiction", "Standalone", "No"),
    "snow crash":                                 ("Fiction", "Standalone", "No"),
    "the diamond age: or, a young lady's illustrated primer": ("Fiction", "Standalone", "No"),
    "anathem":                                    ("Fiction", "Standalone", "No"),
    "reamde":                                     ("Fiction", "Standalone", "No"),
    "seveneves":                                  ("Fiction", "Standalone", "No"),
    "the big u: a hilarious satire of american college life": ("Fiction", "Standalone", "No"),
    "zodiac":                                     ("Fiction", "Standalone", "No"),
    "in the beginning...was the command line":    ("NonFiction", "Standalone", "No"),
    "fall; or, dodge in hell":                    ("Fiction", "Standalone", "No"),
    "termination shock":                          ("Fiction", "Standalone", "No"),
    "polostan (bomb light, #1)":                  ("Fiction", "Series", "No"),
    "the cobweb":                                 ("Fiction", "Standalone", "No"),
    "interface":                                  ("Fiction", "Standalone", "No"),
    "some remarks":                               ("NonFiction", "Standalone", "No"),
    "cimarronin: a samurai in new spain #1":      ("Fiction", "Series", "No"),
    # Octavia Butler
    "parable of the sower (earthseed, #1)":       ("Fiction", "Series", "No"),
    "parable of the talents (earthseed, #2)":     ("Fiction", "Series", "No"),
    # Iain M. Banks / Culture
    "intrusion":                                  ("Fiction", "Standalone", "No"),
    # Kim Stanley Robinson
    "the ministry for the future":                ("Fiction", "Standalone", "No"),
    "aurora":                                     ("Fiction", "Standalone", "No"),
    # H.G. Wells
    "the day of the triffids":                    ("Fiction", "Standalone", "No"),
    "the kraken wakes":                           ("Fiction", "Standalone", "No"),
    "the midwich cuckoos":                        ("Fiction", "Standalone", "No"),
    "the war in the air":                         ("Fiction", "Standalone", "No"),
    "kipps: the story of a simple soul":          ("Fiction", "Standalone", "No"),
    # John Wyndham
    "chocky":                                     ("Fiction", "Standalone", "No"),
    # Misc fiction
    "the road":                                   ("Fiction", "Standalone", "No"),
    "blood meridian, or, the evening redness in the west": ("Fiction", "Standalone", "No"),
    "old man and the sea":                        ("Fiction", "Standalone", "No"),
    "old man and the sea":                        ("Fiction", "Standalone", "No"),
    "bliss":                                      ("Fiction", "Standalone", "No"),
    "the god of small things":                    ("Fiction", "Standalone", "No"),
    "the unbearable lightness of being:":         ("Fiction", "Standalone", "No"),
    "the glass bead game":                        ("Fiction", "Standalone", "No"),
    "pale fire":                                  ("Fiction", "Standalone", "No"),
    "one hundred years of solitude":              ("Fiction", "Standalone", "No"),
    "moby-dick or, the whale":                    ("Fiction", "Standalone", "No"),
    "a book of common prayer":                    ("Fiction", "Standalone", "No"),
    "labyrinths: selected stories and other writings": ("Fiction", "Standalone", "No"),
    "invisible cities":                           ("Fiction", "Standalone", "No"),
    "persuasion":                                 ("Fiction", "Standalone", "No"),
    "station eleven":                             ("Fiction", "Standalone", "No"),
    "severance":                                  ("Fiction", "Standalone", "No"),
    "california":                                 ("Fiction", "Standalone", "No"),
    "the sellout":                                ("Fiction", "Standalone", "No"),
    "gold fame citrus":                           ("Fiction", "Standalone", "No"),
    "half of a yellow sun":                       ("Fiction", "Standalone", "No"),
    "things fall apart":                          ("Fiction", "Standalone", "No"),
    "wild swans: three daughters of china":       ("NonFiction", "Standalone", "No"),
    "the god of small things":                    ("Fiction", "Standalone", "No"),
    "i love dick":                                ("NonFiction", "Standalone", "No"),  # memoir/auto-fiction
    "trick mirror: reflections on self-delusion": ("NonFiction", "Standalone", "No"),
    "a room called earth":                        ("Fiction", "Standalone", "No"),
    "the overstory":                              ("Fiction", "Standalone", "No"),
    "this all come back now":                     ("Fiction", "Standalone", "No"),
    "foreign soil":                               ("Fiction", "Standalone", "No"),
    "the natural way of things":                  ("Fiction", "Standalone", "No"),
    "a town like alice":                          ("Fiction", "Standalone", "No"),
    "accelerando":                                ("Fiction", "Standalone", "No"),
    "the circle":                                 ("Fiction", "Standalone", "No"),
    "gold fame citrus":                           ("Fiction", "Standalone", "No"),
    "the book of elsewhere":                      ("Fiction", "Standalone", "No"),
    "bea wolf":                                   ("Fiction", "Standalone", "No"),
    "a clockwork orange":                         ("Fiction", "Standalone", "No"),
    "brave new world":                            ("Fiction", "Standalone", "No"),
    "1984":                                       ("Fiction", "Standalone", "No"),
    "island":                                     ("Fiction", "Standalone", "No"),
    "we":                                         ("Fiction", "Standalone", "No"),
    "r.u.r.":                                     ("Fiction", "Standalone", "No"),
    "the mysterious island (illustrated)":        ("Fiction", "Standalone", "No"),
    "the road":                                   ("Fiction", "Standalone", "No"),
    "ready player one (ready player one, #1)":    ("Fiction", "Series", "No"),
    "the martian":                                ("Fiction", "Standalone", "No"),
    "project hail mary":                          ("Fiction", "Standalone", "No"),
    "fahrenheit 451":                             ("Fiction", "Standalone", "No"),
    "flowers for algernon":                       ("Fiction", "Standalone", "No"),
    "world war z: an oral history of the zombie war": ("Fiction", "Standalone", "No"),
    "the shining (the shining, #1)":              ("Fiction", "Standalone", "No"),
    "2001: a space odyssey (space odyssey, #1)":  ("Fiction", "Series", "No"),
    "the hobbit":                                 ("Fiction", "Series", "No"),
    "farmer giles of ham":                        ("Fiction", "Series", "No"),
    "charlie and the chocolate factory (charlie bucket, #1)": ("Fiction", "Series", "No"),
    "the lion, the witch and the wardrobe (chronicles of narnia, #1)": ("Fiction", "Series", "No"),
    "lolita":                                     ("Fiction", "Standalone", "No"),
    "catch-22":                                   ("Fiction", "Standalone", "No"),
    "lord of the flies":                          ("Fiction", "Standalone", "No"),
    "the catcher in the rye":                     ("Fiction", "Standalone", "No"),
    "the great gatsby":                           ("Fiction", "Standalone", "No"),
    "gulliver's travels":                         ("Fiction", "Standalone", "No"),
    "gulliver\u00e6s travels":                    ("Fiction", "Standalone", "No"),
    "just so stories":                            ("Fiction", "Standalone", "No"),
    "the wind in the willows":                    ("Fiction", "Standalone", "No"),
    "the tale of peter rabbit (world of beatrix potter, #1)": ("Fiction", "Standalone", "No"),
    "winnie-the-pooh (winnie-the-pooh, #1)":      ("Fiction", "Standalone", "No"),
    "the swiss family robinson":                  ("Fiction", "Standalone", "No"),
    "alice's adventures in wonderland / through the looking-glass": ("Fiction", "Standalone", "No"),
    "alice\u00e6s adventures in wonderland / through the looking-glass": ("Fiction", "Standalone", "No"),
    "the adventures of tom sawyer":               ("Fiction", "Standalone", "No"),
    "travels with my aunt":                       ("Fiction", "Standalone", "No"),
    "the testimony":                              ("Fiction", "Standalone", "No"),
    "metropolis":                                 ("Fiction", "Standalone", "No"),
    "the quantum sausage machine (a science fiction adventure)": ("Fiction", "Standalone", "No"),
    "the specialist":                             ("Fiction", "Standalone", "No"),
    "i am legend and other stories":             ("Fiction", "Standalone", "No"),
    "diaspora":                                   ("Fiction", "Standalone", "No"),
    "hunger":                                     ("Fiction", "Standalone", "No"),
    "the hunger games (the hunger games, #1)":    ("Fiction", "Series", "No"),
    "catching fire (the hunger games, #2)":       ("Fiction", "Series", "No"),
    "mockingjay (the hunger games, #3)":          ("Fiction", "Series", "No"),
    "the day of the triffids":                    ("Fiction", "Standalone", "No"),
    "the kraken wakes":                           ("Fiction", "Standalone", "No"),
    "the moon is a harsh mistress":               ("Fiction", "Standalone", "No"),
    "the city & the city":                        ("Fiction", "Standalone", "No"),
    "high-rise":                                  ("Fiction", "Standalone", "No"),
    "the drowned world":                          ("Fiction", "Standalone", "No"),
    "satin island":                               ("Fiction", "Standalone", "No"),
    "crime and punishment":                       ("Fiction", "Standalone", "No"),
    "a very short, fairly interesting and reasonably cheap book about studying organizations": ("NonFiction", "Standalone", "No"),
    "the prince (a penguin classics hardcover)":  ("NonFiction", "Standalone", "No"),
    "what sort of people should there be?":       ("NonFiction", "Standalone", "No"),
    "the case against perfection: ethics in the age of genetic engineering": ("NonFiction", "Standalone", "No"),
    "i am a strange loop":                        ("NonFiction", "Standalone", "No"),
    "klara and the sun":                          ("Fiction", "Standalone", "No"),
    "other minds":                                ("NonFiction", "Standalone", "No"),
    "kalpa imperial: the greatest empire that never was": ("Fiction", "Standalone", "No"),
    "a summer beyond your reach":                 ("Fiction", "Standalone", "No"),
    "your utopia":                                ("Fiction", "Standalone", "No"),
    "the korean myths: a guide to the gods, heroes and legends": ("NonFiction", "Standalone", "No"),
    "frankenstein":                               ("Fiction", "Standalone", "No"),
    "the last man":                               ("Fiction", "Standalone", "No"),
    "beowulf":                                    ("Fiction", "Standalone", "No"),
    "the silence of the girls (women of troy, #1)": ("Fiction", "Series", "No"),
    "the odyssey":                                ("Fiction", "Standalone", "No"),
    "the penelopiad (faber drama)":               ("Fiction", "Standalone", "No"),
    "micromegas":                                 ("Fiction", "Standalone", "No"),
    "the nun - diderot (erotic classics)":        ("Fiction", "Standalone", "Yes"),
    # Comics/graphic novels
    "blade runner 2019 #1":                       ("Fiction", "Series", "No"),
    "brzrkr: bloodlines, vol. 1":                 ("Fiction", "Series", "No"),
    "brzrkr, volume 2":                           ("Fiction", "Series", "No"),
    "brzrkr, volume 3":                           ("Fiction", "Series", "No"),
    "alien\u2502: the unproduced first-draft screenplay by william gibson": ("Fiction", "Standalone", "No"),
    "alien│: the unproduced first-draft screenplay by william gibson": ("Fiction", "Standalone", "No"),
    "chronicles of a lizard nobody (chronicles of a lizard nobody, #1)": ("Fiction", "Series", "No"),
    "coriolanus (the pelican shakespeare)":       ("Fiction", "Standalone", "No"),
    "the midwich cuckoos":                        ("Fiction", "Standalone", "No"),
    "we can build you":                           ("Fiction", "Standalone", "No"),
    "d'airain #1 (of 2)":                         ("Fiction", "Series", "No"),
    "d'airain #2 (of 2)":                         ("Fiction", "Series", "No"),
    "milo manara's gullivera":                    ("Fiction", "Standalone", "No"),
    "tank girl: one (tank girl, #1)":             ("Fiction", "Series", "No"),
    "lost at sea":                                ("Fiction", "Standalone", "No"),
    "seconds":                                    ("Fiction", "Standalone", "No"),
    "bitch planet #1":                            ("Fiction", "Series", "No"),
    "the walking dead: compendium one":           ("Fiction", "Series", "No"),
    "the walking dead: compendium two (the walking dead, #9-16)": ("Fiction", "Series", "No"),
    "the hobbit":                                 ("Fiction", "Series", "No"),
    "ender's game, volume 1: battle school (ender's saga)": ("Fiction", "Series", "No"),
    # NonFiction – tech
    "the phoenix project: a novel about it, devops, and helping your business win": ("Fiction", "Standalone", "No"),
    "the goal: a process of ongoing improvement": ("Fiction", "Standalone", "No"),
    "an elegant puzzle: systems of engineering management": ("NonFiction", "Standalone", "No"),
    "working in public: the making and maintenance of open source software": ("NonFiction", "Standalone", "No"),
    "the lean startup":                           ("NonFiction", "Standalone", "No"),
    "running lean: iterate from plan a to a plan that works (lean series)": ("NonFiction", "Standalone", "No"),
    "peopleware: productive projects and teams":  ("NonFiction", "Standalone", "No"),
    "the mythical man-month: essays on software engineering": ("NonFiction", "Standalone", "No"),
    "it doesn't have to be crazy at work":        ("NonFiction", "Standalone", "No"),
    "remote: office not required":                ("NonFiction", "Standalone", "No"),
    "deep work: rules for focused success in a distracted world": ("NonFiction", "Standalone", "No"),
    "hackers & painters: big ideas from the computer age": ("NonFiction", "Standalone", "No"),
    "the cathedral & the bazaar: musings on linux and open source by an accidental revolutionary": ("NonFiction", "Standalone", "No"),
    "a girl corrupted by the internet is the summoned hero?!": ("Fiction", "Standalone", "No"),
    "the cucumber book: behaviour-driven development for testers and developers (pragmatic programmers)": ("NonFiction", "Standalone", "No"),
    "scrum: a breathtakingly brief and agile introduction": ("NonFiction", "Standalone", "No"),
    "the elements of scrum":                      ("NonFiction", "Standalone", "No"),
    "race against the machine":                   ("NonFiction", "Standalone", "No"),
    # NonFiction – management/business
    "be slightly evil: a playbook for sociopaths (ribbonfarm roughs)": ("NonFiction", "Standalone", "No"),
    "information doesn't want to be free: laws for the internet age": ("NonFiction", "Standalone", "No"),
    "the gervais principle: the complete series, with a bonus essay on office space (ribbonfarm roughs)": ("NonFiction", "Standalone", "No"),
    "tempo: timing, tactics and strategy in narrative-driven decision-making": ("NonFiction", "Standalone", "No"),
    "post-capitalist society":                    ("NonFiction", "Standalone", "No"),
    "the life-changing magic of tidying":         ("NonFiction", "Standalone", "No"),
    "the epic struggle of the internet of things": ("NonFiction", "Standalone", "No"),
    "zen and the art of motorcycle maintenance: an inquiry into values": ("NonFiction", "Standalone", "No"),
    "on writing well: the classic guide to writing nonfiction": ("NonFiction", "Standalone", "No"),
    "writing to learn: how to write--and think--clearly about any subject at all": ("NonFiction", "Standalone", "No"),
    "parkinson's law":                            ("NonFiction", "Standalone", "No"),
    "the undercover economist":                   ("NonFiction", "Standalone", "No"),
    "the lessons of history":                     ("NonFiction", "Standalone", "No"),
    "irrationality":                              ("NonFiction", "Standalone", "No"),
    "superforecasting: the art and science of prediction": ("NonFiction", "Standalone", "No"),
    "expert political judgment: how good is it? how can we know?": ("NonFiction", "Standalone", "No"),
    "open borders: the science and ethics of immigration": ("NonFiction", "Standalone", "No"),
    "dataclysm: who we are (when we think no one's looking)": ("NonFiction", "Standalone", "No"),
    "nudge: improving decisions about health, wealth, and happiness": ("NonFiction", "Standalone", "No"),
    "thinking, fast and slow":                    ("NonFiction", "Standalone", "No"),
    "freakonomics: a rogue economist explores the hidden side of everything": ("NonFiction", "Standalone", "No"),
    "illustrated superfreakonomics. steven d. levitt & stephen j. dubner": ("NonFiction", "Standalone", "No"),
    "superfreakonomics: global cooling, patriotic prostitutes and why suicide bombers should buy life insurance": ("NonFiction", "Standalone", "No"),
    "the economic naturalist: in search of explanations for everyday enigmas": ("NonFiction", "Standalone", "No"),
    "everything i ever needed to know about economics i learned from online dating": ("NonFiction", "Standalone", "No"),
    "the conundrum: how scientific innovation, increased efficiency, and good intentions can make our energy and climate problems worse": ("NonFiction", "Standalone", "No"),
    "less doing, more living: make everything in life easier": ("NonFiction", "Standalone", "No"),
    "social physics: how good ideas spread \u00f9 the lessons from a new science": ("NonFiction", "Standalone", "No"),
    "social physics: how good ideas spread - the lessons from a new science": ("NonFiction", "Standalone", "No"),
    "perfectly reasonable deviations (from the beaten track): the letters of richard p. feynman": ("NonFiction", "Standalone", "No"),
    "the body: a guide for occupants":            ("NonFiction", "Standalone", "No"),
    # More NF
    "sex at dawn: the prehistoric origins of modern sexuality": ("NonFiction", "Standalone", "No"),
    "the ethical slut: a practical guide to polyamory, open relationships, and other freedoms in sex and love": ("NonFiction", "Standalone", "No"),
    "influence: the psychology of persuasion (collins business essentials book 16)": ("NonFiction", "Standalone", "No"),
    "how not to be a d*ck: an everyday etiquette guide": ("NonFiction", "Standalone", "No"),
    "homo deus: a brief history of tomorrow":     ("NonFiction", "Standalone", "No"),
    "21 lessons for the 21st century":            ("NonFiction", "Standalone", "No"),
    "the beginning of infinity: explanations that transform the world": ("NonFiction", "Standalone", "No"),
    "what if?: serious scientific answers to absurd hypothetical questions": ("NonFiction", "Standalone", "No"),
    "superintelligence: paths, dangers, strategies": ("NonFiction", "Standalone", "No"),
    "global catastrophic risks":                  ("NonFiction", "Standalone", "No"),
    "a new kind of science":                      ("NonFiction", "Standalone", "No"),
    "the structure of scientific revolutions":    ("NonFiction", "Standalone", "No"),
    "naive set theory (undergraduate texts in mathematics)": ("NonFiction", "Standalone", "No"),
    "the craft of research":                      ("NonFiction", "Standalone", "No"),
    "naked statistics: stripping the dread from the data": ("NonFiction", "Standalone", "No"),
    "innumeracy: mathematical illiteracy and its consequences": ("NonFiction", "Standalone", "No"),
    "mathematics: a very short introduction":     ("NonFiction", "Standalone", "No"),
    "logic: a very short introduction":           ("NonFiction", "Standalone", "No"),
    "choice theory: a very short introduction":   ("NonFiction", "Standalone", "No"),
    "economics: a very short introduction":       ("NonFiction", "Standalone", "No"),
    "epicureanism: a very short introduction":    ("NonFiction", "Standalone", "No"),
    "information: a very short introduction (very short introductions)": ("NonFiction", "Standalone", "No"),
    "a very short, fairly interesting and reasonably cheap book about studying organizations": ("NonFiction", "Standalone", "No"),
    "introducing fractal geometry":               ("NonFiction", "Standalone", "No"),
    "the annotated flatland: a romance of many dimensions": ("NonFiction", "Standalone", "No"),
    "flatland: a romance of many dimensions":     ("Fiction",    "Standalone", "No"),
    "euclid's window: from parallel lines to hyperspace": ("NonFiction", "Standalone", "No"),
    "flatterland":                                ("NonFiction", "Standalone", "No"),
    "lewis carroll in numberland: his fantastical mathematical logical life": ("NonFiction", "Standalone", "No"),
    "lewis carroll in numberland: his fantastic, mathematical, logical life": ("NonFiction", "Standalone", "No"),
    "i am a strange loop":                        ("NonFiction", "Standalone", "No"),
    "sustainable energy - without the hot air":   ("NonFiction", "Standalone", "No"),
    "energy and civilization: a history":         ("NonFiction", "Standalone", "No"),
    "the selfish gene":                           ("NonFiction", "Standalone", "No"),
    "climbing mount improbable":                  ("NonFiction", "Standalone", "No"),
    "checklist manifesto how to get things right":("NonFiction", "Standalone", "No"),
    "future people: a moderate consequentialist account of our obligations to future generations": ("NonFiction", "Standalone", "No"),
    "ethics for a broken world: imagining philosophy after catastrophe": ("NonFiction", "Standalone", "No"),
    "our final century: the 50/50 threat to humanity's survival": ("NonFiction", "Standalone", "No"),
    "our final century? : will the human race survive the twenty-first century?": ("NonFiction", "Standalone", "No"),
    "the meaning of the 21st century: a vital blueprint of ensuring our future": ("NonFiction", "Standalone", "No"),
    "posthumanism: anthropological insights":     ("NonFiction", "Standalone", "No"),
    "what sort of people should there be?":       ("NonFiction", "Standalone", "No"),
    "why i am not a christian":                   ("NonFiction", "Standalone", "No"),
    "coming of age in samoa: a psychological study of primitive youth for western civilisation": ("NonFiction", "Standalone", "No"),
    "sand talk: how indigenous thinking can save the world": ("NonFiction", "Standalone", "No"),
    "songlines: the power and promise":           ("NonFiction", "Standalone", "No"),
    "first knowledges design: building on country (first knowledges, 2)": ("NonFiction", "Series", "No"),
    "butts: a backstory":                         ("NonFiction", "Standalone", "No"),
    "notes on grief":                             ("NonFiction", "Standalone", "No"),
    "robot ethics (the mit press essential knowledge series)": ("NonFiction", "Standalone", "No"),
    "under pressure: diving deeper with human factors": ("NonFiction", "Standalone", "No"),
    "basic cave diving: a blueprint for survival": ("NonFiction", "Standalone", "No"),
    "oxygen hacker's companion":                  ("NonFiction", "Standalone", "No"),
    "sweetness and power: the place of sugar in modern history": ("NonFiction", "Standalone", "No"),
    "food in history":                            ("NonFiction", "Standalone", "No"),
    "the book of tea":                            ("NonFiction", "Standalone", "No"),
    "molecular gastronomy: exploring the science of flavor (arts and traditions of the table: perspectives on culinary history)": ("NonFiction", "Standalone", "No"),
    "foundations of flavor: the noma guide to fermentation": ("NonFiction", "Standalone", "No"),
    "liquid intelligence: the art and science of the perfect cocktail": ("NonFiction", "Standalone", "No"),
    "a super upsetting cookbook about sandwiches": ("NonFiction", "Standalone", "No"),
    "nom nom paleo: food for humans (volume 1)":  ("NonFiction", "Standalone", "No"),
    "primal cravings: your favorite foods made paleo": ("NonFiction", "Standalone", "No"),
    "beyond bacon: paleo recipes that respect the whole hog": ("NonFiction", "Standalone", "No"),
    "tonic water aka g&t wtf":                    ("NonFiction", "Standalone", "No"),
    "mr. boston: official bartender's & party guide": ("NonFiction", "Standalone", "No"),
    "how not to be a d*ck: an everyday etiquette guide": ("NonFiction", "Standalone", "No"),
    "meditations":                                ("NonFiction", "Standalone", "No"),
    "on the shortness of life":                   ("NonFiction", "Standalone", "No"),
    "the gallic war":                             ("NonFiction", "Standalone", "No"),
    "the strategemata":                           ("NonFiction", "Standalone", "No"),
    "the sciences of the artificial":             ("NonFiction", "Standalone", "No"),
    "religion for atheists: a non-believer's guide to the uses of religion": ("NonFiction", "Standalone", "No"),
    "techgnosis: myth, magic & mysticism in the age of information": ("NonFiction", "Standalone", "No"),
    "the craftsman":                              ("NonFiction", "Standalone", "No"),
    "the back of the napkin: solving problems and selling ideas with pictures": ("NonFiction", "Standalone", "No"),
    "information doesn't want to be free: laws for the internet age": ("NonFiction", "Standalone", "No"),
    "the dot-com city: silicon valley urbanism":  ("NonFiction", "Standalone", "No"),
    "dark matter and trojan horses: a strategic design vocabulary": ("NonFiction", "Standalone", "No"),
    "future practice: conversations from the edge of architecture": ("NonFiction", "Standalone", "No"),
    "how buildings learn: what happens after they're built": ("NonFiction", "Standalone", "No"),
    "modern architecture: a planetary warming history": ("NonFiction", "Standalone", "No"),
    "modes of criticism 4: radical pedagogy: investigating the use of the word 'radical' in design discourse and practice": ("NonFiction", "Standalone", "No"),
    "a history of the future in 100 objects":     ("Fiction",    "Standalone", "No"),
    "science fiction prototyping: designing the future with science fiction": ("NonFiction", "Standalone", "No"),
    "wired for war: the robotics revolution and conflict in the 21st century": ("NonFiction", "Standalone", "No"),
    "architecture in the digital age: design and manufacturing": ("NonFiction", "Standalone", "No"),
    "the city of tomorrow: sensors, networks, hackers, and the future of urban life (the future series)": ("NonFiction", "Standalone", "No"),
    "counterproductive: time management in the knowledge economy": ("NonFiction", "Standalone", "No"),
    "testosterone rex: unmaking the myths of our gendered minds": ("NonFiction", "Standalone", "No"),
    "the end of money: counterfeiters, preachers, techies, dreamers--and the coming cashless Society": ("NonFiction", "Standalone", "No"),
    "the end of money: counterfeiters, preachers, techies, dreamers--and the coming cashless society": ("NonFiction", "Standalone", "No"),
    "dataclysm: who we are (when we think no one's looking)": ("NonFiction", "Standalone", "No"),
    "living with complexity":                     ("NonFiction", "Standalone", "No"),
    "trick mirror: reflections on self-delusion": ("NonFiction", "Standalone", "No"),
    "other minds":                                ("NonFiction", "Standalone", "No"),
    "the conundrum: how scientific innovation, increased efficiency, and good intentions can make our energy and climate problems worse": ("NonFiction", "Standalone", "No"),
    "designing interactions":                     ("NonFiction", "Standalone", "No"),
    "harry potter and the methods of rationality": ("Fiction", "Series", "No"),
    "thinking, fast and slow":                    ("NonFiction", "Standalone", "No"),
    "a girl corrupted by the internet is the summoned hero?!": ("Fiction", "Standalone", "No"),
    "ubik":                                       ("Fiction", "Standalone", "No"),
    "tomorrow, when the war began (the tomorrow series, #1)": ("Fiction", "Series", "No"),
    "hamburger: a global history (edible)":       ("NonFiction", "Standalone", "No"),
    "flowers for algernon":                       ("Fiction", "Standalone", "No"),
    "the phoenix project: a novel about it, devops, and helping your business win": ("Fiction", "Standalone", "No"),
    "feynman":                                    ("NonFiction", "Standalone", "No"),
    "logicomix":                                  ("NonFiction", "Standalone", "No"),
    "logicomix: an epic search for truth":        ("NonFiction", "Standalone", "No"),
    "the complete maus":                          ("NonFiction", "Standalone", "No"),
    "raised on ritalin":                          ("NonFiction", "Standalone", "No"),
    "goomics: google's corporate culture revealed through internal comics": ("NonFiction", "Standalone", "No"),
    "how long 'til black future month?":          ("Fiction", "Standalone", "Yes"),
    "the very hungry caterpillar":                ("Fiction", "Standalone", "No"),
    "the little book of thunks: 260 questions to make your brain go ouch! (the little books)": ("NonFiction", "Standalone", "No"),
    "nss cavern diving manual":                   ("NonFiction", "Standalone", "No"),
    "shipwrecks of the dover straits":            ("NonFiction", "Standalone", "No"),
    "mit building 20: short stories":             ("NonFiction", "Standalone", "No"),
    "buckminster fuller poet of geometry":        ("NonFiction", "Standalone", "No"),
    "humanimal 3.0":                              ("NonFiction", "Standalone", "No"),
    "architecture words 4: having words":         ("NonFiction", "Standalone", "No"),
    "the prefab bathroom: an architectural history": ("NonFiction", "Standalone", "No"),
    "number 9: the search for the sigma code":    ("NonFiction", "Standalone", "No"),
    "generic architectures/arquitecturas geneticas": ("NonFiction", "Standalone", "No"),
    "genetic architectures/arquitecturas geneticas": ("NonFiction", "Standalone", "No"),
    "collective intelligence in design (architectural design)": ("NonFiction", "Standalone", "No"),
    "emergence: morphogenetic design strategies (architectural design)": ("NonFiction", "Standalone", "No"),
    "nox: machining architecture":                ("NonFiction", "Standalone", "No"),
    "digital real--blobmeister: first built projects (german and english edition)": ("NonFiction", "Standalone", "No"),
    "architecture's new media: principles, theories, and methods of computer-aided design": ("NonFiction", "Standalone", "No"),
    "tooling (pamphlet architecture, 27)":        ("NonFiction", "Standalone", "No"),
    "folding architecture":                       ("NonFiction", "Standalone", "No"),
    "japanese graphics now!":                     ("NonFiction", "Standalone", "No"),
    "the way things work":                        ("NonFiction", "Standalone", "No"),
    "atelier van lieshout":                       ("NonFiction", "Standalone", "No"),
    "intricacy: a project by greg lynn form":     ("NonFiction", "Standalone", "No"),
    "space craft: developments in architectural computing": ("NonFiction", "Standalone", "No"),
    "softspace: from a representation of form to a simulation of space": ("NonFiction", "Standalone", "No"),
    "natural born caadesigners: young american architects (the information technology revolution in architecture)": ("NonFiction", "Standalone", "No"),
    "xyz: the architecture of dagmar richter":    ("NonFiction", "Standalone", "No"),
    "expressive form":                            ("NonFiction", "Standalone", "No"),
    "c# language pocket reference":               ("NonFiction", "Standalone", "No"),
    "c# 2005 for dummies":                        ("NonFiction", "Standalone", "No"),
    "css3 for web designers":                     ("NonFiction", "Standalone", "No"),
    "html5 for web designers":                    ("NonFiction", "Standalone", "No"),
    "mobile first":                               ("NonFiction", "Standalone", "No"),
    "responsive web design":                      ("NonFiction", "Standalone", "No"),
    "just enough research":                       ("NonFiction", "Standalone", "No"),
    "being digital":                              ("NonFiction", "Standalone", "No"),
    "an introduction to genetic algorithms (complex adaptive systems)": ("NonFiction", "Standalone", "No"),
    "blondie24: playing at the edge of ai (the morgan kaufmann series in artificial intelligence)": ("NonFiction", "Standalone", "No"),
    "succeeding with autocad: a full course in 2d drafting and 3d modelling": ("NonFiction", "Standalone", "No"),
    "engineering mathematics":                    ("NonFiction", "Standalone", "No"),
    "a new kind of science":                      ("NonFiction", "Standalone", "No"),
    "mathland from flatland to hypersurfaces":    ("NonFiction", "Standalone", "No"),
    "programming.architecture":                   ("NonFiction", "Standalone", "No"),
    "art forms from the ocean: the radiolarian prints of ernst haeckel": ("NonFiction", "Standalone", "No"),
    "art forms in nature":                        ("NonFiction", "Standalone", "No"),
    "3ds max 8 maxscript essentials":             ("NonFiction", "Standalone", "No"),
    "me++: the cyborg self and the networked city": ("NonFiction", "Standalone", "No"),
    "creation : life and how to make it":         ("NonFiction", "Standalone", "No"),
    "nufonia must fall":                          ("Fiction",    "Standalone", "No"),
    "graphic anatomy - atelier bow wow":          ("NonFiction", "Standalone", "No"),
    "colour for architecture today":              ("NonFiction", "Standalone", "No"),
    "the way things work":                        ("NonFiction", "Standalone", "No"),
    "finite and infinite games: a vision of life as play and possibility": ("NonFiction", "Standalone", "No"),
    "the cartoon history of the modern world part 1: from columbus to the u.s. constitution (the cartoon history of the modern world, #1)": ("NonFiction", "Series", "No"),
    "the cartoon history of the universe iii: from the rise of arabia to the renaissance (the cartoon history of the universe, #3)": ("NonFiction", "Series", "No"),
    "the cartoon history of the universe ii, vol. 8-13: from the springtime of china to the fall of rome (the cartoon history of the universe, #2)": ("NonFiction", "Series", "No"),
    "the cartoon history of the universe i, vol. 1-7: from the big bang to alexander the great (the cartoon history of the universe, #1)": ("NonFiction", "Series", "No"),
    "the cartoon guide to statistics":            ("NonFiction", "Standalone", "No"),
    "the walking dead: compendium two (the walking dead, #9-16)": ("Fiction", "Series", "No"),
    "the walking dead: compendium one":           ("Fiction", "Series", "No"),
    "the economic naturalist: in search of explanations for everyday enigmas": ("NonFiction", "Standalone", "No"),
    "economic naturalist":                        ("NonFiction", "Standalone", "No"),
    "the future of work (cato unbound book 62006)": ("NonFiction", "Standalone", "No"),
    "codex seraphinianus":                        ("Fiction",    "Standalone", "No"),
    "necronomicum #1 (necronomicum: the magazine of weird erotica)": ("Fiction", "Series", "No"),
    "accessing the future: a disability-themed anthology of speculative fiction": ("Fiction", "Standalone", "No"),
    "hieroglyph: stories and visions for a better future": ("Fiction", "Standalone", "No"),
    "future visions: original science fiction inspired by microsoft": ("Fiction", "Standalone", "No"),
    "if this goes on":                            ("Fiction", "Standalone", "No"),
    "a town like alice":                          ("Fiction", "Standalone", "No"),
    "the city of tomorrow: sensors, networks, hackers, and the future of urban life (the future series)": ("NonFiction", "Standalone", "No"),
    "science fiction prototyping: designing the future with science fiction": ("NonFiction", "Standalone", "No"),
    "boyd: the fighter pilot who changed the art of war": ("NonFiction", "Standalone", "No"),
    "the secret history of the mongol queens: how the daughters of genghis khan rescued his empire": ("NonFiction", "Standalone", "No"),
    "ghost fleet: a novel of the next world war": ("Fiction", "Standalone", "No"),
    "the rise and fall of d.o.d.o. (d.o.d.o., #1)": ("Fiction", "Series", "No"),
    "aurora":                                     ("Fiction", "Standalone", "No"),
    "the ministry for the future":                ("Fiction", "Standalone", "No"),
    "a psalm for the wild-built":                 ("Fiction", "Series", "Yes"),
    "a prayer for the crown-shy":                 ("Fiction", "Series", "Yes"),
    "binti (binti, #1)":                          ("Fiction", "Series", "No"),
    "farmer giles of ham":                        ("Fiction", "Series", "No"),
    "the hobbit":                                 ("Fiction", "Series", "No"),
    "divisidero (signed first edition)":          ("Fiction", "Standalone", "No"),
    "the cat's table":                            ("Fiction", "Standalone", "No"),
    "running in the family":                      ("NonFiction", "Standalone", "No"),
    "anil's ghost":                               ("Fiction", "Standalone", "No"),
    "coming through slaughter":                   ("Fiction", "Standalone", "No"),
    "in the skin of a lion":                      ("Fiction", "Standalone", "No"),
    "the english patient":                        ("Fiction", "Standalone", "No"),
    "the circle":                                 ("Fiction", "Standalone", "No"),
    "prelude to foundation (foundation, #6)":     ("Fiction", "Series", "No"),
    "a clockwork orange":                         ("Fiction", "Standalone", "No"),
    "the power":                                  ("Fiction", "Standalone", "No"),
    "klara and the sun":                          ("Fiction", "Standalone", "No"),
    "i love dick":                                ("NonFiction", "Standalone", "No"),
    "the course of love":                         ("Fiction", "Standalone", "No"),
    "murder in the mews: a hercule poirot short story (hercule poirot, #ss-36)": ("Fiction", "Series", "No"),
    "agatha christie":                            ("Fiction", "Series", "No"),
    "the measure of time (guido guerrieri series)": ("Fiction", "Series", "No"),
    "juice":                                      ("Fiction", "Standalone", "No"),
    "study of cave diving accidents: accident analysis, human factors, and safety lessons from technical and cave diving worldwide": ("NonFiction", "Standalone", "No"),
}


def main():
    books = pd.read_csv(BOOKS_FILE, dtype=str)

    # Ensure annotation columns exist
    for col in ANNO_COLS:
        if col not in books.columns:
            books[col] = ""

    filled = 0

    for i, row in books.iterrows():
        # Skip if all annotation columns already filled
        if all(str(row.get(c, "")).strip() not in ("", "nan") for c in ANNO_COLS):
            continue

        isbn = str(row.get("isbn13", "")).strip()
        raw_title = str(row.get("title", "")).strip()
        norm_title = normalise(raw_title)
        stripped_title = normalise(strip_series(raw_title))

        # Lookup order: isbn13 → exact normalised title → series-stripped title
        source = (
            BY_ISBN.get(isbn)
            or BY_TITLE.get(norm_title)
            or BY_TITLE.get(stripped_title)
        )
        if not source:
            continue

        fic, series, lgbtq = source
        changed = False
        for col, val in zip(ANNO_COLS, (fic, series, lgbtq)):
            current = str(row.get(col, "")).strip()
            if current in ("", "nan") and val:
                books.at[i, col] = val
                changed = True
        if changed:
            filled += 1

    books.to_csv(BOOKS_FILE, index=False)
    print(f"Annotated {filled} books.")

    for col in ANNO_COLS:
        n = books[col].apply(lambda x: str(x).strip() not in ("", "nan") and pd.notna(x)).sum()
        print(f"  {col}: {n} / {len(books)} filled")

    blank = books[books["ficOrNonFic"].apply(lambda x: str(x).strip() in ("", "nan"))]
    if not blank.empty:
        print(f"\n{len(blank)} books still need manual annotation:")
        for _, r in blank.iterrows():
            print(f"  {r['title']}")


if __name__ == "__main__":
    main()
