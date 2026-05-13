import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Track Record",
    page_icon="assets/logo.png",
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

if len(df) == 0:
    st.warning("Noch keine historischen Daten vorhanden.")
    st.stop()

# Alte Spaltennamen abfangen
rename_map = {
    "Entry Price": "Preis",
    "Range Momentum": "Momentum"
}

df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns and v not in df.columns})

required = ["Date", "Ticker", "Preis"]

missing = [col for col in required if col not in df.columns]

if missing:
    st.error(f"Diese Pflichtspalten fehlen in signal_history.csv: {missing}")
    st.stop()

df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values(by=["Ticker", "Date"])

# Zahlen sicher konvertieren
numeric_cols = [
    "Preis",
    "Trend Score",
    "Momentum",
    "3M Momentum",
    "Entry Score",
    "Short Score",
    "Long Score",
    "Early Score",
    "Fundamental Score"
]

for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Future Returns berechnen
df["Future Price 30D"] = df.groupby("Ticker")["Preis"].shift(-30)
df["Future Price 90D"] = df.groupby("Ticker")["Preis"].shift(-90)

df["Return 30D"] = (df["Future Price 30D"] - df["Preis"]) / df["Preis"]
df["Return 90D"] = (df["Future Price 90D"] - df["Preis"]) / df["Preis"]

valid_30d = df["Return 30D"].dropna()
valid_90d = df["Return 90D"].dropna()

avg_30d = valid_30d.mean() if len(valid_30d) > 0 else None
avg_90d = valid_90d.mean() if len(valid_90d) > 0 else None

hitrate_30d = (valid_30d > 0).mean() * 100 if len(valid_30d) > 0 else None
hitrate_90d = (valid_90d > 0).mean() * 100 if len(valid_90d) > 0 else None

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

kpi1.metric("Ø Return 30D", f"{avg_30d:.1%}" if avg_30d is not None else "n/a")
kpi2.metric("Trefferquote 30D", f"{hitrate_30d:.0f}%" if hitrate_30d is not None else "n/a")
kpi3.metric("Ø Return 90D", f"{avg_90d:.1%}" if avg_90d is not None else "n/a")
kpi4.metric("Trefferquote 90D", f"{hitrate_90d:.0f}%" if hitrate_90d is not None else "n/a")

st.caption("Hinweis: Aussagekräftige 30D/90D-Werte entstehen erst, wenn signal_history.csv über längere Zeit Daten gesammelt hat.")

st.markdown("---")

# Filter
filter_col1, filter_col2 = st.columns(2)

with filter_col1:
    if "Signal Type" in df.columns:
        selected_signal_type = st.selectbox(
            "Signal-Typ",
            ["Alle"] + sorted(df["Signal Type"].dropna().unique().tolist())
        )
    else:
        selected_signal_type = "Alle"

with filter_col2:
    min_date = df["Date"].min()
    max_date = df["Date"].max()
    selected_range = st.date_input(
        "Zeitraum",
        value=(min_date, max_date)
    )

filtered_df = df.copy()

if "Signal Type" in filtered_df.columns and selected_signal_type != "Alle":
    filtered_df = filtered_df[filtered_df["Signal Type"] == selected_signal_type]

if isinstance(selected_range, tuple) and len(selected_range) == 2:
    start_date = pd.to_datetime(selected_range[0])
    end_date = pd.to_datetime(selected_range[1])
    filtered_df = filtered_df[
        (filtered_df["Date"] >= start_date) &
        (filtered_df["Date"] <= end_date)
    ]

# Hilfsfunktion für sichere Tabellen
def safe_columns(dataframe, wanted_cols):
    return [col for col in wanted_cols if col in dataframe.columns]


def show_table(title, data, sort_col, ascending):
    st.markdown(title)

    base_cols = [
        "Date",
        "Name",
        "Ticker",
        "Signal Type",
        "Rank",
        "Trend Score",
        "3M Momentum",
        "Entry Score",
        "Short Score",
        "Long Score",
        "Early Score",
        "Return 30D",
        "Return 90D"
    ]

    cols = safe_columns(data, base_cols)

    if sort_col not in data.columns or len(data.dropna(subset=[sort_col])) == 0:
        st.info("Noch nicht genug Daten für diese Auswertung.")
        return

    table_df = (
        data.dropna(subset=[sort_col])
        .sort_values(by=sort_col, ascending=ascending)
        .head(20)
    )

    format_dict = {}

    for col in ["Trend Score", "Entry Score", "Short Score", "Long Score", "Early Score"]:
        if col in cols:
            format_dict[col] = "{:.2f}"

    for col in ["3M Momentum", "Return 30D", "Return 90D"]:
        if col in cols:
            format_dict[col] = "{:.1%}"

    st.dataframe(
        table_df[cols].style.format(format_dict),
        use_container_width=True,
        hide_index=True
    )


show_table("## 🚀 Beste historische Signale 30D", filtered_df, "Return 30D", False)
st.markdown("---")
show_table("## 🔴 Schlechteste historische Signale 30D", filtered_df, "Return 30D", True)
st.markdown("---")
show_table("## 📈 Beste historische Signale 90D", filtered_df, "Return 90D", False)
st.markdown("---")
show_table("## 📉 Schlechteste historische Signale 90D", filtered_df, "Return 90D", True)

st.markdown("---")

with st.expander("Rohdaten anzeigen"):
    st.dataframe(
        filtered_df.sort_values(by="Date", ascending=False),
        use_container_width=True,
        hide_index=True
    )
