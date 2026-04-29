import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Aktien Ranking", layout="wide")

if not os.path.exists("theme_scores.csv"):
    st.warning("theme_scores.csv wurde nicht gefunden.")
    st.stop()

df = pd.read_csv("theme_scores.csv")

if "3M Momentum" not in df.columns:
    st.error("Die Spalte '3M Momentum' fehlt. Bitte zuerst update_data.py ausführen.")
    st.stop()


def get_status(score):
    if score > 0.7:
        return "Bullisch"
    elif score > 0.5:
        return "Neutral"
    else:
        return "Baerisch"


def get_signal(stock_score, range_momentum, momentum_3m, theme_status, theme_bullish_pct):
    if stock_score < 0.35 and momentum_3m < 0 and theme_status == "Baerisch":
        return "Avoid"
    if stock_score > 0.85 and momentum_3m < 0:
        return "Take Profits"
    if (
        0.55 <= stock_score <= 0.85
        and range_momentum > 0
        and momentum_3m > 0
        and theme_status in ["Bullisch", "Neutral"]
        and theme_bullish_pct >= 50
    ):
        return "Attraktiv"
    if stock_score > 0.85 and momentum_3m > 0:
        return "Hold"
    if stock_score >= 0.50 and range_momentum >= -0.10 and momentum_3m >= 0 and theme_status != "Baerisch":
        return "Hold"
    return "Review"


def get_trend_phase(stock_score, range_momentum, momentum_3m):
    if stock_score < 0.35 and momentum_3m < 0:
        return "Weak"
    elif stock_score > 0.85 and momentum_3m < 0:
        return "Late Trend"
    elif stock_score > 0.75 and range_momentum >= 0.30 and momentum_3m > 0:
        return "Mid Trend"
    elif 0.55 <= stock_score <= 0.75 and range_momentum > 0 and momentum_3m > 0:
        return "Early Trend"
    else:
        return "Transition"


def get_zone(price, low_52, high_52):
    range_52 = high_52 - low_52
    weak_zone_max = low_52 + 0.35 * range_52
    watchlist_zone_min = low_52 + 0.55 * range_52
    hold_zone_min = low_52 + 0.70 * range_52
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


def get_entry_score(zone, trend_direction, range_momentum, momentum_3m, fundamental_quality, forward_pe, revenue_growth, earnings_growth):
    score = 0

    if zone == "Watchlist Zone":
        score += 3
    elif zone == "Transition Zone":
        score += 2
    elif zone == "Hold Zone":
        score += 1

    if trend_direction in ["Frischer Aufwaertstrend", "Turnaround moeglich"]:
        score += 2
    elif trend_direction == "Aufwaertstrend":
        score += 1
    elif trend_direction in ["Abwaertstrend", "Trend schwaecht sich ab"]:
        score -= 1

    if range_momentum > 0:
        score += 1
    elif range_momentum < -0.20:
        score -= 1

    if momentum_3m > 0.10:
        score += 2
    elif momentum_3m > 0:
        score += 1
    elif momentum_3m < -0.10:
        score -= 2
    elif momentum_3m < 0:
        score -= 1

    if fundamental_quality == "Hoch":
        score += 2
    elif fundamental_quality == "Mittel":
        score += 1

    if pd.notna(forward_pe):
        if 0 < forward_pe < 20:
            score += 1
        elif forward_pe > 60:
            score -= 1

    growth_positive = False

    if pd.notna(revenue_growth) and revenue_growth > 0.05:
        growth_positive = True

    if pd.notna(earnings_growth) and earnings_growth > 0.05:
        growth_positive = True

    if growth_positive:
        score += 1

    return max(0, min(score, 10))


def get_entry_quality_from_score(score):
    if score >= 8:
        return "Sehr gut"
    elif score >= 6:
        return "Gut"
    elif score >= 4:
        return "Neutral"
    else:
        return "Riskant"


def get_exit_signal(zone, range_momentum, trend_direction):
    if zone == "Upper Range" and range_momentum < 0.30:
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


def get_fundamental_score(pe, forward_pe, revenue_growth, earnings_growth, profit_margin):
    score = 0

    if pd.notna(revenue_growth):
        if revenue_growth > 0.20:
            score += 2
        elif revenue_growth > 0.05:
            score += 1

    if pd.notna(earnings_growth):
        if earnings_growth > 0.20:
            score += 2
        elif earnings_growth > 0.05:
            score += 1

    if pd.notna(forward_pe):
        if 0 < forward_pe < 20:
            score += 2
        elif 20 <= forward_pe < 35:
            score += 1

    if pd.notna(profit_margin):
        if profit_margin > 0.20:
            score += 2
        elif profit_margin > 0.10:
            score += 1

    if pd.notna(revenue_growth) and pd.notna(earnings_growth) and pd.notna(profit_margin):
        if revenue_growth > 0.15 and earnings_growth > 0.15 and profit_margin > 0.15:
            score += 2

    return score


