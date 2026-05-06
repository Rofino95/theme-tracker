import os
import pandas as pd
import streamlit as st
import yfinance as yf

st.set_page_config(
    page_title="Top Opportunities",
    page_icon="assets/logo.png",
    layout="wide"
)

st.title("🔥 Top Opportunities")
st.caption("Top-Kandidaten nach Entry Score, 3M Momentum, Risiko und Fundamentaldaten.")

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

st.markdown("""
**Short Term (2 Wochen – 3 Monate)**  
Fokus: Entry Score, echtes 3M Momentum, Zone und Risiko.

**Long Term (6+ Monate bis mehrere Jahre)**  
Fokus: Fundamentaldaten, Qualität und stabile technische Lage.
""")

if not os.path.exists("theme_scores.csv"):
    st.warning("theme_scores.csv fehlt")
    st.stop()

df = pd.read_csv("theme_scores.csv")

if "3M Momentum" not in df.columns:
    st.error("Die Spalte '3M Momentum' fehlt. Bitte zuerst update_data.py ausführen.")
    st.stop()


@st.cache_data(ttl=3600)
def load_price_history(ticker):
    try:
        return yf.Ticker(ticker).history(period="1y")
    except Exception:
        return pd.DataFrame()


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


def get_trend_direction(hist, price):
    if hist.empty or len(hist) < 50:
        return "Unklar"

    hist = hist.copy()
    hist["MA50"] = hist["Close"].rolling(50).mean()
    hist["MA200"] = hist["Close"].rolling(200).mean()

    ma50 = hist["MA50"].iloc[-1]
    ma200 = hist["MA200"].iloc[-1] if len(hist) >= 200 else None

    if pd.isna(ma50):
        return "Unklar"

    if ma200 is not None and not pd.isna(ma200):
        if price > ma50 and ma50 > ma200:
            recent_60 = hist.tail(60)
            above_ma50_60 = (recent_60["Close"] > recent_60["MA50"]).sum()
            ma50_slope = hist["MA50"].iloc[-1] - hist["MA50"].iloc[-20]

            if above_ma50_60 >= 45 and ma50_slope > 0:
                return "Aufwaertstrend"
            else:
                return "Frischer Aufwaertstrend"

        elif price < ma50 and ma50 < ma200:
            return "Abwaertstrend"

        elif price > ma50 and ma50 < ma200:
            return "Turnaround moeglich"

        elif price < ma50 and ma50 > ma200:
            return "Trend schwaecht sich ab"

        else:
            return "Seitwaerts / unklar"

    else:
        if price > ma50:
            return "Kurzfristig positiv"
        else:
            return "Kurzfristig negativ"


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


def get_risk_score(zone, trend_direction):
    if zone == "Weak Zone":
        return "Sehr hoch"
    elif trend_direction in ["Turnaround moeglich", "Frischer Aufwaertstrend"]:
        return "Hoch"
    elif zone == "Upper Range":
        return "Mittel"
    else:
        return "Niedrig"


def short_score(row):
    score = 0

    score += row["Entry Score"] * 1.5

    if row["3M Momentum"] > 0.10:
        score += 2
    elif row["3M Momentum"] > 0:
        score += 1
    elif row["3M Momentum"] < -0.10:
        score -= 2
    elif row["3M Momentum"] < 0:
        score -= 1

    if row["Momentum"] > 0:
        score += row["Momentum"] * 1.5

    if row["Risiko"] == "Niedrig":
        score += 2
    elif row["Risiko"] == "Mittel":
        score += 1
    elif row["Risiko"] == "Hoch":
        score -= 1
    elif row["Risiko"] == "Sehr hoch":
        score -= 2

    if row["Fundamental Quality"] == "Hoch":
        score += 1

    return score


def long_score(row):
    score = 0

    score += row["Fundamental Score"] * 2
    score += row["Trend Score"] * 2

    if row["Entry Score"] >= 6:
        score += 2
    elif row["Entry Score"] >= 4:
        score += 1

    if row["3M Momentum"] > 0:
        score += 1
    elif row["3M Momentum"] < -0.10:
        score -= 1

    if row["Risiko"] == "Niedrig":
        score += 2
    elif row["Risiko"] == "Mittel":
        score += 1

    return score


