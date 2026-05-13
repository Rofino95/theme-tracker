import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Track Record",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Signal Track Record")
st.caption("Historische Analyse der Signal-Performance.")

st.markdown("### Navigation")

nav1, nav2, nav3, nav4, nav5, nav6 = st.columns(6)

with nav1:
    st.page_link("app.py", label="Startseite", icon="🏠")

with nav2:
    st.page_link("pages/1_Aktien_Detail.py", label="Aktien-Detail", icon="📈")

with nav3:
    st.page_link("pages/2_Aktien_Ranking.py", label="Ranking", icon="🔎")

with nav4:
    st.page_link("pages/3_Top_Opportunities.py", label="Top Opportunities", icon="🔥")

with nav5:
    st.page_link("pages/4_Erklaerungen.py", label="Erklaerungen", icon="ℹ️")

with nav6:
    st.page_link("pages/5_Track_Record.py", label="Track Record", icon="📊")

st.markdown("---")

HISTORY_FILE = "signal_history.csv"

if not os.path.exists(HISTORY_FILE):
    st.warning("signal_history.csv wurde nicht gefunden.")
    st.stop()

df = pd.read_csv(HISTORY_FILE)

if "Preis" not in df.columns and "Entry Price" in df.columns:
    df = df.rename(columns={"Entry Price": "Preis"})

if len(df) == 0:
    st.warning("Noch keine historischen Daten vorhanden.")
    st.stop()

df["Date"] = pd.to_datetime(df["Date"])

df = df.sort_values(by=["Ticker", "Date"])

# -------------------------
# Future Returns berechnen
# -------------------------

df["Future Price 30D"] = df.groupby("Ticker")["Preis"].shift(-30)
df["Future Price 90D"] = df.groupby("Ticker")["Preis"].shift(-90)

df["Return 30D"] = (
    (df["Future Price 30D"] - df["Preis"]) / df["Preis"]
)

df["Return 90D"] = (
    (df["Future Price 90D"] - df["Preis"]) / df["Preis"]
)

# -------------------------
# Kennzahlen
# -------------------------

valid_30d = df["Return 30D"].dropna()
valid_90d = df["Return 90D"].dropna()

avg_30d = valid_30d.mean() if len(valid_30d) > 0 else None
avg_90d = valid_90d.mean() if len(valid_90d) > 0 else None

hitrate_30d = (
    (valid_30d > 0).mean() * 100
    if len(valid_30d) > 0 else None
)

hitrate_90d = (
    (valid_90d > 0).mean() * 100
    if len(valid_90d) > 0 else None
)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

kpi1.metric(
    "Ø Return 30D",
    f"{avg_30d:.1%}" if avg_30d is not None else "n/a"
)

kpi2.metric(
    "Trefferquote 30D",
    f"{hitrate_30d:.0f}%" if hitrate_30d is not None else "n/a"
)

kpi3.metric(
    "Ø Return 90D",
    f"{avg_90d:.1%}" if avg_90d is not None else "n/a"
)

kpi4.metric(
    "Trefferquote 90D",
    f"{hitrate_90d:.0f}%" if hitrate_90d is not None else "n/a"
)

st.markdown("---")

# -------------------------
# Beste Signale
# -------------------------

st.markdown("## 🚀 Beste historische Signale")

best_df = (
    df.dropna(subset=["Return 30D"])
    .sort_values(by="Return 30D", ascending=False)
    .head(20)
)

st.dataframe(
    best_df[[
        "Date",
        "Name",
        "Ticker",
        "Trend Score",
        "3M Momentum",
        "Entry Score",
        "Short Score",
        "Return 30D"
    ]].style.format({
        "Trend Score": "{:.2f}",
        "3M Momentum": "{:.1%}",
        "Return 30D": "{:.1%}"
    }),
    use_container_width=True,
    hide_index=True
)

st.markdown("---")

# -------------------------
# Schlechteste Signale
# -------------------------

st.markdown("## 🔴 Schlechteste historische Signale")

worst_df = (
    df.dropna(subset=["Return 30D"])
    .sort_values(by="Return 30D", ascending=True)
    .head(20)
)

st.dataframe(
    worst_df[[
        "Date",
        "Name",
        "Ticker",
        "Trend Score",
        "3M Momentum",
        "Entry Score",
        "Short Score",
        "Return 30D"
    ]].style.format({
        "Trend Score": "{:.2f}",
        "3M Momentum": "{:.1%}",
        "Return 30D": "{:.1%}"
    }),
    use_container_width=True,
    hide_index=True
)

st.markdown("---")

st.info(
    """
Die Track-Record-Seite analysiert historische Signale rückwirkend.

30D Return:
→ Entwicklung ca. 1 Monat nach Signal

90D Return:
→ Entwicklung ca. 3 Monate nach Signal

Die Qualität der Auswertung verbessert sich automatisch,
je länger signal_history.csv Daten sammelt.
"""
)
