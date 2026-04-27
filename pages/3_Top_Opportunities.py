import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Top Opportunities", layout="wide")

st.title("🔥 Top Opportunities")

st.markdown("""
**Short Term (2 Wochen – 3 Monate)**  
Fokus: Einstieg, Momentum, Zone und Risiko.

**Long Term (6+ Monate bis mehrere Jahre)**  
Fokus: Fundamentaldaten, Qualität und stabile technische Lage.
""")

if not os.path.exists("theme_scores.csv"):
    st.warning("theme_scores.csv fehlt")
    st.stop()

df = pd.read_csv("theme_scores.csv")


def get_zone(row):
    low = row["52W Low"]
    high = row["52W High"]
    price = row["Preis"]

    range_52 = high - low

    weak_zone_max = low + 0.35 * range_52
    watchlist_zone_min = low + 0.55 * range_52
    hold_zone_min = low + 0.70 * range_52
    upper_range_min = low + 0.85 * range_52

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


def get_entry_quality(row):
    zone = row["Zone"]
    momentum = row["Momentum"]

    if zone in ["Watchlist Zone", "Transition Zone"] and momentum > 0:
        return "Sehr gut"
    elif zone == "Hold Zone" and momentum > 0:
        return "Gut"
    elif zone == "Upper Range":
        return "Zu spaet"
    elif zone == "Weak Zone":
        return "Riskant"
    else:
        return "Neutral"


def get_risk(row):
    if row["Zone"] == "Weak Zone":
        return "Sehr hoch"
    elif row["Zone"] == "Upper Range":
        return "Mittel"
    elif row["Momentum"] < 0:
        return "Hoch"
    else:
        return "Niedrig"


def get_fundamental_score(row):
    score = 0

    if pd.notna(row.get("Revenue Growth")):
        if row["Revenue Growth"] > 0.20:
            score += 2
        elif row["Revenue Growth"] > 0.05:
            score += 1

    if pd.notna(row.get("Earnings Growth")):
        if row["Earnings Growth"] > 0.20:
            score += 2
        elif row["Earnings Growth"] > 0.05:
            score += 1

    if pd.notna(row.get("Forward PE")):
        if 0 < row["Forward PE"] < 20:
            score += 2
        elif 20 <= row["Forward PE"] < 35:
            score += 1

    if pd.notna(row.get("Profit Margin")):
        if row["Profit Margin"] > 0.20:
            score += 2
        elif row["Profit Margin"] > 0.10:
            score += 1

    if (
        pd.notna(row.get("Revenue Growth"))
        and pd.notna(row.get("Earnings Growth"))
        and pd.notna(row.get("Profit Margin"))
    ):
        if row["Revenue Growth"] > 0.15 and row["Earnings Growth"] > 0.15 and row["Profit Margin"] > 0.15:
            score += 2

    return score


def get_fundamental_quality(score):
    if score >= 8:
        return "Hoch"
    elif score >= 5:
        return "Mittel"
    else:
        return "Niedrig"


def short_score(row):
    score = 0

    if row["Entry Quality"] == "Sehr gut":
        score += 4
    elif row["Entry Quality"] == "Gut":
        score += 2

    if row["Momentum"] > 0.50:
        score += 3
    elif row["Momentum"] > 0:
        score += 2

    if row["Zone"] == "Watchlist Zone":
        score += 3
    elif row["Zone"] == "Transition Zone":
        score += 2
    elif row["Zone"] == "Hold Zone":
        score += 1

    if row["Risiko"] == "Niedrig":
        score += 2
    elif row["Risiko"] == "Mittel":
        score += 1

    if row["Fundamental Quality"] == "Hoch":
        score += 1

    return score


def long_score(row):
    score = 0

    if row["Fundamental Quality"] == "Hoch":
        score += 5
    elif row["Fundamental Quality"] == "Mittel":
        score += 3

    if row["Fundamental Score"] >= 8:
        score += 3
    elif row["Fundamental Score"] >= 5:
        score += 2

    if row["Trend Score"] > 0.70:
        score += 2
    elif row["Trend Score"] > 0.50:
        score += 1

    if row["Momentum"] > 0:
        score += 1

    if row["Risiko"] == "Niedrig":
        score += 2
    elif row["Risiko"] == "Mittel":
        score += 1

    if row["Zone"] in ["Watchlist Zone", "Hold Zone"]:
        score += 1

    return score