def get_fundamental_quality(score):
    if score >= 8:
        return "Hoch"
    elif score >= 5:
        return "Mittel"
    else:
        return "Niedrig"


def color_fundamental_quality(val):
    if val == "Hoch":
        return "background-color: #123524; color: white"
    elif val == "Mittel":
        return "background-color: #5c4b00; color: white"
    elif val == "Niedrig":
        return "background-color: #5a1e1e; color: white"
    return ""


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


def color_entry_quality(val):
    if val == "Sehr gut":
        return "background-color: #123524; color: white"
    elif val == "Gut":
        return "background-color: #1f3c88; color: white"
    elif val == "Neutral":
        return "background-color: #5c4b00; color: white"
    elif val == "Riskant":
        return "background-color: #5a1e1e; color: white"
    return ""


def color_risk(val):
    if val == "Niedrig":
        return "background-color: #123524; color: white"
    elif val == "Mittel":
        return "background-color: #5c4b00; color: white"
    elif val == "Hoch":
        return "background-color: #6a3d00; color: white"
    elif val == "Sehr hoch":
        return "background-color: #5a1e1e; color: white"
    return ""


st.title("Aktien-Ranking")
st.caption("Screening nach Entry Score, 3M Momentum, Zonen, Risiko und Fundamentaldaten.")

st.markdown("### Navigation")

nav1, nav2, nav3, nav4, nav5 = st.columns(5)

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

st.markdown("---")

df["Status"] = df["Trend Score"].apply(get_status)

theme_summary = (
    df.groupby("Sub Theme", as_index=False)
    .agg({"Trend Score": "mean"})
)
theme_summary["Theme Status"] = theme_summary["Trend Score"].apply(get_status)

theme_bullish = (
    df.assign(Status=df["Trend Score"].apply(get_status))
    .groupby("Sub Theme")["Status"]
    .apply(lambda x: round((x == "Bullisch").mean() * 100, 0))
    .reset_index(name="Theme Bullisch %")
)

theme_summary = theme_summary.merge(theme_bullish, on="Sub Theme", how="left")

ranking_df = df.copy()

ranking_df["Zone"] = ranking_df.apply(
    lambda row: get_zone(row["Preis"], row["52W Low"], row["52W High"]),
    axis=1
)

ranking_df["Trendphase"] = ranking_df.apply(
    lambda row: get_trend_phase(row["Trend Score"], row["Momentum"], row["3M Momentum"]),
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
        row["3M Momentum"],
        row["Theme Status"],
        row["Theme Bullisch %"]
    ),
    axis=1
)

ranking_df["Trendrichtung"] = ranking_df.apply(
    lambda row: (
        "Frischer Aufwaertstrend"
        if row["Zone"] in ["Watchlist Zone", "Transition Zone"] and row["Momentum"] > 0 and row["3M Momentum"] > 0
        else "Trend schwaecht sich ab"
        if row["3M Momentum"] < -0.10
        else "Aufwaertstrend"
        if row["Momentum"] > 0.50 and row["3M Momentum"] > 0
        else "Seitwaerts / unklar"
    ),
    axis=1
)

ranking_df["Fundamental Score"] = ranking_df.apply(
    lambda row: get_fundamental_score(
        row.get("PE"),
        row.get("Forward PE"),
        row.get("Revenue Growth"),
        row.get("Earnings Growth"),
        row.get("Profit Margin")
    ),
    axis=1
)

ranking_df["Fundamental Quality"] = ranking_df["Fundamental Score"].apply(get_fundamental_quality)

ranking_df["Entry Score"] = ranking_df.apply(
    lambda row: get_entry_score(
        row["Zone"],
        row["Trendrichtung"],
        row["Momentum"],
        row["3M Momentum"],
        row["Fundamental Quality"],
        row.get("Forward PE"),
        row.get("Revenue Growth"),
        row.get("Earnings Growth")
    ),
    axis=1
)

ranking_df["Entry Quality"] = ranking_df["Entry Score"].apply(get_entry_quality_from_score)

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

ranking_df["Rank im Theme"] = ranking_df.groupby("Sub Theme")["Trend Score"].rank(ascending=False, method="min")
ranking_df["Anzahl im Theme"] = ranking_df.groupby("Sub Theme")["Ticker"].transform("count")
ranking_df["Top %"] = (ranking_df["Rank im Theme"] / ranking_df["Anzahl im Theme"] * 100).round(0)

