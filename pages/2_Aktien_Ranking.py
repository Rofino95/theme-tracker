import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Aktien Ranking", layout="wide")


def get_status(score):
    if score > 0.7:
        return "Bullisch"
    elif score > 0.5:
        return "Neutral"
    else:
        return "Baerisch"


def get_signal(stock_score, stock_momentum, theme_status, theme_bullish_pct):
    if stock_score < 0.35 and stock_momentum < -0.20 and theme_status == "Baerisch":
        return "Avoid"
    if stock_score > 0.85 and stock_momentum < 0.30:
        return "Take Profits"
    if 0.60 <= stock_score <= 0.85 and stock_momentum > 0 and theme_status in ["Bullisch", "Neutral"] and theme_bullish_pct >= 50:
        return "Attraktiv"
    if stock_score > 0.85 and stock_momentum >= 0.30:
        return "Hold"
    if stock_score >= 0.50 and stock_momentum >= -0.10 and theme_status != "Baerisch":
        return "Hold"
    return "Review"


def get_trend_phase(stock_score, stock_momentum):
    if stock_score < 0.35 and stock_momentum < -0.20:
        return "Weak"
    elif stock_score > 0.85 and stock_momentum < 0.30:
        return "Late Trend"
    elif stock_score > 0.75 and stock_momentum >= 0.30:
        return "Mid Trend"
    elif 0.55 <= stock_score <= 0.75 and stock_momentum > 0:
        return "Early Trend"
    else:
        return "Transition"


def get_zone(price, low_52, high_52):
    range_52 = high_52 - low_52

    weak_zone_max = low_52 + 0.35 * range_52
    watchlist_zone_min = low_52 + 0.55 * range_52
    watchlist_zone_max = low_52 + 0.70 * range_52
    hold_zone_min = low_52 + 0.70 * range_52
    hold_zone_max = low_52 + 0.85 * range_52
    upper_range_min = low_52 + 0.85 * range_52

    if price < weak_zone_max:
        return "Weak Zone"
    elif weak_zone_max <= price < watchlist_zone_min:
        return "Transition Zone"
    elif watchlist_zone_min <= price < hold_zone_min:
        return "Watchlist Zone"
    elif hold_zone_min <= price < upper_range_min:
        return "Hold Zone"
    else:
        return "Upper Range"


def get_entry_quality(zone, trend_direction, momentum):
    if zone in ["Watchlist Zone", "Transition Zone"] and momentum > 0 and trend_direction in ["Turnaround moeglich", "Frischer Aufwaertstrend"]:
        return "Sehr gut"
    elif zone == "Hold Zone" and momentum > 0:
        return "Gut"
    elif zone == "Upper Range":
        return "Zu spaet"
    elif zone == "Weak Zone":
        return "Riskant"
    else:
        return "Neutral"


def get_exit_signal(zone, momentum, trend_direction):
    if zone == "Upper Range" and momentum < 0.30:
        return "Gewinne sichern"
    elif trend_direction == "Trend schwaecht sich ab":
        return "Vorsicht"
    else:
        return "Hold"


def get_risk_score(zone, trend_direction):
    if zone == "Weak Zone":
        return "Sehr hoch"
    elif trend_direction in ["Turnaround moeglich", "Frischer Aufwaertstrend"]:
        return "Hoch"
    elif zone == "Upper Range":
        return "Mittel"
    else:
        return "Niedrig"


def color_signal(val):
    if val == "Attraktiv":
        return "background-color: #123524; color: white"
    elif val == "Hold":
        return "background-color: #1f3c88; color: white"
    elif val == "Review":
        return "background-color: #5c4b00; color: white"
    elif val == "Take Profits":
        return "background-color: #6a3d00; color: white"
    elif val == "Avoid":
        return "background-color: #5a1e1e; color: white"
    return ""


def color_trend_phase(val):
    if val == "Early Trend":
        return "background-color: #123524; color: white"
    elif val == "Mid Trend":
        return "background-color: #1f3c88; color: white"
    elif val == "Late Trend":
        return "background-color: #6a3d00; color: white"
    elif val == "Transition":
        return "background-color: #5c4b00; color: white"
    elif val == "Weak":
        return "background-color: #5a1e1e; color: white"
    return ""


def color_zone(val):
    if val == "Weak Zone":
        return "background-color: #5a1e1e; color: white"
    elif val == "Transition Zone":
        return "background-color: #4b3d00; color: white"
    elif val == "Watchlist Zone":
        return "background-color: #6b5a00; color: white"
    elif val == "Hold Zone":
        return "background-color: #1f3c88; color: white"
    elif val == "Upper Range":
        return "background-color: #123524; color: white"
    return ""