def add_rank(df_to_rank):
    ranked = df_to_rank.copy().reset_index(drop=True)
    medals = ["🏆 1.", "🥈 2.", "🥉 3."]

    ranks = []
    for i in range(len(ranked)):
        if i < 3:
            ranks.append(medals[i])
        else:
            ranks.append(f"{i + 1}.")

    ranked.insert(0, "Rang", ranks)
    return ranked


df["Zone"] = df.apply(get_zone, axis=1)
df["Entry Quality"] = df.apply(get_entry_quality, axis=1)
df["Risiko"] = df.apply(get_risk, axis=1)
df["Fundamental Score"] = df.apply(get_fundamental_score, axis=1)
df["Fundamental Quality"] = df["Fundamental Score"].apply(get_fundamental_quality)

df["Short Score"] = df.apply(short_score, axis=1)
df["Long Score"] = df.apply(long_score, axis=1)

short_df = (
    df.sort_values(
        by=["Short Score", "Momentum", "Fundamental Score"],
        ascending=[False, False, False]
    )
    .head(8)
)

long_df = (
    df.sort_values(
        by=["Long Score", "Fundamental Score", "Trend Score"],
        ascending=[False, False, False]
    )
    .head(8)
)

short_display = add_rank(short_df)
long_display = add_rank(long_df)

st.markdown("## 🚀 Top 8 Short Term Chancen")

st.dataframe(
    short_display[[
        "Rang",
        "Name",
        "Ticker",
        "Entry Quality",
        "Zone",
        "Risiko",
        "Momentum",
        "Fundamental Quality",
        "Short Score"
    ]].style.format({
        "Momentum": "{:.2f}",
        "Short Score": "{:.0f}"
    }),
    use_container_width=True,
    hide_index=True
)

st.markdown("### Short Term Aktie oeffnen")

short_options = short_display[["Name", "Ticker"]].drop_duplicates().copy()
short_options["Label"] = short_options["Name"] + " (" + short_options["Ticker"] + ")"

selected_short = st.selectbox(
    "Short Term Aktie fuer Detailseite auswaehlen",
    short_options["Label"].tolist(),
    key="short_detail_select"
)

selected_short_ticker = short_options.loc[
    short_options["Label"] == selected_short, "Ticker"
].iloc[0]

st.page_link(
    "pages/1_Aktien_Detail.py",
    label=f"Zur Detailseite von {selected_short}",
    icon="📈",
    query_params={"ticker": selected_short_ticker}
)

st.markdown("---")

st.markdown("## 📈 Top 8 Long Term Chancen")

st.dataframe(
    long_display[[
        "Rang",
        "Name",
        "Ticker",
        "Fundamental Quality",
        "Fundamental Score",
        "Zone",
        "Risiko",
        "Trend Score",
        "Long Score"
    ]].style.format({
        "Fundamental Score": "{:.0f}",
        "Trend Score": "{:.2f}",
        "Long Score": "{:.0f}"
    }),
    use_container_width=True,
    hide_index=True
)

st.markdown("### Long Term Aktie oeffnen")

long_options = long_display[["Name", "Ticker"]].drop_duplicates().copy()
long_options["Label"] = long_options["Name"] + " (" + long_options["Ticker"] + ")"

selected_long = st.selectbox(
    "Long Term Aktie fuer Detailseite auswaehlen",
    long_options["Label"].tolist(),
    key="long_detail_select"
)

selected_long_ticker = long_options.loc[
    long_options["Label"] == selected_long, "Ticker"
].iloc[0]

st.page_link(
    "pages/1_Aktien_Detail.py",
    label=f"Zur Detailseite von {selected_long}",
    icon="📈",
    query_params={"ticker": selected_long_ticker}
)
