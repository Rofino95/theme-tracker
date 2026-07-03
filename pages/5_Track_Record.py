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
CURRENT_FILE = "theme_scores.csv"


def safe_columns(dataframe, wanted_cols):
    return [col for col in wanted_cols if col in dataframe.columns]


def normalize_history_columns(dataframe):
    rename_map = {
        "Entry Price": "Preis",
        "Range Momentum": "Momentum",
        "Signal": "Signal Type",
        "Signal_Type": "Signal Type",
        "Rank im Theme": "Rank"
    }

    dataframe = dataframe.rename(
        columns={
            old: new
            for old, new in rename_map.items()
            if old in dataframe.columns and new not in dataframe.columns
        }
    )

    return dataframe


def get_price_at_or_after(group, target_date):
    future_rows = group[group["Date"] >= target_date]

    if future_rows.empty:
        return None

    return future_rows.iloc[0]["Preis"]


def calculate_forward_returns(dataframe):
    rows = []

    for ticker, group in dataframe.groupby("Ticker"):
        group = group.sort_values("Date").copy()

        for _, row in group.iterrows():
            signal_date = row["Date"]

            price_30d = get_price_at_or_after(
                group,
                signal_date + pd.Timedelta(days=30)
            )

            price_90d = get_price_at_or_after(
                group,
                signal_date + pd.Timedelta(days=90)
            )

            rows.append({
                "Index": row.name,
                "Future Price 30D": price_30d,
                "Future Price 90D": price_90d
            })

    result = pd.DataFrame(rows)

    if result.empty:
        dataframe["Future Price 30D"] = None
        dataframe["Future Price 90D"] = None
        dataframe["Return 30D"] = None
        dataframe["Return 90D"] = None
        return dataframe

    dataframe = dataframe.merge(
        result,
        left_index=True,
        right_on="Index",
        how="left"
    ).drop(columns=["Index"])

    dataframe["Return 30D"] = (
        dataframe["Future Price 30D"] - dataframe["Preis"]
    ) / dataframe["Preis"]

    dataframe["Return 90D"] = (
        dataframe["Future Price 90D"] - dataframe["Preis"]
    ) / dataframe["Preis"]

    return dataframe


def get_signal_status(days_since_signal, current_return):
    if pd.isna(current_return):
        return "Unklar"

    if days_since_signal < 7:
        return "Zu früh"

    if days_since_signal < 30:
        if current_return > 0.05:
            return "Früh positiv"
        elif current_return < -0.05:
            return "Früh negativ"
        else:
            return "Offen"

    if current_return > 0.10:
        return "Treffer"

    if current_return < -0.10:
        return "Fehlsignal"

    return "Neutral"


def format_percent(value):
    if pd.notna(value):
        return f"{value:.1%}"
    return "n/a"


def show_table(title, data, sort_col, ascending):
    st.markdown(title)

    if sort_col not in data.columns:
        st.info("Diese Auswertung ist noch nicht verfügbar.")
        return

    if len(data.dropna(subset=[sort_col])) == 0:
        st.info("Noch nicht genug historische Daten für diese Auswertung.")
        return

    base_cols = [
        "Date",
        "Name",
        "Ticker",
        "Signal Type",
        "Rank",
        "Preis",
        "Current Price",
        "Current Return",
        "Days Since Signal",
        "Signal Status",
        "Trend Score",
        "3M Momentum",
        "1M Momentum",
        "20D Momentum",
        "Momentum Risiko",
        "Entry Score",
        "Short Score",
        "Long Score",
        "Early Score",
        "Return 30D",
        "Return 90D"
    ]

    cols = safe_columns(data, base_cols)

    table_df = (
        data.dropna(subset=[sort_col])
        .sort_values(by=sort_col, ascending=ascending)
        .head(20)
        .copy()
    )

    format_dict = {}

    for col in [
        "Preis",
        "Current Price",
        "Trend Score",
        "Entry Score",
        "Short Score",
        "Long Score",
        "Early Score"
    ]:
        if col in cols:
            format_dict[col] = "{:.2f}"

    for col in [
        "3M Momentum",
        "1M Momentum",
        "20D Momentum",
        "Current Return",
        "Return 30D",
        "Return 90D"
    ]:
        if col in cols:
            format_dict[col] = "{:.1%}"

    st.dataframe(
        table_df[cols].style.format(format_dict),
        use_container_width=True,
        hide_index=True
    )


if not os.path.exists(HISTORY_FILE):
    st.warning("signal_history.csv wurde nicht gefunden.")
    st.stop()

df = pd.read_csv(HISTORY_FILE)

if len(df) == 0:
    st.warning("Noch keine historischen Daten vorhanden.")
    st.stop()

df = normalize_history_columns(df)

