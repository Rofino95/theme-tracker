import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Top Opportunities", layout="wide")

st.title("🔥 Top Opportunities")

st.markdown("""
**Short Term (2 Wochen – 3 Monate)**  
→ Fokus: Einstieg + Momentum  

**Long Term (6+ Monate)**  
→ Fokus: Fundament + Stabilität  
""")

if not os.path.exists("theme_scores.csv"):
    st.warning("theme_scores.csv fehlt")
    st.stop()

df = pd.read_csv("theme_scores.csv")


# =========================
# FUNDAMENTAL SCORE
# =========================

def get_fundamental_score(row):
    score = 0

    if pd.notna(row["Revenue Growth"]):
        if row["Revenue Growth"] > 0.20:
            score += 2
        elif row["Revenue Growth"] > 0.05:
            score += 1

    if pd.notna(row["Earnings Growth"]):
        if row["Earnings Growth"] > 0.20:
            score += 2
        elif row["Earnings Growth"] > 0.05:
            score += 1

    if pd.notna(row["Forward PE"]):
        if 0 < row["Forward PE"] < 20:
            score += 2
        elif row["Forward PE"] < 35:
            score += 1

    if pd.notna(row["Profit Margin"]):
        if row["Profit Margin"] > 0.20:
            score += 2
        elif row["Profit Margin"] > 0.10:
            score += 1

    return score


def get_fundamental_quality(score):
    if score >= 6:
        return "Hoch"
    elif score >= 3:
        return "Mittel"
    else:
        return "Niedrig"


# =========================
# ZONE + ENTRY + RISK (vereinfacht)
# =========================

def get_zone(row):
    low = row["52W Low"]
    high = row["52W High"]
    price = row["Preis"]

    r = high - low

    if price < low + 0.35 * r:
        return "Weak"
    elif price < low + 0.55 * r:
        return "Transition"
    elif price < low + 0.70 * r:
        return "Watchlist"
    elif price < low + 0.85 * r:
        return "Hold"
    else:
        return "Upper"


def get_entry_quality(row):
    if row["Zone"] in ["Watchlist", "Transition"] and row["Momentum"] > 0:
        return "Sehr gut"
    elif row["Zone"] == "Hold" and row["Momentum"] > 0:
        return "Gut"
    elif row["Zone"] == "Upper":
        return "Zu spät"
    else:
        return "Schwach"


def get_risk(row):
    if row["Zone"] == "Weak":
        return "Sehr hoch"
    elif row["Momentum"] < 0:
        return "Hoch"
    elif row["Zone"] == "Upper":
        return "Mittel"
    else:
        return "Niedrig"


# =========================
# BERECHNUNG
# =========================

df["Zone"] = df.apply(get_zone, axis=1)
df["Entry"] = df.apply(get_entry_quality, axis=1)
df["Risk"] = df.apply(get_risk, axis=1)

df["Fundamental Score"] = df.apply(get_fundamental_score, axis=1)
df["Fundamental Quality"] = df["Fundamental Score"].apply(get_fundamental_quality)


# =========================
# OPPORTUNITY SCORE
# =========================

def get_opportunity_score(row):
    score = 0

    if row["Entry"] == "Sehr gut":
        score += 3
    elif row["Entry"] == "Gut":
        score += 2

    if row["Fundamental Quality"] == "Hoch":
        score += 3
    elif row["Fundamental Quality"] == "Mittel":
        score += 2

    if row["Risk"] == "Niedrig":
        score += 2
    elif row["Risk"] == "Mittel":
        score += 1

    if row["Momentum"] > 0:
        score += 1

    return score


df["Opportunity Score"] = df.apply(get_opportunity_score, axis=1)


# =========================
# SHORT TERM
# =========================

st.markdown("## 🚀 Top 5 Short Term")

short_df = df.sort_values(by="Opportunity Score", ascending=False).head(5)

st.dataframe(
    short_df[[
        "Name",
        "Ticker",
        "Entry",
        "Fundamental Quality",
        "Risk",
        "Momentum",
        "Opportunity Score"
    ]],
    use_container_width=True,
    hide_index=True
)


# =========================
# LONG TERM
# =========================

st.markdown("## 📈 Top 5 Long Term")

long_df = df.sort_values(by="Fundamental Score", ascending=False).head(5)

st.dataframe(
    long_df[[
        "Name",
        "Ticker",
        "Fundamental Quality",
        "Fundamental Score",
        "Risk"
    ]],
    use_container_width=True,
    hide_index=True
)