st.markdown("### Filter")

with st.expander("Filter anzeigen / ausblenden", expanded=True):
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
        selected_entry_quality = st.selectbox(
            "Entry Quality",
            ["Alle", "Sehr gut", "Gut", "Neutral", "Riskant"]
        )

    with filter_col6:
        selected_risk = st.selectbox(
            "Risiko",
            ["Alle", "Niedrig", "Mittel", "Hoch", "Sehr hoch"]
        )

    filter_col7, filter_col8, filter_col9 = st.columns(3)

    with filter_col7:
        selected_exit_signal = st.selectbox(
            "Exit Signal",
            ["Alle", "Hold", "Vorsicht", "Gewinne sichern"]
        )

    with filter_col8:
        selected_fundamental_quality = st.selectbox(
            "Fundamental Quality",
            ["Alle", "Hoch", "Mittel", "Niedrig"]
        )

    with filter_col9:
        selected_momentum_3m = st.selectbox(
            "3M Momentum",
            ["Alle", "Positiv", "Negativ"]
        )

    filter_col10, filter_col11 = st.columns(2)

    with filter_col10:
        sort_by = st.selectbox(
            "Sortieren nach",
            [
                "Entry Score",
                "Fundamental Score",
                "3M Momentum",
                "Trend Score",
                "Momentum",
                "Preis",
                "Name",
                "Top %"
            ]
        )

    with filter_col11:
        sort_ascending = st.checkbox("Aufsteigend sortieren", value=False)

filtered_df = ranking_df.copy()

if selected_main_theme != "Alle":
    filtered_df = filtered_df[filtered_df["Main Theme"] == selected_main_theme]

if selected_sub_theme != "Alle":
    filtered_df = filtered_df[filtered_df["Sub Theme"] == selected_sub_theme]

if selected_zone != "Alle":
    filtered_df = filtered_df[filtered_df["Zone"] == selected_zone]

if selected_signal != "Alle":
    filtered_df = filtered_df[filtered_df["Signal"] == selected_signal]

if selected_entry_quality != "Alle":
    filtered_df = filtered_df[filtered_df["Entry Quality"] == selected_entry_quality]

if selected_risk != "Alle":
    filtered_df = filtered_df[filtered_df["Risiko"] == selected_risk]

if selected_exit_signal != "Alle":
    filtered_df = filtered_df[filtered_df["Exit Signal"] == selected_exit_signal]

if selected_fundamental_quality != "Alle":
    filtered_df = filtered_df[filtered_df["Fundamental Quality"] == selected_fundamental_quality]

if selected_momentum_3m == "Positiv":
    filtered_df = filtered_df[filtered_df["3M Momentum"] > 0]

if selected_momentum_3m == "Negativ":
    filtered_df = filtered_df[filtered_df["3M Momentum"] < 0]

filtered_df = filtered_df.sort_values(by=sort_by, ascending=sort_ascending)

summary1, summary2, summary3, summary4, summary5 = st.columns(5)

summary1.metric("Gefilterte Aktien", len(filtered_df))
summary2.metric("Sehr guter Entry", int((filtered_df["Entry Quality"] == "Sehr gut").sum()) if len(filtered_df) > 0 else 0)
summary3.metric("Fundamental Hoch", int((filtered_df["Fundamental Quality"] == "Hoch").sum()) if len(filtered_df) > 0 else 0)
summary4.metric("3M Momentum positiv", int((filtered_df["3M Momentum"] > 0).sum()) if len(filtered_df) > 0 else 0)
summary5.metric("Niedriges Risiko", int((filtered_df["Risiko"] == "Niedrig").sum()) if len(filtered_df) > 0 else 0)

st.markdown("### Ergebnisliste")

display_df = filtered_df[[
    "Name",
    "Ticker",
    "Zone",
    "Entry Quality",
    "Entry Score",
    "3M Momentum",
    "Signal",
    "Risiko",
    "Fundamental Quality",
    "Fundamental Score"
]].copy()

display_df = display_df.rename(columns={
    "Momentum": "Range Momentum"
})

height_table = min(1000, 50 + len(display_df) * 35)

st.dataframe(
    display_df
    .style
    .map(color_zone, subset=["Zone"])
    .map(color_entry_quality, subset=["Entry Quality"])
    .map(color_signal, subset=["Signal"])
    .map(color_risk, subset=["Risiko"])
    .map(color_fundamental_quality, subset=["Fundamental Quality"])
    .format({
        "Entry Score": "{:.0f}",
        "3M Momentum": "{:.1%}",
        "Fundamental Score": "{:.0f}"
    }),
    use_container_width=True,
    hide_index=True,
    height=height_table
)

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
    