required = ["Date", "Ticker", "Preis"]
missing = [col for col in required if col not in df.columns]

if missing:
    st.error(f"Diese Pflichtspalten fehlen in signal_history.csv: {missing}")
    st.stop()

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.dropna(subset=["Date", "Ticker", "Preis"]).copy()

df["Signal Date"] = df["Date"].dt.date

# Mehrfach-Snapshots am selben Tag reduzieren.
dedupe_cols = ["Signal Date", "Ticker"]

if "Signal Type" in df.columns:
    dedupe_cols.append("Signal Type")

df = (
    df.sort_values(by="Date")
    .drop_duplicates(subset=dedupe_cols, keep="first")
    .copy()
)

numeric_cols = [
    "Preis",
    "Trend Score",
    "Momentum",
    "3M Momentum",
    "1M Momentum",
    "20D Momentum",
    "MA50 Abstand",
    "Volume Ratio",
    "Entry Score",
    "Short Score",
    "Long Score",
    "Early Score",
    "Fundamental Score",
    "Rank"
]

for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.sort_values(by=["Ticker", "Date"]).copy()

# Historische 30D/90D Returns nur anhand echter Datumsabstände berechnen.
df = calculate_forward_returns(df)

latest_prices = None

if os.path.exists(CURRENT_FILE):
    current_df = pd.read_csv(CURRENT_FILE)

    if {"Ticker", "Preis"}.issubset(current_df.columns):
        latest_prices = (
            current_df[["Ticker", "Preis"]]
            .dropna()
            .drop_duplicates(subset=["Ticker"], keep="last")
            .rename(columns={"Preis": "Current Price"})
        )

if latest_prices is not None:
    df = df.merge(latest_prices, on="Ticker", how="left")
else:
    latest_from_history = (
        df.sort_values("Date")
        .groupby("Ticker", as_index=False)
        .tail(1)[["Ticker", "Preis"]]
        .rename(columns={"Preis": "Current Price"})
    )

    df = df.merge(latest_from_history, on="Ticker", how="left")

df["Current Return"] = (df["Current Price"] - df["Preis"]) / df["Preis"]

today = pd.Timestamp.today().normalize()
df["Days Since Signal"] = (today - df["Date"].dt.normalize()).dt.days

df["Signal Status"] = df.apply(
    lambda row: get_signal_status(
        row["Days Since Signal"],
        row["Current Return"]
    ),
    axis=1
)

st.info(
    """
Der Track Record bewertet historische Signale erst sinnvoll, wenn genug Zeit vergangen ist.  
30D und 90D werden jetzt über echte Datumsabstände berechnet, nicht einfach über 30 oder 90 Tabellenzeilen.
"""
)

# KPIs
valid_30d = df["Return 30D"].dropna()
valid_90d = df["Return 90D"].dropna()

avg_30d = valid_30d.mean() if len(valid_30d) > 0 else None
avg_90d = valid_90d.mean() if len(valid_90d) > 0 else None

hitrate_30d = (valid_30d > 0).mean() * 100 if len(valid_30d) > 0 else None
hitrate_90d = (valid_90d > 0).mean() * 100 if len(valid_90d) > 0 else None

open_signals = int((df["Days Since Signal"] < 30).sum())
matured_30d = int(df["Return 30D"].notna().sum())
matured_90d = int(df["Return 90D"].notna().sum())

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

kpi1.metric("Ø Return 30D", format_percent(avg_30d))
kpi2.metric("Trefferquote 30D", f"{hitrate_30d:.0f}%" if hitrate_30d is not None else "n/a")
kpi3.metric("Ø Return 90D", format_percent(avg_90d))
kpi4.metric("Trefferquote 90D", f"{hitrate_90d:.0f}%" if hitrate_90d is not None else "n/a")

kpi5, kpi6, kpi7, kpi8 = st.columns(4)

kpi5.metric("Signale gesamt", len(df))
kpi6.metric("Offen <30D", open_signals)
kpi7.metric("Auswertbar 30D", matured_30d)
kpi8.metric("Auswertbar 90D", matured_90d)

st.caption("Je mehr Tage signal_history.csv gesammelt hat, desto aussagekräftiger wird diese Seite.")

st.markdown("---")

# Filter
filter_col1, filter_col2, filter_col3 = st.columns(3)

with filter_col1:
    if "Signal Type" in df.columns:
        selected_signal_type = st.selectbox(
            "Signal-Typ",
            ["Alle"] + sorted(df["Signal Type"].dropna().unique().tolist())
        )
    else:
        selected_signal_type = "Alle"

with filter_col2:
    selected_status = st.selectbox(
        "Signal Status",
        ["Alle"] + sorted(df["Signal Status"].dropna().unique().tolist())
    )

