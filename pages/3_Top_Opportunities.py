import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Top Opportunities", layout="wide")

st.title("🔥 Top Opportunities")

st.markdown("""
**Short Term (2 Wochen – 3 Monate)**  
Fokus: Momentum + Timing  

**Long Term (6+ Monate)**  
Fokus: Struktur + stabile Trends  
""")

if not os.path.exists("theme_scores.csv"):
    st.warning("theme_scores.csv fehlt")
    st.stop()

df = pd.read_csv("theme_scores.csv")


# =========================
# SHORT TERM SCORE
# =========================

def short_score(row):
    score = 0

    if row["Entry Quality"] == "Sehr gut":
        score += 3
    elif row["Entry Quality"] == "Gut":
        score += 2

    if row["Momentum"] > 0:
        score += 2

    if row["Zone"] in ["Watchlist Zone", "Transition Zone"]:
        score += 2

    if row["Risiko"] in ["Niedrig", "Mittel"]:
        score += 1

    return score


# =========================
# LONG TERM SCORE
# =========================

def long_score(row):
    score = 0

    if row["Trend Score"] > 0.7:
        score += 3
    elif row["Trend Score"] > 0.5:
        score += 2

    if row["Zone"] in ["Hold Zone", "Watchlist Zone"]:
        score += 2

    if row["Risiko"] in ["Niedrig", "Mittel"]:
        score += 2

    if row["Momentum"] > 0:
        score += 1

    return score


df["Short Score"] = df.apply(short_score, axis=1)
df["Long Score"] = df.apply(long_score, axis=1)


# =========================
# TOP 5 SHORT TERM
# =========================

st.markdown("## 🚀 Top 5 Short Term Chancen")

short_df = df.sort_values(by="Short Score", ascending=False).head(5)

st.dataframe(
    short_df[[
        "Name",
        "Ticker",
        "Zone",
        "Entry Quality",
        "Momentum",
        "Risiko",
        "Short Score"
    ]],
    use_container_width=True,
    hide_index=True
)


# =========================
# TOP 5 LONG TERM
# =========================

st.markdown("## 📈 Top 5 Long Term Chancen")

long_df = df.sort_values(by="Long Score", ascending=False).head(5)

st.dataframe(
    long_df[[
        "Name",
        "Ticker",
        "Zone",
        "Trend Score",
        "Momentum",
        "Risiko",
        "Long Score"
    ]],
    use_container_width=True,
    hide_index=True
)
