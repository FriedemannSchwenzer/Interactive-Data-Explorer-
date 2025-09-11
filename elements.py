# elements.py
iimport pandas as pd
import altair as alt
from data_loader import load_and_clean_multiple, AGE_ORDER

###sidebar options 

def get_sidebar_options(cleaned_df: pd.DataFrame):
    """Prepare sidebar options for years and libraries."""
    years = sorted(cleaned_df["Year"].unique().tolist())
    libraries = sorted(cleaned_df["Library"].dropna().unique().tolist())
    return years, libraries



## Number of total Libraries, Borrowings and Renewals 

def show_kpis(df_filtered):
    """Return KPI values (libraries, borrowings, renewals)."""
    total_borrowings = (df_filtered["Type of Transaction"] == "A").sum()
    total_renewals   = (df_filtered["Type of Transaction"] == "T").sum()
    num_libraries    = df_filtered["Library"].nunique()
    return num_libraries, total_borrowings, total_renewals


def show_dataframe(df_filtered):
    """Render cleaned borrowings dataframe."""
    st.dataframe(
        df_filtered[df_filtered["Type of Transaction"] == "A"]
        .dropna(subset=["Title"])
        .drop(columns=["Type of Transaction"], errors="ignore")
        .assign(Year=df_filtered["Year"].astype(str))
        .reset_index(drop=True)
    )

    
# --- Helper functions ---
def format_year(year: int) -> str:
    return str(year)


def format_libraries(libraries: list, max_display: int = 2) -> str:
    if not libraries:
        return "No libraries selected"
    if len(libraries) <= max_display:
        return ", ".join(libraries)
    return ", ".join(libraries[:max_display]) + f" … +{len(libraries) - max_display} more"

def normalize_author(name: str) -> str:
    if "," in name:
        parts = [p.strip() for p in name.split(",", 1)]
        return f"{parts[1]} {parts[0]}"
    return name.strip()




# --- Top items by media ---
def top_items_by_media(df, media_type, n=5):
    filtered = df[df["Media Type"] == media_type]
    counts = (
        filtered.groupby(["Title", "Author"], observed=True)
        .size()
        .reset_index(name="Borrow Count")
    )
    return counts.sort_values("Borrow Count", ascending=False).head(n)

def make_lists(borrowings_valid):
    """Return top books, dvds, cds, authors as lists of strings."""
    books = [row["Title"] for _, row in top_items_by_media(borrowings_valid, "Book").iterrows()]
    dvds  = [row["Title"] for _, row in top_items_by_media(borrowings_valid, "DVD").iterrows()]
    cds   = [row["Title"] for _, row in top_items_by_media(borrowings_valid, "CD").iterrows()]

    author_counts = (
        borrowings_valid.groupby("Author", observed=True)
        .size()
        .reset_index(name="Borrow Count")
    )
    top_authors = author_counts.sort_values("Borrow Count", ascending=False).head(5)
    authors = [normalize_author(row["Author"]) for _, row in top_authors.iterrows()]

    return books, dvds, cds, authors




def make_bar_chart(df, category_field, color="#363062", sort="-y", height=300, width=300, order=None):
    """Standard vertical bar chart showing relative frequencies."""
    df = df.copy()
    df["Relative"] = df["Count"] / df["Count"].sum()

    return (
        alt.Chart(df)
        .mark_bar(color=color)
        .encode(
            x=alt.X(category_field,
                    type="nominal",
                    sort=order or sort,
                    title=None,
                    axis=alt.Axis(labelColor="#363062")),
            y=alt.Y("Relative",
                    type="quantitative",
                    axis=alt.Axis(format="%", title=None, labelColor="#363062"),
                    scale=alt.Scale(domain=[0, 1])),
            tooltip=[
                alt.Tooltip(category_field, title=category_field),
                alt.Tooltip("Relative", format=".1%", title="Relative (%)"),
                alt.Tooltip("Count", title="Absolute Borrowings")
            ]
        )
        .properties(height=height, width=width)
    )


