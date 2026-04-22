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

selected_label = st.selectbox(
    "Waehle eine Aktie",
    stock_options["Label"].tolist()
)

selected_ticker = stock_options.loc[
    stock_options["Label"] == selected_label, "Ticker"
].iloc[0]

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

