import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Aktien Detail", layout="wide")

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

st.title("Aktien-Detailseite")

if not os.path.exists("theme_scores.csv"):
    st.warning("theme_scores.csv wurde nicht gefunden.")
    st.stop()

df = pd.read_csv("theme_scores.csv")

stock_options = (
    df[["Name", "Ticker"]]
    .drop_duplicates()
    .sort_values(by="Name")
)

stock_options["Label"] = stock_options["Name"] + " (" + stock_options["Ticker"] + ")"

query_ticker = st.query_params.get("ticker", None)

labels = stock_options["Label"].tolist()
default_index = 0

if query_ticker is not None:
    matches = stock_options[stock_options["Ticker"] == query_ticker]
    if not matches.empty:
        default_label = matches.iloc[0]["Label"]
        if default_label in labels:
            default_index = int(labels.index(default_label))

selected_label = st.selectbox(
    "Waehle eine Aktie",
    labels,
    index=default_index
)

selected_ticker = stock_options.loc[
    stock_options["Label"] == selected_label, "Ticker"
].iloc[0]

st.query_params["ticker"] = selected_ticker

stock_df = df[df["Ticker"] == selected_ticker].copy()

stock_name = stock_df.iloc[0]["Name"]
ticker = stock_df.iloc[0]["Ticker"]
main_themes = ", ".join(sorted(stock_df["Main Theme"].dropna().unique()))
sub_themes = ", ".join(sorted(stock_df["Sub Theme"].dropna().unique()))
price = stock_df.iloc[0]["Preis"]
high_52 = stock_df.iloc[0]["52W High"]
low_52 = stock_df.iloc[0]["52W Low"]
trend_score = stock_df.iloc[0]["Trend Score"]
momentum = stock_df.iloc[0]["Momentum"]
description = stock_df.iloc[0]["Description"] if "Description" in stock_df.columns else ""

range_52 = high_52 - low_52

weak_zone_max = low_52 + 0.35 * range_52

watchlist_zone_min = low_52 + 0.55 * range_52
watchlist_zone_max = low_52 + 0.70 * range_52

hold_zone_min = low_52 + 0.70 * range_52
hold_zone_max = low_52 + 0.85 * range_52

take_profits_min = low_52 + 0.85 * range_52

primary_sub_theme = stock_df.iloc[0]["Sub Theme"]

theme_df = df[df["Sub Theme"] == primary_sub_theme].copy()
theme_status = get_status(theme_df["Trend Score"].mean())
theme_bullish_pct = round((theme_df["Trend Score"].apply(get_status) == "Bullisch").mean() * 100, 0)

signal = get_signal(trend_score, momentum, theme_status, theme_bullish_pct)
trend_phase = get_trend_phase(trend_score, momentum)

st.subheader(stock_name)
st.write(f"**Ticker:** {ticker}")
st.write(f"**Main Theme(s):** {main_themes}")
st.write(f"**Sub Theme(s):** {sub_themes}")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Preis", f"{price:.2f}")
col2.metric("52W High", f"{high_52:.2f}")
col3.metric("52W Low", f"{low_52:.2f}")
col4.metric("Trend Score", f"{trend_score:.2f}")

col5, col6, col7 = st.columns(3)
col5.metric("Momentum", f"{momentum:.2f}")
col6.metric("Signal", signal)
col7.metric("Trendphase", trend_phase)

st.markdown("### Einordnung")

if price < weak_zone_max:
    position_label = "Weak Zone"
elif watchlist_zone_min <= price <= watchlist_zone_max:
    position_label = "Watchlist Zone"
elif hold_zone_min <= price <= hold_zone_max:
    position_label = "Hold Zone"
elif price >= take_profits_min:
    position_label = "Upper Range"
else:
    position_label = "Transition Zone"

if momentum >= 0.50:
    trend_label = "Very Strong"
elif momentum >= 0.20:
    trend_label = "Strong"
elif momentum >= 0.00:
    trend_label = "Positive"
elif momentum >= -0.20:
    trend_label = "Weakening"
else:
    trend_label = "Weak"

if position_label == "Upper Range" and momentum > 0.30:
    interpretation_label = "Hold"
elif position_label == "Upper Range" and momentum <= 0.30:
    interpretation_label = "Take Profits moeglich"
elif position_label == "Hold Zone" and momentum >= 0.00:
    interpretation_label = "Hold"
elif position_label == "Watchlist Zone" and momentum > 0.00:
    interpretation_label = "Attraktiv / Watchlist"
elif position_label == "Weak Zone" and momentum < 0.00:
    interpretation_label = "Avoid"
else:
    interpretation_label = "Review"

info1, info2, info3 = st.columns(3)

info1.metric("Position", position_label)
info2.metric("Trend", trend_label)
info3.metric("Interpretation", interpretation_label)

st.info(
    f"""
Aktuelle Einordnung

- Position: **{position_label}**
- Trend: **{trend_label}**
- Interpretation: **{interpretation_label}**

Diese Einordnung kombiniert die aktuelle Position innerhalb der 52W-Range mit der Trenddynamik.
"""
)

st.markdown("---")
st.subheader("Warum dieses Signal?")

st.info(
    f"""
Diese Aktie wird aktuell als **{signal}** eingestuft.

- Trend Score: **{trend_score:.2f}**
- Momentum: **{momentum:.2f}**
- Zugehoeriges Sub Theme: **{primary_sub_theme}**
- Theme Status: **{theme_status}**
- Bullisch-Anteil im Theme: **{theme_bullish_pct:.0f}%**
"""
)

st.markdown("---")
st.subheader("Unternehmensbeschreibung")

if description:
    st.write(description)
else:
    st.info("Keine Beschreibung verfuegbar.")