def make_horizontal_bar_chart(df, category_field, color="#363062", sort="-x", height=300, width=300, order=None):
    """Horizontal bar chart showing relative frequencies."""
    df = df.copy()
    df["Relative"] = df["Count"] / df["Count"].sum()

    return (
        alt.Chart(df)
        .mark_bar(color=color)
        .encode(
            y=alt.Y(category_field,
                    type="nominal",
                    sort=order or sort,
                    title=None,
                    axis=alt.Axis(labelColor="#363062")),
            x=alt.X("Relative",
                    type="quantitative",
                    axis=alt.Axis(format="%", title=None, labelColor="#363062"),
                    scale=alt.Scale(domain=[0, 1])),
            tooltip=[
                alt.Tooltip(category_field, title=category_field),
                alt.Tooltip("Relative", type="quantitative", format=".1%", title="Relative (%)"),
                alt.Tooltip("Count", type="quantitative", title="Absolute")
            ]
        )
        .properties(height=height, width=width)
    )



def make_pie_chart(
    df, 
    category_field, 
    value_field="Count", 
    height=300, 
    width=300, 
    colors=["#363062", "#4A90E2","#E94F37"]
):
    """Pie chart showing relative frequencies with absolute counts in tooltip and custom colors."""
    df = df.copy()
    df["Relative"] = df[value_field] / df[value_field].sum()

    return (
        alt.Chart(df)
        .mark_arc()
        .encode(
            theta=alt.Theta("Relative", type="quantitative", stack=True),
            color=alt.Color(
                category_field,
                type="nominal",
                legend=alt.Legend(title=category_field),
                scale=alt.Scale(range=colors)  # 🎨 custom colors
            ),
            tooltip=[
                alt.Tooltip(category_field, title=category_field),
                alt.Tooltip("Relative", type="quantitative", format=".1%", title="Relative (%)"),
                alt.Tooltip(value_field, type="quantitative", title="Absolute")
            ]
        )
        .properties(height=height, width=width)
    )


def make_line_chart(df, x_field="Month", y_field="Count", height=300, width=500):
    """Line chart for monthly data with white dots, absolute values on y-axis, and relative % in tooltip."""
    month_order = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    df = df.copy()
    df["Relative"] = df[y_field] / df[y_field].sum()

    base = alt.Chart(df).encode(
        x=alt.X(x_field, type="nominal", sort=month_order,
                title=None, axis=alt.Axis(labelColor="#363062")),
        y=alt.Y(y_field, type="quantitative",
                title=None, axis=alt.Axis(labelColor="#363062")),
        tooltip=[
            alt.Tooltip(x_field, title="Month"),
            alt.Tooltip(y_field, type="quantitative", title="Absolute Borrowings"),
            alt.Tooltip("Relative", type="quantitative", format=".1%", title="Relative (%)"),
        ]
    )

    line = base.mark_line(color="#363062")
    points = base.mark_point(color="#FFFFFF", size=60, stroke="#363062", strokeWidth=0.5)

    return (line + points).properties(height=height, width=width)




def make_media_chart(borrowings):
    df = borrowings.groupby("Media Type", observed=True).size().reset_index(name="Count")
    return make_horizontal_bar_chart(df, "Media Type")

def make_genre_chart(borrowings):
    df = borrowings.groupby("Genre", observed=True).size().reset_index(name="Count")
    return make_horizontal_bar_chart(df, "Genre")

def make_target_chart(borrowings):
    df = borrowings.groupby("Target Group", observed=True).size().reset_index(name="Count")
    return make_horizontal_bar_chart(df, "Target Group")

def make_gender_chart(borrowings):
    df = borrowings.groupby("Gender", observed=True).size().reset_index(name="Count")
    return make_horizontal_bar_chart(df, "Gender")

def make_age_chart(borrowings):
    df = borrowings.groupby("Age Group", observed=True).size().reset_index(name="Count")
    return make_bar_chart(df, "Age Group", order=AGE_ORDER)

def make_user_chart(borrowings):
    df = borrowings.groupby("User Group", observed=True).size().reset_index(name="Count")
    return make_horizontal_bar_chart(df, "User Group")

def make_library_chart(borrowings):
    df = borrowings.groupby("Library", observed=True).size().reset_index(name="Count")
    return make_horizontal_bar_chart(df, "Library")

def make_month_chart(borrowings):
    df = borrowings.groupby("Month", observed=True).size().reset_index(name="Count")
    return make_line_chart(df, "Month")