st.title("Aktien-Ranking")
st.write("Hier kannst du Aktien nach Themes, Zonen und Signal screenen.")

if not os.path.exists("theme_scores.csv"):
    st.warning("theme_scores.csv wurde nicht gefunden.")
    st.stop()

df = pd.read_csv("theme_scores.csv")

# Theme-Status und Bullisch-% je Sub Theme vorbereiten
theme_summary = (
    df.groupby("Sub Theme", as_index=False)
    .agg({
        "Trend Score": "mean"
    })
)
theme_summary["Theme Status"] = theme_summary["Trend Score"].apply(get_status)

theme_bullish = (
    df.assign(Status=df["Trend Score"].apply(get_status))
    .groupby("Sub Theme")["Status"]
    .apply(lambda x: round((x == "Bullisch").mean() * 100, 0))
    .reset_index(name="Theme Bullisch %")
)

theme_summary = theme_summary.merge(theme_bullish, on="Sub Theme", how="left")

# Zone / Trendphase / Signal pro Aktie berechnen
ranking_df = df.copy()

ranking_df["Zone"] = ranking_df.apply(
    lambda row: get_zone(row["Preis"], row["52W Low"], row["52W High"]),
    axis=1
)

ranking_df["Trendphase"] = ranking_df.apply(
    lambda row: get_trend_phase(row["Trend Score"], row["Momentum"]),
    axis=1
)

ranking_df = ranking_df.merge(
    theme_summary[["Sub Theme", "Theme Status", "Theme Bullisch %"]],
    on="Sub Theme",
    how="left"
)

ranking_df["Signal"] = ranking_df.apply(
    lambda row: get_signal(
        row["Trend Score"],
        row["Momentum"],
        row["Theme Status"],
        row["Theme Bullisch %"]
    ),
    axis=1
)

# Vereinfachte Trendrichtung fuer Ranking-Seite
# Hinweis: ohne MA50/MA200, nur auf Basis von Zone + Momentum
ranking_df["Trendrichtung"] = ranking_df.apply(
    lambda row: (
        "Frischer Aufwaertstrend"
        if row["Zone"] in ["Watchlist Zone", "Transition Zone"] and row["Momentum"] > 0
        else "Trend schwaecht sich ab"
        if row["Momentum"] < -0.20
        else "Aufwaertstrend"
        if row["Momentum"] > 0.50
        else "Seitwaerts / unklar"
    ),
    axis=1
)

ranking_df["Entry Quality"] = ranking_df.apply(
    lambda row: get_entry_quality(
        row["Zone"],
        row["Trendrichtung"],
        row["Momentum"]
    ),
    axis=1
)

ranking_df["Exit Signal"] = ranking_df.apply(
    lambda row: get_exit_signal(
        row["Zone"],
        row["Momentum"],
        row["Trendrichtung"]
    ),
    axis=1
)

ranking_df["Risiko"] = ranking_df.apply(
    lambda row: get_risk_score(
        row["Zone"],
        row["Trendrichtung"]
    ),
    axis=1
)

# Ranking innerhalb Sub Theme
ranking_df["Rank im Theme"] = ranking_df.groupby("Sub Theme")["Trend Score"] \
    .rank(ascending=False, method="min")

ranking_df["Anzahl im Theme"] = ranking_df.groupby("Sub Theme")["Ticker"] \
    .transform("count")

ranking_df["Top %"] = (
    ranking_df["Rank im Theme"] / ranking_df["Anzahl im Theme"] * 100
).round(0)

# Filter
filter_col1, filter_col2, filter_col3 = st.columns(3)

with filter_col1:
    selected_main_theme = st.selectbox(
        "Main Theme",
        ["Alle"] + sorted(ranking_df["Main Theme"].dropna().unique().tolist())
    )

with filter_col2:
    selected_sub_theme = st.selectbox(
        "Sub Theme",
        ["Alle"] + sorted(ranking_df["Sub Theme"].dropna().unique().tolist())
    )

with filter_col3:
    selected_zone = st.selectbox(
        "Zone",
        ["Alle", "Weak Zone", "Transition Zone", "Watchlist Zone", "Hold Zone", "Upper Range"]
    )

filter_col4, filter_col5, filter_col6 = st.columns(3)

with filter_col4:
    selected_signal = st.selectbox(
        "Signal",
        ["Alle", "Attraktiv", "Hold", "Review", "Take Profits", "Avoid"]
    )