def early_score(row):
    score = 0

    score += row["Fundamental Score"] * 1.5

    if row["Trend Score"] < 0.6:
        score += 3
    elif row["Trend Score"] < 0.75:
        score += 1
    else:
        score -= 2

    if row["3M Momentum"] > 0.05:
        score += 3
    elif row["3M Momentum"] > 0:
        score += 2
    elif row["3M Momentum"] < -0.10:
        score -= 2

    if row["Momentum"] > 0:
        score += 2

    if row["Trendrichtung"] in ["Turnaround moeglich", "Frischer Aufwaertstrend"]:
        score += 2

    if row["Risiko"] == "Sehr hoch":
        score -= 2

    # Smart Money
    if pd.notna(row.get("Volume")) and pd.notna(row.get("Avg Volume")):
        if row["Volume"] > 2 * row["Avg Volume"]:
            score += 5
        elif row["Volume"] > 1.5 * row["Avg Volume"]:
            score += 3
        elif row["Volume"] > 1.2 * row["Avg Volume"]:
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
df["Fundamental Score"] = df.apply(get_fundamental_score, axis=1)
df["Fundamental Quality"] = df["Fundamental Score"].apply(get_fundamental_quality)

trendrichtungen = []

for _, row in df.iterrows():
    hist = load_price_history(row["Ticker"])
    trendrichtungen.append(get_trend_direction(hist, row["Preis"]))

df["Trendrichtung"] = trendrichtungen

df["Entry Score"] = df.apply(
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

df["Entry Quality"] = df["Entry Score"].apply(get_entry_quality_from_score)

df["Risiko"] = df.apply(
    lambda row: get_risk_score(row["Zone"], row["Trendrichtung"]),
    axis=1
)

df["Short Score"] = df.apply(short_score, axis=1)
df["Long Score"] = df.apply(long_score, axis=1)
df["Early Score"] = df.apply(early_score, axis=1)

df["High Conviction"] = (
    (df["Early Score"] >= 8) &
    (df["Fundamental Quality"] == "Hoch") &
    (df["3M Momentum"] > 0)
)

df = (
    df.sort_values(
        by=["Long Score", "Short Score", "Entry Score", "Fundamental Score"],
        ascending=[False, False, False, False]
    )
    .drop_duplicates(subset=["Ticker"], keep="first")
)

short_df = (
    df.sort_values(
        by=["Short Score", "Entry Score", "3M Momentum", "Fundamental Score"],
        ascending=[False, False, False, False]
    )
    .head(8)
)

long_df = (
    df.sort_values(
        by=["Long Score", "Fundamental Score", "Trend Score", "Entry Score"],
        ascending=[False, False, False, False]
    )
    .head(8)
)

early_df = (
    df[
        (df["3M Momentum"] > 0) &
        (df["Trend Score"] < 0.75)
    ]
    .sort_values(
        by=["Early Score", "Fundamental Score", "3M Momentum"],
        ascending=[False, False, False]
    )
    .head(8)
)

early_display = add_rank(early_df)
short_display = add_rank(short_df)
long_display = add_rank(long_df)

st.markdown("## 🚀 Top 8 Short Term Chancen")

st.dataframe(
    short_display[[
        "Rang",
        "Name",
        "Ticker",
        "Entry Quality",
        "Entry Score",
        "3M Momentum",
        "Zone",
        "Risiko",
        "Fundamental Quality",
        "Short Score"
    ]].style.format({
        "Entry Score": "{:.0f}",
        "3M Momentum": "{:.1%}",
        "Short Score": "{:.1f}"
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
        "Entry Quality",
        "Entry Score",
        "3M Momentum",
        "Risiko",
        "Trend Score",
        "Long Score"
    ]].style.format({
        "Fundamental Score": "{:.0f}",
        "Entry Score": "{:.0f}",
        "3M Momentum": "{:.1%}",
        "Trend Score": "{:.2f}",
        "Long Score": "{:.1f}"
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

st.markdown("---")

st.markdown("## 🟣 Top 8 Early Plays")

st.dataframe(
    early_display[[
        "Rang",
        "Name",
        "Ticker",
        "Fundamental Quality",
        "Trendrichtung",
        "Trend Score",
        "3M Momentum",
        "Early Score",
        "High Conviction"
    ]].style.format({
        "Trend Score": "{:.2f}",
        "3M Momentum": "{:.1%}",
        "Early Score": "{:.1f}"
    }),
    use_container_width=True,
    hide_index=True
)

st.markdown("### Early Play oeffnen")

early_options = early_display[["Name", "Ticker"]].drop_duplicates().copy()
early_options["Label"] = early_options["Name"] + " (" + early_options["Ticker"] + ")"

selected_early = st.selectbox(
    "Early Play fuer Detailseite auswaehlen",
    early_options["Label"].tolist(),
    key="early_detail_select"
)

selected_early_ticker = early_options.loc[
    early_options["Label"] == selected_early, "Ticker"
].iloc[0]

st.page_link(
    "pages/1_Aktien_Detail.py",
    label=f"Zur Detailseite von {selected_early}",
    icon="📈",
    query_params={"ticker": selected_early_ticker}
)
