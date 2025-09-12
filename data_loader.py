# data_loader.py
import pandas as pd

# --- Dictionaries for translations ---
RENAME_COLS = {
    "Ausleihtyp": "Type of Transaction", 
    "Titel": "Title",
    "Autor:in": "Author",
    "Medientypcode": "Media Type",
    "Fächerstatistik": "Genre",
    "Benutzergruppe": "User Group",
    "Geschlecht": "Gender",
    "Altersgruppe": "Age Group",
    "Fächerstatistik2": "Target Group",
    "Monat": "Month",
    "Sigel besitzende Bibliothek": "Library",
}

MEDIA_TYPE_TRANSLATION = {
    "Buch": "Book",
    "Medienkombination": "Media Combination",
    "Konventionelles Spiel": "Conventional Game",
    "DVD": "DVD",
    "Noten": "Sheet Music",
    "Zeitschrift": "Magazine",
    "CD": "CD",
    "Software": "Software",
    "Konsolenspiel": "Console Game",
    "Mobiles Endgerät": "Mobile Device",
    "Verkürzte Leihfrist": "Shortened Loan Period",
    "Sonstiges": "Other",
    "Nur vor Ort entleihbar": "In-library use only",
}

GENDER_TRANSLATION = {"M": "Male", "W": "Female", "K": "No Information"}

GENRE_TRANSLATION = {
    "Sachliteratur": "Non-fiction",
    "Schöne Literatur": "Fiction",
    "Spiele": "Games",
    "Musik": "Music",
}

USER_GROUP_TRANSLATION = {
    "Schüler ab 16": "Students 16+",
    "Erwachsene": "Adults",
    "ermäßigte Erwachsene": "Adults (reduced rate)",
    "entgeltfreie Erwachsene": "Adults (no charge)",
    "Bibliothekspersonal": "Library Staff",
    "Kinder und Jugendliche": "Children and Youth",
    "Öffentlich-rechtliche Institution": "Public Institution",
    "Flüchtlinge": "Refugees",
    "Berliner Verwaltung": "Berlin Administration",
}

TARGET_GROUP_TRANSLATION = {
    "Erwachsene": "Adults",
    "Jugend": "Youth",
    "Kinder": "Children",
}

LIBRARIES = {
    975: "Bibliothek Am Wasserturm",
    971: "B.-von-Arnim-Bibliothek",
    650: "W.-Schnurre-Bibliothek",
    462: "J.-Korczak-Bibliothek",
    655: "Bibliothek Karow",
    457: "H.-Böll-Bibliothek",
    972: "K.-Tucholsky-Bibliothek",
    471: "Bibliothek Buch",
}

MONTH_NAME_MAP = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December",
}
MONTH_ORDER = list(MONTH_NAME_MAP.values())

AGE_ORDER = [
    "0-5", "6-10", "11-14", "15-17", "18-24",
    "25-39", "40-54", "55-64", "65-79", "80+",
]


def load_raw(path: str, year: int) -> pd.DataFrame:
    """Load a Parquet file and add a Year column."""
    df = pd.read_parquet(path)
    df["Year"] = int(year)
    return df

def load_raw_multiple(files: dict) -> pd.DataFrame:
    """Load multiple Parquet files and combine into one DataFrame."""
    dfs = []
    for year, paths in files.items():
        if isinstance(paths, list):  # if multiple parts (e.g. 2024 split)
            for path in paths:
                dfs.append(load_raw(path, year))
        else:
            dfs.append(load_raw(paths, year))
    return pd.concat(dfs, ignore_index=True)

def clean_data(raw: pd.DataFrame, year: int) -> pd.DataFrame:
    """Clean one year of raw data, keep both borrowings (A) and renewals (T)."""
    df = (
        raw.loc[
            (raw["Medientypcode"] != "Nicht bestellbar") &
            (raw["Medientypcode"] != "Nicht entleihbar"),
            RENAME_COLS.keys(),
        ]
        .rename(columns=RENAME_COLS)
    )

    for col in [
        "Media Type", "Gender", "Genre", "Age Group",
        "Target Group", "User Group", "Library"
    ]:
        df[col] = df[col].astype("category")

    df["Month"] = df["Month"].astype(int)

    df["Age Group"] = df["Age Group"].cat.rename_categories(
        lambda x: "80+" if x == "ab 80" else x
    )
    df["Age Group"] = pd.Categorical(df["Age Group"], categories=AGE_ORDER, ordered=True)

    df["Media Type"]   = df["Media Type"].cat.rename_categories(MEDIA_TYPE_TRANSLATION)
    df["Gender"]       = df["Gender"].cat.rename_categories(GENDER_TRANSLATION)
    df["Genre"]        = df["Genre"].cat.rename_categories(GENRE_TRANSLATION)
    df["Target Group"] = df["Target Group"].cat.rename_categories(TARGET_GROUP_TRANSLATION)
    df["User Group"]   = df["User Group"].cat.rename_categories(USER_GROUP_TRANSLATION)
    df["Library"]      = df["Library"].cat.rename_categories(LIBRARIES)

    df["Month"] = df["Month"].map(MONTH_NAME_MAP)
    df["Month"] = pd.Categorical(df["Month"], categories=MONTH_ORDER, ordered=True)

    df["Year"] = int(year)

    return df

def load_and_clean_multiple(files: dict) -> pd.DataFrame:
    """Load and clean multiple datasets, given {year: path(s)} mapping."""
    cleaned_multiple_years = []
    for year, paths in files.items():
        raws = []
        if isinstance(paths, list):
            raws = [load_raw(path, year) for path in paths]
        else:
            raws = [load_raw(paths, year)]
        raw = pd.concat(raws, ignore_index=True)
        cleaned = clean_data(raw, year)
        cleaned_multiple_years.append(cleaned)
    return pd.concat(cleaned_multiple_years, ignore_index=True)
