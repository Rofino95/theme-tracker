import pandas as pd
import streamlit as st

st.set_page_config(page_title="Theme Tracker", layout="wide")

df = pd.read_excel("themes_clean.xlsx")

grouped = df.groupby("Sub Theme").agg({
    "Trend Score": "mean",
    "Momentum": "mean"
}).reset_index()

grouped["Trend Score"] = grouped["Trend Score"].round(2)
grouped["Momentum"] = grouped["Momentum"].round(2)
grouped = grouped.sort_values(by="Trend Score", ascending=False)

def get_status(score):
    if score > 0.7:
        return "Bullisch"
    elif score > 0.5:
        return "Neutral"
    else:
        return "Baerisch"

grouped["Status"] = grouped["Trend Score"].apply(get_status)

top_theme = grouped.iloc[0]["Sub Theme"]
top_score = grouped.iloc[0]["Trend Score"]

flop_theme = grouped.iloc[-1]["Sub Theme"]
flop_score = grouped.iloc[-1]["Trend Score"]

st.title("Theme Tracker")
st.subheader("Markt-Heatmap nach Themes")

col1, col2 = st.columns(2)
col1.metric("Top Theme", top_theme, top_score)
col2.metric(
    "Schwaechstes Theme",
    flop_theme,
    f"-{flop_score}"
)
filter_status = st.selectbox(
    "Status filtern",
    ["Alle", "Bullisch", "Neutral", "Baerisch"]
)

if filter_status != "Alle":
    grouped = grouped[grouped["Status"] == filter_status]

def color_status(val):
    if val == "Bullisch":
        return "background-color: #123524; color: white"
    elif val == "Neutral":
        return "background-color: #5c4b00; color: white"
    else:
        return "background-color: #5a1e1e; color: white"

styled = grouped.style.map(color_status, subset=["Status"])

st.dataframe(
    styled.format({
        "Trend Score": "{:.2f}",
        "Momentum": "{:.2f}"
    }),
    use_container_width=True,
    hide_index=True
)
st.info(
    """
Legende

🟢 Bullisch: Trend Score über 0.70  
🟡 Neutral: Trend Score über 0.50 bis 0.70  
🔴 Baerisch: Trend Score 0.50 oder niedriger  

Momentum:
- ab 0.50 = stark positiv
- 0.00 bis 0.49 = leicht positiv
- -0.49 bis -0.01 = schwach
- ab -0.50 = stark negativ
"""
)