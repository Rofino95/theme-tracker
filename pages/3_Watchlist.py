import os
import json
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Watchlist", layout="wide")

WATCHLIST_FILE = "watchlist.json"

def load_watchlist():
    try:
        with open(WATCHLIST_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_watchlist(watchlist):
    with open(WATCHLIST_FILE, "w") as f:
        json.dump(watchlist, f)

st.title("⭐ Watchlist")

if not os.path.exists("theme_scores.csv"):
    st.warning("theme_scores.csv fehlt")
    st.stop()

df = pd.read_csv("theme_scores.csv")

watchlist = load_watchlist()

if len(watchlist) == 0:
    st.info("Watchlist ist leer")
    st.stop()

watch_df = df[df["Ticker"].isin(watchlist)].copy()

st.dataframe(
    watch_df[[
        "Name",
        "Ticker",
        "Preis",
        "Trend Score",
        "Momentum"
    ]],
    use_container_width=True,
    hide_index=True
)

st.markdown("### Zur Aktien-Detailseite")

detail_options = watch_df[["Name", "Ticker"]].drop_duplicates().copy()
detail_options["Label"] = detail_options["Name"] + " (" + detail_options["Ticker"] + ")"

selected_detail = st.selectbox(
    "Aktie fuer Detailansicht auswaehlen",
    detail_options["Label"].tolist(),
    key="watchlist_detail_select"
)

selected_detail_ticker = detail_options.loc[
    detail_options["Label"] == selected_detail, "Ticker"
].iloc[0]

st.page_link(
    "pages/1_Aktien_Detail.py",
    label=f"Zur Detailseite von {selected_detail}",
    icon="📈",
    query_params={"ticker": selected_detail_ticker}
)

st.markdown("### Entfernen")

remove_options = watch_df["Name"] + " (" + watch_df["Ticker"] + ")"

selected_remove = st.selectbox(
    "Aktie entfernen",
    remove_options.tolist()
)

remove_ticker = watch_df.loc[
    remove_options == selected_remove, "Ticker"
].iloc[0]

if st.button("Entfernen ❌"):
    watchlist = [t for t in watchlist if t != remove_ticker]
    save_watchlist(watchlist)
    st.success("Entfernt")
    st.rerun()
