import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Theme Tracker", layout="wide")

if not os.path.exists("theme_scores.csv"):
    st.warning("Noch keine Daten vorhanden – bitte warten oder update ausfuehren.")
    st.stop()

df = pd.read_csv("theme_scores.csv")

# Status pro Aktie
def get_status(score):
    if score > 0.7:
        return "Bullisch"
    elif score > 0.5:
        return "Neutral"
    else:
        return "Baerisch"

df["Status"] = df["Trend Score"].apply(get_status)

# Theme-Uebersicht bauen
grouped = (
    df.groupby("Sub Theme", as_index=False)
    .agg({
        "Trend Score": "mean",
        "Momentum": "mean"
    })
)

grouped["Trend Score"] = grouped["Trend Score"].round(2)
grouped["Momentum"] = grouped["Momentum"].round(2)
grouped["Status"] = grouped["Trend Score"].apply(get_status)
grouped = grouped.sort_values(by="Trend Score", ascending=False)

main_grouped = (
    df.groupby("Main Theme", as_index=False)
    .agg({
        "Trend Score": "mean",
        "Momentum": "mean"
    })
)

main_grouped["Trend Score"] = main_grouped["Trend Score"].round(2)
main_grouped["Momentum"] = main_grouped["Momentum"].round(2)
main_grouped["Status"] = main_grouped["Trend Score"].apply(get_status)
main_grouped = main_grouped.sort_values(by="Trend Score", ascending=False)

# Top / Flop
top_theme = grouped.iloc[0]["Sub Theme"]
top_score = grouped.iloc[0]["Trend Score"]
flop_theme = grouped.iloc[-1]["Sub Theme"]
flop_score = grouped.iloc[-1]["Trend Score"]

st.title("Theme Tracker")
st.subheader("Markt-Heatmap nach Themes")

col1, col2 = st.columns(2)
col1.metric("Top Theme", top_theme, top_score)
col2.metric("Schwaechstes Theme", flop_theme, f"-{flop_score}")

col_filter1, col_filter2 = st.columns(2)

with col_filter1:
    filter_status = st.selectbox(
        "Status filtern",
        ["Alle", "Bullisch", "Neutral", "Baerisch"]
    )

with col_filter2:
    filter_main_theme = st.selectbox(
        "Main Theme filtern",
        ["Alle"] + sorted(df["Main Theme"].dropna().unique().tolist())
    )

filtered_df = df.copy()

if filter_main_theme != "Alle":
    filtered_df = filtered_df[filtered_df["Main Theme"] == filter_main_theme]

filtered_grouped = (
    filtered_df.groupby("Sub Theme", as_index=False)
    .agg({
        "Trend Score": "mean",
        "Momentum": "mean",
        "Ticker": "count"
    })
    .rename(columns={"Ticker": "Anzahl Aktien"})
)

filtered_grouped["Trend Score"] = filtered_grouped["Trend Score"].round(2)
filtered_grouped["Momentum"] = filtered_grouped["Momentum"].round(2)
filtered_grouped["Status"] = filtered_grouped["Trend Score"].apply(get_status)

bullish_pct = (
    filtered_df.assign(IsBullish=filtered_df["Status"] == "Bullisch")
    .groupby("Sub Theme")["IsBullish"]
    .mean()
    .mul(100)
    .round(0)
    .reset_index(name="Bullisch %")
)

neutral_pct = (
    filtered_df.assign(IsNeutral=filtered_df["Status"] == "Neutral")
    .groupby("Sub Theme")["IsNeutral"]
    .mean()
    .mul(100)
    .round(0)
    .reset_index(name="Neutral %")
)

bearish_pct = (
    filtered_df.assign(IsBearish=filtered_df["Status"] == "Baerisch")
    .groupby("Sub Theme")["IsBearish"]
    .mean()
    .mul(100)
    .round(0)
    .reset_index(name="Baerisch %")
)

filtered_grouped = filtered_grouped.merge(bullish_pct, on="Sub Theme", how="left")
filtered_grouped = filtered_grouped.merge(neutral_pct, on="Sub Theme", how="left")
filtered_grouped = filtered_grouped.merge(bearish_pct, on="Sub Theme", how="left")

filtered_grouped = filtered_grouped.sort_values(by="Trend Score", ascending=False)

if filter_status != "Alle":
    filtered_grouped = filtered_grouped[filtered_grouped["Status"] == filter_status]
    
def color_status(val):
    if val == "Bullisch":
        return "background-color: #123524; color: white"
    elif val == "Neutral":
        return "background-color: #5c4b00; color: white"
    else:
        return "background-color: #5a1e1e; color: white"

styled = filtered_grouped.style.map(color_status, subset=["Status"])

st.markdown("### Main Theme Uebersicht")

st.dataframe(
    main_grouped.style.map(color_status, subset=["Status"]).format({
        "Trend Score": "{:.2f}",
        "Momentum": "{:.2f}"
    }),
    use_container_width=True,
    hide_index=True
)

st.markdown("### Sub Theme Uebersicht")

st.dataframe(
    styled.format({
        "Trend Score": "{:.2f}",
        "Momentum": "{:.2f}",
        "Bullisch %": "{:.0f}%",
        "Neutral %": "{:.0f}%",
        "Baerisch %": "{:.0f}%"
    }),
    use_container_width=True,
    hide_index=True
)

st.info(
    """
Legende

🟢 Bullisch: Trend Score ueber 0.70  
🟡 Neutral: Trend Score ueber 0.50 bis 0.70  
🔴 Baerisch: Trend Score 0.50 oder niedriger  

Momentum:
- ab 0.50 = stark positiv
- 0.00 bis 0.49 = leicht positiv
- -0.49 bis -0.01 = schwach
- ab -0.50 = stark negativ
"""
)

st.markdown("---")
st.subheader("Sub Theme im Detail")

selected_theme = st.selectbox(
    "Waehle ein Sub Theme",
    filtered_grouped["Sub Theme"].tolist()
)

detail_df = filtered_df[filtered_df["Sub Theme"] == selected_theme].copy()
detail_df = detail_df.sort_values(by="Trend Score", ascending=False)

selected_main_theme = df[df["Sub Theme"] == selected_theme]["Main Theme"].iloc[0]

st.write(f"**Main Theme:** {selected_main_theme}")
st.write(f"**Bestandteile von {selected_theme}**")

st.dataframe(
    detail_df[[
        "Name",
        "Ticker",
        "Preis",
        "52W High",
        "52W Low",
        "Trend Score",
        "Momentum",
        "Status"
    ]].style.map(color_status, subset=["Status"]).format({
        "Preis": "{:.2f}",
        "52W High": "{:.2f}",
        "52W Low": "{:.2f}",
        "Trend Score": "{:.2f}",
        "Momentum": "{:.2f}"
    }),
    use_container_width=True,
    hide_index=True
)