with filter_col3:
    only_matured = st.checkbox("Nur Signale mit 30D-Auswertung", value=False)

filter_col4, filter_col5 = st.columns(2)

with filter_col4:
    min_date = df["Date"].min().date()
    max_date = df["Date"].max().date()
    selected_range = st.date_input(
        "Zeitraum",
        value=(min_date, max_date)
    )

with filter_col5:
    selected_ticker = st.selectbox(
        "Ticker",
        ["Alle"] + sorted(df["Ticker"].dropna().unique().tolist())
    )

filtered_df = df.copy()

if "Signal Type" in filtered_df.columns and selected_signal_type != "Alle":
    filtered_df = filtered_df[filtered_df["Signal Type"] == selected_signal_type]

if selected_status != "Alle":
    filtered_df = filtered_df[filtered_df["Signal Status"] == selected_status]

if only_matured:
    filtered_df = filtered_df[filtered_df["Return 30D"].notna()]

if selected_ticker != "Alle":
    filtered_df = filtered_df[filtered_df["Ticker"] == selected_ticker]

if isinstance(selected_range, tuple) and len(selected_range) == 2:
    start_date = pd.to_datetime(selected_range[0])
    end_date = pd.to_datetime(selected_range[1])
    filtered_df = filtered_df[
        (filtered_df["Date"] >= start_date)
        & (filtered_df["Date"] <= end_date)
    ]

st.markdown("## Aktuelle offene Signale")

open_cols = [
    "Date",
    "Name",
    "Ticker",
    "Signal Type",
    "Preis",
    "Current Price",
    "Current Return",
    "Days Since Signal",
    "Signal Status",
    "Entry Score",
    "Momentum Risiko"
]

open_table_cols = safe_columns(filtered_df, open_cols)

open_df = (
    filtered_df
    .sort_values(by="Date", ascending=False)
    .head(30)
)

format_open = {}

for col in ["Preis", "Current Price", "Entry Score"]:
    if col in open_table_cols:
        format_open[col] = "{:.2f}"

if "Current Return" in open_table_cols:
    format_open["Current Return"] = "{:.1%}"

st.dataframe(
    open_df[open_table_cols].style.format(format_open),
    use_container_width=True,
    hide_index=True
)

st.markdown("---")

show_table("## 🚀 Beste historische Signale 30D", filtered_df, "Return 30D", False)
st.markdown("---")
show_table("## 🔴 Schlechteste historische Signale 30D", filtered_df, "Return 30D", True)
st.markdown("---")
show_table("## 📈 Beste historische Signale 90D", filtered_df, "Return 90D", False)
st.markdown("---")
show_table("## 📉 Schlechteste historische Signale 90D", filtered_df, "Return 90D", True)

st.markdown("---")

st.markdown("## Auswertung nach Signal-Typ")

if "Signal Type" in filtered_df.columns:
    signal_summary = (
        filtered_df
        .groupby("Signal Type", as_index=False)
        .agg(
            Anzahl=("Ticker", "count"),
            Avg_Current_Return=("Current Return", "mean"),
            Avg_Return_30D=("Return 30D", "mean"),
            Trefferquote_30D=("Return 30D", lambda x: (x.dropna() > 0).mean() * 100 if len(x.dropna()) > 0 else None),
            Avg_Return_90D=("Return 90D", "mean"),
            Trefferquote_90D=("Return 90D", lambda x: (x.dropna() > 0).mean() * 100 if len(x.dropna()) > 0 else None)
        )
        .sort_values(by="Avg_Current_Return", ascending=False)
    )

    st.dataframe(
        signal_summary.style.format({
            "Avg_Current_Return": "{:.1%}",
            "Avg_Return_30D": "{:.1%}",
            "Trefferquote_30D": "{:.0f}%",
            "Avg_Return_90D": "{:.1%}",
            "Trefferquote_90D": "{:.0f}%"
        }),
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("Keine Spalte 'Signal Type' vorhanden.")

st.markdown("---")

with st.expander("Rohdaten anzeigen"):
    raw_cols = [
        "Date",
        "Name",
        "Ticker",
        "Signal Type",
        "Preis",
        "Current Price",
        "Current Return",
        "Days Since Signal",
        "Signal Status",
        "Trend Score",
        "3M Momentum",
        "1M Momentum",
        "20D Momentum",
        "Momentum Risiko",
        "Entry Score",
        "Short Score",
        "Long Score",
        "Early Score",
        "Return 30D",
        "Return 90D"
    ]

    cols = safe_columns(filtered_df, raw_cols)

    st.dataframe(
        filtered_df[cols].sort_values(by="Date", ascending=False),
        use_container_width=True,
        hide_index=True
    )