with filter_col5:
    selected_trendphase = st.selectbox(
        "Trendphase",
        ["Alle", "Early Trend", "Mid Trend", "Late Trend", "Transition", "Weak"]
    )

with filter_col6:
    selected_entry_quality = st.selectbox(
        "Entry Quality",
        ["Alle", "Sehr gut", "Gut", "Neutral", "Zu spaet", "Riskant"]
    )

filter_col7, filter_col8, filter_col9 = st.columns(3)

with filter_col7:
    selected_risk = st.selectbox(
        "Risiko",
        ["Alle", "Niedrig", "Mittel", "Hoch", "Sehr hoch"]
    )

with filter_col8:
    selected_exit_signal = st.selectbox(
        "Exit Signal",
        ["Alle", "Hold", "Vorsicht", "Gewinne sichern"]
    )

with filter_col9:
    sort_by = st.selectbox(
        "Sortieren nach",
        ["Trend Score", "Momentum", "Preis", "Name", "Top %"]
    )

sort_ascending = st.checkbox("Aufsteigend sortieren", value=False)

# Filter anwenden
filtered_df = ranking_df.copy()

if selected_main_theme != "Alle":
    filtered_df = filtered_df[filtered_df["Main Theme"] == selected_main_theme]

if selected_sub_theme != "Alle":
    filtered_df = filtered_df[filtered_df["Sub Theme"] == selected_sub_theme]

if selected_zone != "Alle":
    filtered_df = filtered_df[filtered_df["Zone"] == selected_zone]

if selected_signal != "Alle":
    filtered_df = filtered_df[filtered_df["Signal"] == selected_signal]

if selected_trendphase != "Alle":
    filtered_df = filtered_df[filtered_df["Trendphase"] == selected_trendphase]

if selected_entry_quality != "Alle":
    filtered_df = filtered_df[filtered_df["Entry Quality"] == selected_entry_quality]

if selected_risk != "Alle":
    filtered_df = filtered_df[filtered_df["Risiko"] == selected_risk]

if selected_exit_signal != "Alle":
    filtered_df = filtered_df[filtered_df["Exit Signal"] == selected_exit_signal]

filtered_df = filtered_df.sort_values(by=sort_by, ascending=sort_ascending)

# Kleine Summary
sum1, sum2, sum3, sum4 = st.columns(4)
sum1.metric("Gefilterte Aktien", len(filtered_df))
sum2.metric("Attraktiv", int((filtered_df["Signal"] == "Attraktiv").sum()) if len(filtered_df) > 0 else 0)
sum3.metric("Hold", int((filtered_df["Signal"] == "Hold").sum()) if len(filtered_df) > 0 else 0)
sum4.metric("Avoid", int((filtered_df["Signal"] == "Avoid").sum()) if len(filtered_df) > 0 else 0)

# Tabelle
display_df = filtered_df[[
    "Name",
    "Ticker",
    "Zone",
    "Entry Quality",
    "Risiko"
]].copy()

height_table = min(1000, 50 + len(display_df) * 35)

st.dataframe(
    display_df
    .style
    .map(color_zone, subset=["Zone"])
    .map(color_signal, subset=["Signal"])
    .map(color_trend_phase, subset=["Trendphase"])
    .format({
        "Preis": "{:.2f}",
        "Trend Score": "{:.2f}",
        "Momentum": "{:.2f}",
        "Rank im Theme": "{:.0f}",
        "Top %": "{:.0f}%"
    }),
    use_container_width=True,
    hide_index=True,
    height=height_table
)

# Direkt zur Detailseite
st.markdown("### Aktie direkt oeffnen")

if len(display_df) > 0:
    jump_options = display_df[["Name", "Ticker"]].drop_duplicates().copy()
    jump_options["Label"] = jump_options["Name"] + " (" + jump_options["Ticker"] + ")"

    selected_jump_label = st.selectbox(
        "Waehle eine Aktie fuer die Detailseite",
        jump_options["Label"].tolist(),
        key="ranking_jump_to_stock_detail"
    )

    selected_jump_ticker = jump_options.loc[
        jump_options["Label"] == selected_jump_label, "Ticker"
    ].iloc[0]

    st.page_link(
        "pages/1_Aktien_Detail.py",
        label=f"Zur Detailseite von {selected_jump_label}",
        icon="📈",
        query_params={"ticker": selected_jump_ticker}
    )
else:
    st.info("Keine Aktien fuer die aktuelle Filterkombination gefunden.")
