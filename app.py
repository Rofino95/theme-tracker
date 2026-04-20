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
        
def get_signal(stock_score, stock_momentum, theme_status, theme_bullish_pct):
    if stock_score >= 0.90 and stock_momentum < 0.20:
        return "Take Profits"
    elif stock_score < 0.35 and stock_momentum < -0.20 and theme_status == "Baerisch":
        return "Avoid"
    elif stock_score >= 0.60 and stock_momentum > 0 and theme_status in ["Bullisch", "Neutral"] and theme_bullish_pct >= 50:
        return "Attraktiv"
    elif stock_score >= 0.50 and stock_momentum >= -0.10 and theme_status != "Baerisch":
        return "Hold"
    else:
        return "Review"

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

height = 50 + len(filtered_grouped) * 35

st.dataframe(
    styled.format({
        "Trend Score": "{:.2f}",
        "Momentum": "{:.2f}",
        "Bullisch %": "{:.0f}%",
        "Neutral %": "{:.0f}%",
        "Baerisch %": "{:.0f}%"
    }),
    use_container_width=True,
    hide_index=True,
    height=height
)

st.markdown("---")
st.subheader("Aktiensuche")

search_term = st.text_input("Suche nach Aktienname oder Ticker")

if search_term:
    search_df = df.copy()
    search_df["Signal"] = search_df.apply(
        lambda row: get_signal(
            row["Trend Score"],
            row["Momentum"],
            get_status(
                df[df["Sub Theme"] == row["Sub Theme"]]["Trend Score"].mean()
            ),
            round((df[df["Sub Theme"] == row["Sub Theme"]]["Status"] == "Bullisch").mean() * 100, 0)
        ),
        axis=1
    )

    result_df = search_df[
        search_df["Name"].str.contains(search_term, case=False, na=False) |
        search_df["Ticker"].str.contains(search_term, case=False, na=False)
    ].copy()

    result_df = result_df.sort_values(by="Trend Score", ascending=False)

    if len(result_df) > 0:
        st.dataframe(
            result_df[[
                "Main Theme",
                "Sub Theme",
                "Name",
                "Ticker",
                "Preis",
                "Trend Score",
                "Momentum",
                "Status",
                "Signal"
            ]]
            .style
            .map(color_status, subset=["Status"])
            .map(color_signal, subset=["Signal"])
            .format({
                "Preis": "{:.2f}",
                "Trend Score": "{:.2f}",
                "Momentum": "{:.2f}"
            }),
            use_container_width=True,
            hide_index=True,
            height=min(900, 50 + len(result_df) * 35)
        )
    else:
        st.warning("Keine passende Aktie gefunden.")

st.markdown("---")
st.subheader("Sub Theme im Detail")

selected_theme = st.selectbox(
    "Waehle ein Sub Theme",
    filtered_grouped["Sub Theme"].tolist()
)

detail_df = filtered_df[filtered_df["Sub Theme"] == selected_theme].copy()
detail_df = detail_df.sort_values(by="Trend Score", ascending=False)

theme_status_detail = filtered_grouped[filtered_grouped["Sub Theme"] == selected_theme]["Status"].iloc[0]
theme_bullish_pct_detail = filtered_grouped[filtered_grouped["Sub Theme"] == selected_theme]["Bullisch %"].iloc[0]

detail_df["Signal"] = detail_df.apply(
    lambda row: get_signal(
        row["Trend Score"],
        row["Momentum"],
        theme_status_detail,
        theme_bullish_pct_detail
    ),
    axis=1
)

selected_main_theme = df[df["Sub Theme"] == selected_theme]["Main Theme"].iloc[0]

st.write(f"**Main Theme:** {selected_main_theme}")
st.write(f"**Bestandteile von {selected_theme}**")

best_stock = detail_df.iloc[0]["Name"]
best_score = detail_df.iloc[0]["Trend Score"]

weakest_stock = detail_df.iloc[-1]["Name"]
weakest_score = detail_df.iloc[-1]["Trend Score"]

stock_count = len(detail_df)
bullish_pct_detail = round((detail_df["Status"] == "Bullisch").mean() * 100, 0)

def metric_delta_by_status(score):
    status = get_status(score)

    if status == "Bullisch":
        return {
            "delta": f"{score:.2f}",
            "delta_color": "normal",
            "delta_arrow": "up"
        }
    elif status == "Neutral":
        return {
            "delta": f"→ {score:.2f}",
            "delta_color": "off",
            "delta_arrow": "off"
        }
    else:
        return {
            "delta": f"{score:.2f}",
            "delta_color": "inverse",
            "delta_arrow": "down"
        }

best_metric = metric_delta_by_status(best_score)
weakest_metric = metric_delta_by_status(weakest_score)

col_a, col_b, col_c, col_d = st.columns(4)

col_a.metric(
    "Staerkste Aktie",
    best_stock,
    best_metric["delta"],
    delta_color=best_metric["delta_color"],
    delta_arrow=best_metric["delta_arrow"]
)

col_b.metric(
    "Relativ schwaechste Aktie",
    weakest_stock,
    weakest_metric["delta"],
    delta_color=weakest_metric["delta_color"],
    delta_arrow=weakest_metric["delta_arrow"]
)

col_c.metric("Anzahl Aktien", stock_count)
col_d.metric("Bullisch %", f"{bullish_pct_detail:.0f}%")

col_a.caption(get_status(best_score))
col_b.caption(get_status(weakest_score))

height_detail = 50 + len(detail_df) * 35

st.dataframe(
    detail_df[[
        "Name",
        "Ticker",
        "Preis",
        "52W High",
        "52W Low",
        "Trend Score",
        "Momentum",
        "Status",
        "Signal"
    ]]
    .style
    .map(color_status, subset=["Status"])
    .map(color_signal, subset=["Signal"])
    .format({
        "Preis": "{:.2f}",
        "52W High": "{:.2f}",
        "52W Low": "{:.2f}",
        "Trend Score": "{:.2f}",
        "Momentum": "{:.2f}"
    }),
    use_container_width=True,
    hide_index=True,
    height=height_detail
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

st.info(
    """
Signal-Logik

🟢 Attraktiv:
- Trend Score mindestens 0.60
- Momentum positiv
- Theme ist Bullisch oder Neutral
- mindestens 50% der Aktien im Theme sind Bullisch

🔵 Hold:
- Trend Score mindestens 0.50
- Momentum nicht klar negativ
- Theme nicht Baerisch

🟡 Review:
- Aktie ist weder stark genug fuer Attraktiv/Hold
- oder Momentum/Trend werden schwaecher

🟠 Take Profits:
- Aktie sehr stark gelaufen (Trend Score sehr hoch)
- Momentum flacht ab
- Hinweis auf moegliche Gewinnsicherung

🔴 Avoid:
- schwacher Trend Score
- negatives Momentum
- und das Theme selbst ist Baerisch

Wichtig:
Das Signal ist keine Finanzberatung, sondern eine regelbasierte technische Einordnung innerhalb des jeweiligen Themes.
"""
)
