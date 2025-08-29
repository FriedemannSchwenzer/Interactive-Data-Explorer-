# app.py
import streamlit as st
import pandas as pd
import altair as alt
from data_loader import load_and_clean_multiple, AGE_ORDER
import elements as el


# --- File paths ---
files = {
    2022: "Pankow_2022.parquet",
    2024: [
        "Pankow_2024_part1.parquet",
        "Pankow_2024_part2.parquet"
    ],
}

# --- Page config ---
st.set_page_config(
    page_title="Pankow Libraries: Data Explorer",
    layout="wide"
)

# --- Title + Intro ---
st.markdown("<h1>Pankow Libraries: Interactive Data Explorer</h1>", unsafe_allow_html=True)

st.markdown(
    """
   Curious about what people take home from public libraries? Or who’s flocking to the libraries — and when shelves get the busiest? 
   Dive into this dashboard to explore borrowing data from the eight public libraries in Berlin’s Pankow district. 
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <p style='color:#6E6E6E; font-size:13px; margin-bottom:0px;'>
    Use the filters on the left to select or deselect years and libraries. 
    The data and charts update dynamically upon your selections!
    </p>
    """,
    unsafe_allow_html=True
)

# --- Seperation line --- 
st.markdown("---")

# --- Loading and caching data & spinner ---
@st.cache_data(show_spinner=False)
def cached_load_and_clean_multiple(files: dict) -> pd.DataFrame:
    return load_and_clean_multiple(files)

with st.spinner("Loading some exciting but heavy data from Pankow's libraries..."):
    cleaned_df = cached_load_and_clean_multiple(files)
    
    
# -------------------
# Sidebar & Filtering 
# -------------------

years, libraries = el.get_sidebar_options(cleaned_df)

years_selected = st.sidebar.multiselect(
    "Select year(s) to view:",
    options=years,
    default=years,
)

libraries_selected = st.sidebar.multiselect(
    "Select library/libraries to view:",
    options=libraries,
    default=libraries,
    label_visibility="visible",
    placeholder="Choose libraries...",
    key="library_multiselect",
    help="Pick one or more libraries to filter the data",
)

# --- Seperation line --- 
st.sidebar.markdown("---")

st.sidebar.markdown(
    "Please head over to the [Berlin Open Data Portal]"
    "(https://daten.berlin.de/datensaetze/ausleihen-in-offentlichen-bibliotheken-in-pankow-2022) "
    "to get more information about the datasets and download the raw files."
)

# Applying the filter 
df_filtered = cleaned_df[
    cleaned_df["Year"].isin(years_selected) &
    cleaned_df["Library"].isin(libraries_selected)
]




# --- KPI Layout, KPI and Dataframe imported from charts_lists_frames.py  ---
spacing, col_left, col_right = st.columns([0.1, 1, 5])

with col_left:
    num_libraries, total_borrowings, total_renewals = el.show_kpis(df_filtered)
    st.metric(" ", " ")
    st.metric("Libraries", f"{num_libraries}")
    st.metric("Borrowings", f"{total_borrowings:,}".replace(",", "."))
    st.metric("Renewals", f"{total_renewals:,}".replace(",", "."))

with col_right:
    # Subset borrowings
    df_display = (
        df_filtered[df_filtered["Type of Transaction"] == "A"]
        .dropna(subset=["Title"])
        .drop(columns=["Type of Transaction"], errors="ignore")
        .assign(Year=df_filtered["Year"].astype(str))
        .reset_index(drop=True)
    )

    # Take a random sample of up to 100 rows from the filtered set
    if len(df_display) > 100:
        df_display = df_display.sample(n=100, random_state=None)  # random_state=None -> new sample each rerun
    else:
        df_display = df_display.sample(frac=1, random_state=None)  # shuffle all if fewer than 100

    # Show the sampled dataframe
    st.dataframe(df_display)

    st.markdown(
        """
        <p style='color:#6E6E6E; font-size:13px; margin-top:8px;'>
        Displaying 100 randomly chosen borrowings (or all if fewer available).  
        The sample updates automatically based on your selections.  
        </p>
        """,
        unsafe_allow_html=True
    )


# --- Seperation line --- 
st.markdown("---")

# -------------------
# Input for Lists and Charts 
# -------------------

# --- Filtered subset for Borrowings only  ---
borrowings = df_filtered[df_filtered["Type of Transaction"] == "A"]

# --- Lists ---
books_list, dvds_list, cds_list, authors_list = el.make_lists(borrowings)

# --- Charts ---
media_chart   = el.make_media_chart(borrowings)
genre_chart   = el.make_genre_chart(borrowings)
target_chart  = el.make_target_chart(borrowings)
age_chart     = el.make_age_chart(borrowings)
user_chart    = el.make_user_chart(borrowings)
library_chart = el.make_library_chart(borrowings)
month_chart   = el.make_month_chart(borrowings)
gender_chart = el.make_gender_chart(borrowings)



# -------------------
# Row 1 → Demographics (who borrows?)
# -------------------
col4, space, col5, space, col6 = st.columns([1, 0.1, 1.5, 0.1, 1.5])

with col4:
    st.markdown(f"<div style='color:#363062; font-size:16px; font-weight:bold;'>Top 5 Authors ({el.format_years(years_selected)})</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='color:#6E6E6E; font-size:12px; margin-bottom:12px;'>{el.format_libraries(libraries_selected)}</div>", unsafe_allow_html=True)
    for author in authors_list:
        st.markdown(f"<p style='color:#363062; font-size:14px;'>{author}</p>", unsafe_allow_html=True)

with col5:
    st.markdown(f"<div style='color:#363062; font-size:16px; font-weight:bold;'>Borrowings by Target Group ({el.format_years(years_selected)})</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='color:#6E6E6E; font-size:12px; margin-bottom:12px;'>{el.format_libraries(libraries_selected)}</div>", unsafe_allow_html=True)
    st.altair_chart(target_chart, use_container_width=True)

with col6:
    st.markdown(f"<div style='color:#363062; font-size:16px; font-weight:bold;'>Borrowings by Gender ({el.format_years(years_selected)})</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='color:#6E6E6E; font-size:12px; margin-bottom:12px;'>{el.format_libraries(libraries_selected)}</div>", unsafe_allow_html=True)
    st.altair_chart(gender_chart, use_container_width=True)

st.markdown("---")




# -------------------
# Row 2 → Collection / Materials
# -------------------
col1, space,  col3, space, col2,= st.columns([1, 0.1, 1.5, 0.1, 1.5])

with col1:
    st.markdown(f"<div style='color:#363062; font-size:16px; font-weight:bold;'>Top 5 Books ({el.format_years(years_selected)})</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='color:#6E6E6E; font-size:12px; margin-bottom:12px;'>{el.format_libraries(libraries_selected)}</div>", unsafe_allow_html=True)
    for book in books_list:
        st.markdown(f"<p style='color:#363062; font-size:14px;'>{book}</p>", unsafe_allow_html=True)


with col3:
    st.markdown(f"<div style='color:#363062; font-size:16px; font-weight:bold;'>Borrowings by Genre ({el.format_years(years_selected)})</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='color:#6E6E6E; font-size:12px; margin-bottom:12px;'>{el.format_libraries(libraries_selected)}</div>", unsafe_allow_html=True)
    st.altair_chart(genre_chart, use_container_width=True)

with col2:
    st.markdown(f"<div style='color:#363062; font-size:16px; font-weight:bold;'>Borrowings by Media Type ({el.format_years(years_selected)})</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='color:#6E6E6E; font-size:12px; margin-bottom:12px;'>{el.format_libraries(libraries_selected)}</div>", unsafe_allow_html=True)
    st.altair_chart(media_chart, use_container_width=True)

    
st.markdown("---")




# -------------------
# Row 3 → Access / Formats
# -------------------
col7, space, col8, space, col9 = st.columns([1, 0.1, 1.5, 0.1, 1.5])

with col7:
    st.markdown(f"<div style='color:#363062; font-size:16px; font-weight:bold;'>Top 5 CDs ({el.format_years(years_selected)})</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='color:#6E6E6E; font-size:12px; margin-bottom:12px;'>{el.format_libraries(libraries_selected)}</div>", unsafe_allow_html=True)
    for cd in cds_list:
        st.markdown(f"<p style='color:#363062; font-size:14px;'>{cd}</p>", unsafe_allow_html=True)

with col8:
    st.markdown(f"<div style='color:#363062; font-size:16px; font-weight:bold;'>Borrowings by Age Group ({el.format_years(years_selected)})</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='color:#6E6E6E; font-size:12px; margin-bottom:12px;'>{el.format_libraries(libraries_selected)}</div>", unsafe_allow_html=True)
    st.altair_chart(age_chart, use_container_width=True)

with col9:
    st.markdown(f"<div style='color:#363062; font-size:16px; font-weight:bold;'>Borrowings by User Group ({el.format_years(years_selected)})</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='color:#6E6E6E; font-size:12px; margin-bottom:12px;'>{el.format_libraries(libraries_selected)}</div>", unsafe_allow_html=True)
    st.altair_chart(user_chart, use_container_width=True)

st.markdown("---")


# -------------------
# Row 4 → Place + Time
# -------------------
col10, space, col11, space, col12 = st.columns([1, 0.1, 1.5, 0.1, 1.5])

with col10:
    st.markdown(f"<div style='color:#363062; font-size:16px; font-weight:bold;'>Top 5 DVDs ({el.format_years(years_selected)})</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='color:#6E6E6E; font-size:12px; margin-bottom:12px;'>{el.format_libraries(libraries_selected)}</div>", unsafe_allow_html=True)
    for dvd in dvds_list:
        st.markdown(f"<p style='color:#363062; font-size:14px;'>{dvd}</p>", unsafe_allow_html=True)

with col11:
    st.markdown(f"<div style='color:#363062; font-size:16px; font-weight:bold;'>Borrowings by Library ({el.format_years(years_selected)})</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='color:#6E6E6E; font-size:12px; margin-bottom:12px;'>{el.format_libraries(libraries_selected)}</div>", unsafe_allow_html=True)
    st.altair_chart(library_chart, use_container_width=True)

with col12:
    st.markdown(f"<div style='color:#363062; font-size:16px; font-weight:bold;'>Borrowings by Month ({el.format_years(years_selected)})</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='color:#6E6E6E; font-size:12px; margin-bottom:12px;'>{el.format_libraries(libraries_selected)}</div>", unsafe_allow_html=True)
    st.altair_chart(month_chart, use_container_width=True)

st.markdown("---")
