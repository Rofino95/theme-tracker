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
st.caption("Top-Kandidaten nach Entry Score, 3M/1M/20D Momentum, MA50, Risiko und Fundamentaldaten.")

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
Fokus: Entry Score, 3M Momentum, 1M Momentum, 20D Momentum, MA50, Zone und Risiko.

**Long Term Core (6+ Monate bis mehrere Jahre)**  
Fokus: Unternehmensqualität, strukturelle Stärke und langfristige Robustheit.

**Long Term Entry**  
Fokus: gute langfristige Werte mit sinnvollerem Einstiegsbereich.

**Early Plays**  
Gefilterte Kandidaten für frühe Trends mit zusätzlichem Smart-Money-Check.
""")

if not os.path.exists("theme_scores.csv"):
    st.warning("theme_scores.csv fehlt")
    st.stop()

df = pd.read_csv("theme_scores.csv")

required_columns = [
    "3M Momentum",
    "1M Momentum",
    "20D Momentum",
    "MA50 Abstand",
    "Preis ueber MA50",
    "Volume",
    "Avg Volume",
    "Volume Ratio"
]

missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    st.error(f"Diese Spalten fehlen in theme_scores.csv: {missing_columns}")
    st.stop()


@st.cache_data(ttl=3600)
def load_price_history(ticker):
    try:
        return yf.Ticker(ticker).history(period="1y")
    except Exception:
        return pd.DataFrame()


def normalize_bool(value):
    if value is True:
        return True

    if value is False:
        return False

    if isinstance(value, str):
        value = value.strip().lower()

        if value == "true":
            return True

        if value == "false":
            return False

    return None


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


def get_momentum_risk(
    momentum_3m,
    momentum_1m,
    momentum_20d,
    ma50_distance,
    price_above_ma50,
    zone
):
    price_above_ma50 = normalize_bool(price_above_ma50)

    if pd.isna(momentum_3m):
        return "Unklar"

    # Stark gelaufen, aber kurzfristig kippt es.
    if momentum_3m > 0.50:
        if pd.notna(momentum_1m) and momentum_1m < 0:
            return "Kippt"

        if pd.notna(momentum_20d) and momentum_20d < 0:
            return "Kippt"

        if price_above_ma50 is False:
            return "Kippt"

    # Fallendes Messer / kurzfristiger Bruch.
    if pd.notna(momentum_1m) and momentum_1m < -0.10:
        return "Fallend"

    if pd.notna(momentum_20d) and momentum_20d < -0.10:
        return "Fallend"

    if pd.notna(ma50_distance) and ma50_distance < -0.05:
        return "Fallend"

    if price_above_ma50 is False and pd.notna(momentum_1m) and momentum_1m < 0:
        return "Fallend"

    # Überhitzung ohne klaren Bruch.
    if momentum_3m > 0.80:
        return "Extrem ueberhitzt"

    if momentum_3m > 0.50:
        return "Ueberhitzt"

    if momentum_3m < -0.10:
        return "Fallend"

    if zone == "Upper Range" and momentum_3m < 0:
        return "Kippt"

    return "Normal"


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
        if (
            row["Revenue Growth"] > 0.15
            and row["Earnings Growth"] > 0.15
            and row["Profit Margin"] > 0.15
        ):
            score += 2

    return score


def get_fundamental_quality(score):
    if score >= 8:
        return "Hoch"
    elif score >= 5:
        return "Mittel"
    else:
        return "Niedrig"


def get_entry_score(
    zone,
    trend_direction,
    range_momentum,
    momentum_3m,
    fundamental_quality,
    forward_pe,
    revenue_growth,
    earnings_growth
):
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


def apply_momentum_risk_to_entry(row):
    score = row["Entry Score"]

    if row["Momentum Risiko"] == "Ueberhitzt":
        score -= 2

    if row["Momentum Risiko"] == "Extrem ueberhitzt":
        score -= 4

    if row["Momentum Risiko"] in ["Fallend", "Kippt"]:
        score -= 3

    if row["Momentum Risiko"] == "Unklar":
        score -= 1

    return max(0, min(score, 10))


def short_score(row):
    score = 0

    score += row["Entry Score"] * 1.5

    if 0.05 < row["3M Momentum"] < 0.30:
        score += 3
    elif row["3M Momentum"] > 0.30:
        score -= 2
    elif row["3M Momentum"] > 0:
        score += 1
    elif row["3M Momentum"] < -0.10:
        score -= 3
    elif row["3M Momentum"] < 0:
        score -= 1

    if pd.notna(row.get("1M Momentum")):
        if row["1M Momentum"] > 0.03:
            score += 1
        elif row["1M Momentum"] < -0.05:
            score -= 3

    if pd.notna(row.get("20D Momentum")):
        if row["20D Momentum"] > 0.03:
            score += 1
        elif row["20D Momentum"] < -0.05:
            score -= 3

    if pd.notna(row.get("MA50 Abstand")):
        if 0 <= row["MA50 Abstand"] <= 0.10:
            score += 1
        elif row["MA50 Abstand"] < -0.03:
            score -= 3
        elif row["MA50 Abstand"] > 0.25:
            score -= 2

    if row["Momentum"] > 0:
        score += row["Momentum"] * 1.5
    elif row["Momentum"] < -0.2:
        score -= 2

    if row["Zone"] == "Watchlist Zone":
        score += 3
    elif row["Zone"] == "Transition Zone":
        score += 2
    elif row["Zone"] == "Hold Zone":
        score += 1
    elif row["Zone"] == "Upper Range":
        score -= 3
    elif row["Zone"] == "Weak Zone":
        score -= 2

    if row["Trendrichtung"] == "Frischer Aufwaertstrend":
        score += 3
    elif row["Trendrichtung"] == "Aufwaertstrend":
        score += 2
    elif row["Trendrichtung"] == "Turnaround moeglich":
        score += 1
    elif row["Trendrichtung"] in ["Abwaertstrend", "Trend schwaecht sich ab", "Kurzfristig negativ"]:
        score -= 3

    if row["Risiko"] == "Niedrig":
        score += 2
    elif row["Risiko"] == "Mittel":
        score += 1
    elif row["Risiko"] == "Hoch":
        score -= 2
    elif row["Risiko"] == "Sehr hoch":
        score -= 4

    if row["Fundamental Quality"] == "Hoch":
        score += 1

    if (
        row["Trendrichtung"] in ["Aufwaertstrend", "Frischer Aufwaertstrend"]
        and row["3M Momentum"] > 0
        and row["Trend Score"] < 0.7
    ):
        score += 2

    if row["Momentum Risiko"] == "Ueberhitzt":
        score -= 4
    elif row["Momentum Risiko"] == "Extrem ueberhitzt":
        score -= 8
    elif row["Momentum Risiko"] in ["Fallend", "Kippt"]:
        score -= 8
    elif row["Momentum Risiko"] == "Unklar":
        score -= 2

    return score


def structural_score(row):
    text = " ".join([
        str(row.get("Main Theme", "")),
        str(row.get("Sub Theme", "")),
        str(row.get("Sector", "")),
        str(row.get("Industry", ""))
    ]).lower()

    score = 0

    structural_keywords = [
        "ai", "artificial intelligence", "semiconductor", "semiconductors",
        "chip", "chips", "photonics", "cloud", "data center", "datacenter",
        "networking", "software", "automation", "memory", "compute"
    ]

    cyclical_keywords = [
        "energy", "oil", "gas", "commodity", "commodities",
        "material", "materials", "gold", "mining",
        "fertilizer", "chemical", "chemicals", "agriculture"
    ]

    if any(x in text for x in structural_keywords):
        score += 3

    if any(x in text for x in cyclical_keywords):
        score -= 2

    return score


def long_type(row):
    text = " ".join([
        str(row.get("Main Theme", "")),
        str(row.get("Sub Theme", "")),
        str(row.get("Sector", "")),
        str(row.get("Industry", ""))
    ]).lower()

    if any(x in text for x in [
        "ai", "artificial intelligence", "semiconductor", "semiconductors",
        "chip", "chips", "photonics", "cloud", "data center", "datacenter",
        "networking", "software", "automation", "memory", "compute"
    ]):
        return "Structural Growth"

    if any(x in text for x in [
        "energy", "oil", "gas", "commodity", "commodities",
        "material", "materials", "gold", "mining",
        "fertilizer", "chemical", "chemicals", "agriculture"
    ]):
        return "Cyclical"

    return "Quality / Defensive"


def long_warning(row):
    warnings = []

    if row["Trend Score"] > 0.90:
        warnings.append("Zu spaet im Trend")

    if row["3M Momentum"] > 0.60:
        warnings.append("Hype Momentum")

    if pd.notna(row.get("1M Momentum")) and row["1M Momentum"] < 0:
        warnings.append("1M negativ")

    if pd.notna(row.get("20D Momentum")) and row["20D Momentum"] < 0:
        warnings.append("20D negativ")

    if pd.notna(row.get("MA50 Abstand")) and row["MA50 Abstand"] < 0:
        warnings.append("Unter/nahe MA50")

    if row["Momentum Risiko"] in ["Ueberhitzt", "Extrem ueberhitzt"]:
        warnings.append(row["Momentum Risiko"])

    if row["Momentum Risiko"] in ["Fallend", "Kippt"]:
        warnings.append("Trend kippt")

    if row["Risiko"] in ["Hoch", "Sehr hoch"]:
        warnings.append("Erhoehtes Risiko")

    return " | ".join(warnings) if warnings else ""


def long_score(row):
    score = 0

    quality_block = row["Fundamental Score"] * 2

    if row["Fundamental Quality"] == "Hoch":
        quality_block += 2
    elif row["Fundamental Quality"] == "Mittel":
        quality_block += 1

    timing_block = 0

    if row["Entry Score"] >= 8:
        timing_block += 3
    elif row["Entry Score"] >= 6:
        timing_block += 2
    elif row["Entry Score"] >= 4:
        timing_block += 1

    if 0.45 <= row["Trend Score"] <= 0.80:
        timing_block += 3
    elif 0.80 < row["Trend Score"] <= 0.90:
        timing_block += 1
    elif row["Trend Score"] > 0.90:
        timing_block -= 3

    if 0.08 <= row["3M Momentum"] <= 0.35:
        timing_block += 2
    elif 0 < row["3M Momentum"] < 0.08:
        timing_block += 1
    elif row["3M Momentum"] > 0.60:
        timing_block -= 3
    elif row["3M Momentum"] < -0.10:
        timing_block -= 2
    elif row["3M Momentum"] < 0:
        timing_block -= 1

    if pd.notna(row.get("1M Momentum")):
        if row["1M Momentum"] < -0.05:
            timing_block -= 3
        elif row["1M Momentum"] > 0.02:
            timing_block += 1

    if pd.notna(row.get("20D Momentum")):
        if row["20D Momentum"] < -0.05:
            timing_block -= 3
        elif row["20D Momentum"] > 0.02:
            timing_block += 1

    if pd.notna(row.get("MA50 Abstand")):
        if row["MA50 Abstand"] < -0.03:
            timing_block -= 3
        elif 0 <= row["MA50 Abstand"] <= 0.15:
            timing_block += 1
        elif row["MA50 Abstand"] > 0.25:
            timing_block -= 2

    if row["Momentum Risiko"] == "Ueberhitzt":
        timing_block -= 3
    elif row["Momentum Risiko"] == "Extrem ueberhitzt":
        timing_block -= 6
    elif row["Momentum Risiko"] in ["Fallend", "Kippt"]:
        timing_block -= 6
    elif row["Momentum Risiko"] == "Unklar":
        timing_block -= 1

    risk_block = 0

    if row["Risiko"] == "Niedrig":
        risk_block += 2
    elif row["Risiko"] == "Mittel":
        risk_block += 1
    elif row["Risiko"] == "Hoch":
        risk_block -= 2
    elif row["Risiko"] == "Sehr hoch":
        risk_block -= 3

    turnaround_block = 0

    if (
        row["Trendrichtung"] == "Turnaround moeglich"
        and row["Fundamental Quality"] == "Hoch"
    ):
        turnaround_block += 1.5

    structure_block = row["Structural Score"] * 1.5

    score = quality_block + timing_block + risk_block + turnaround_block + structure_block

    return score


def early_score(row):
    score = 0

    score += row["Fundamental Score"] * 2

    if row["Trend Score"] < 0.4:
        score += 5
    elif row["Trend Score"] < 0.6:
        score += 3
    else:
        score -= 2

    if 0.03 < row["3M Momentum"] < 0.25:
        score += 5
    elif row["3M Momentum"] >= 0.25:
        score -= 3
    elif row["3M Momentum"] > 0:
        score += 2

    if pd.notna(row.get("1M Momentum")):
        if 0.02 < row["1M Momentum"] < 0.20:
            score += 3
        elif row["1M Momentum"] < 0:
            score -= 5

    if pd.notna(row.get("20D Momentum")):
        if 0.02 < row["20D Momentum"] < 0.18:
            score += 3
        elif row["20D Momentum"] < 0:
            score -= 5

    if row["Trendrichtung"] == "Frischer Aufwaertstrend":
        score += 4
    elif row["Trendrichtung"] == "Turnaround moeglich":
        score += 1
    else:
        score -= 3

    if pd.notna(row.get("Volume Ratio")):
        if row["Volume Ratio"] > 2:
            score += 6
        elif row["Volume Ratio"] > 1.5:
            score += 4
        elif row["Volume Ratio"] > 1.15:
            score += 2
        elif row["Volume Ratio"] < 0.8:
            score -= 1

    if row["Momentum"] > 0:
        score += 2

    if pd.notna(row.get("MA50 Abstand")):
        if -0.03 <= row["MA50 Abstand"] <= 0.12:
            score += 2
        elif row["MA50 Abstand"] < -0.05:
            score -= 5
        elif row["MA50 Abstand"] > 0.20:
            score -= 2

    if row["Risiko"] == "Sehr hoch":
        score -= 4

    if row["Momentum Risiko"] != "Normal":
        score -= 8

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


def show_open_detail_section(display_df, label, key):
    if display_df.empty:
        return

    st.markdown(f"### {label} Aktie oeffnen")

    options = display_df[["Name", "Ticker"]].drop_duplicates().copy()
    options["Label"] = options["Name"] + " (" + options["Ticker"] + ")"

    selected = st.selectbox(
        f"{label} Aktie fuer Detailseite auswaehlen",
        options["Label"].tolist(),
        key=key
    )

    selected_ticker = options.loc[
        options["Label"] == selected, "Ticker"
    ].iloc[0]

    st.page_link(
        "pages/1_Aktien_Detail.py",
        label=f"Zur Detailseite von {selected}",
        icon="📈",
        query_params={"ticker": selected_ticker}
    )


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

df["Momentum Risiko"] = df.apply(
    lambda row: get_momentum_risk(
        row.get("3M Momentum"),
        row.get("1M Momentum"),
        row.get("20D Momentum"),
        row.get("MA50 Abstand"),
        row.get("Preis ueber MA50"),
        row.get("Zone")
    ),
    axis=1
)

df["Entry Score"] = df.apply(apply_momentum_risk_to_entry, axis=1)
df["Entry Quality"] = df["Entry Score"].apply(get_entry_quality_from_score)

df["Structural Score"] = df.apply(structural_score, axis=1)
df["Long Type"] = df.apply(long_type, axis=1)
df["Long Warning"] = df.apply(long_warning, axis=1)

df["Short Score"] = df.apply(short_score, axis=1)
df["Long Score"] = df.apply(long_score, axis=1)
df["Early Score"] = df.apply(early_score, axis=1)

df["High Conviction"] = (
    (df["Early Score"] >= 12)
    & (df["Fundamental Quality"] == "Hoch")
    & (df["3M Momentum"] > 0)
    & (df["1M Momentum"] > 0)
    & (df["20D Momentum"] > 0)
    & (df["Momentum Risiko"] == "Normal")
)

df = (
    df.sort_values(
        by=["Long Score", "Short Score", "Entry Score", "Fundamental Score"],
        ascending=[False, False, False, False]
    )
    .drop_duplicates(subset=["Ticker"], keep="first")
)

safe_momentum_mask = (
    (df["Momentum Risiko"] == "Normal")
    & (df["1M Momentum"] > 0)
    & (df["20D Momentum"] > 0)
    & (df["MA50 Abstand"] > -0.03)
)

short_df = (
    df[
        safe_momentum_mask
        & ~df["Trendrichtung"].isin(["Abwaertstrend", "Trend schwaecht sich ab", "Kurzfristig negativ"])
    ]
    .sort_values(
        by=["Short Score", "Entry Score", "1M Momentum", "20D Momentum", "Fundamental Score"],
        ascending=[False, False, False, False, False]
    )
    .head(8)
)

long_core_df = (
    df[
        df["Fundamental Quality"].isin(["Hoch", "Mittel"])
    ]
    .sort_values(
        by=["Fundamental Score", "Structural Score", "Long Score", "Entry Score"],
        ascending=[False, False, False, False]
    )
    .head(8)
)

long_entry_df = (
    df[
        df["Fundamental Quality"].isin(["Hoch", "Mittel"])
        & safe_momentum_mask
        & ~df["Trendrichtung"].isin(["Abwaertstrend", "Trend schwaecht sich ab", "Kurzfristig negativ"])
    ]
    .sort_values(
        by=["Long Score", "Entry Score", "1M Momentum", "20D Momentum", "Fundamental Score"],
        ascending=[False, False, False, False, False]
    )
    .head(8)
)

early_mask = (
    # Nicht mehr ganz unten, aber auch noch nicht spät im Trend
    (df["Trend Score"] > 0.20)
    & (df["Trend Score"] < 0.78)

    # 3M Momentum leicht bis moderat positiv
    & (df["3M Momentum"] > 0.02)
    & (df["3M Momentum"] < 0.40)

    # Kurzfristig darf es leicht wackeln, aber nicht kaputt sein
    & (df["1M Momentum"] > -0.04)
    & (df["20D Momentum"] > -0.04)

    # Kein überhitztes, fallendes oder kippendes Setup
    & (df["Momentum Risiko"] == "Normal")

    # Nicht zu weit unter MA50, aber auch nicht extrem weit darüber
    & (df["MA50 Abstand"] > -0.06)
    & (df["MA50 Abstand"] < 0.22)

    # Trendstruktur darf früh oder gerade erst positiv sein
    & (
        df["Trendrichtung"].isin([
            "Frischer Aufwaertstrend",
            "Turnaround moeglich",
            "Kurzfristig positiv",
            "Aufwaertstrend",
            "Seitwaerts / unklar"
        ])
    )

    # Volumen muss zumindest leicht erhöht sein
    & (df["Volume Ratio"] > 1.05)
)

early_df = (
    df[early_mask]
    .sort_values(
        by=[
            "Early Score",
            "Volume Ratio",
            "Fundamental Score",
            "1M Momentum",
            "20D Momentum"
        ],
        ascending=[False, False, False, False, False]
    )
)

early_df = early_df[early_df["Early Score"] >= 8].head(8)

short_display = add_rank(short_df)
long_core_display = add_rank(long_core_df)
long_entry_display = add_rank(long_entry_df)
early_display = add_rank(early_df)

st.markdown("## 🚀 Top 8 Short Term Chancen")
st.caption("Überhitzte, fallende oder kippende Werte werden hier bewusst ausgeschlossen.")

st.dataframe(
    short_display[[
        "Rang",
        "Name",
        "Ticker",
        "Entry Quality",
        "Entry Score",
        "3M Momentum",
        "1M Momentum",
        "20D Momentum",
        "MA50 Abstand",
        "Momentum Risiko",
        "Zone",
        "Risiko",
        "Fundamental Quality",
        "Short Score"
    ]].style.format({
        "Entry Score": "{:.0f}",
        "3M Momentum": "{:.1%}",
        "1M Momentum": "{:.1%}",
        "20D Momentum": "{:.1%}",
        "MA50 Abstand": "{:.1%}",
        "Short Score": "{:.1f}"
    }),
    use_container_width=True,
    hide_index=True
)

show_open_detail_section(short_display, "Short Term", "short_detail_select")

st.markdown("---")

st.markdown("## 📈 Long Term Core")
st.caption("Die qualitativ stärksten langfristigen Kandidaten. Überhitzung oder kurzfristige Schwäche wird angezeigt, aber nicht automatisch ausgeschlossen.")

st.dataframe(
    long_core_display[[
        "Rang",
        "Name",
        "Ticker",
        "Long Type",
        "Fundamental Quality",
        "Fundamental Score",
        "Structural Score",
        "Entry Quality",
        "Entry Score",
        "3M Momentum",
        "1M Momentum",
        "20D Momentum",
        "MA50 Abstand",
        "Momentum Risiko",
        "Risiko",
        "Trend Score",
        "Long Warning"
    ]].style.format({
        "Fundamental Score": "{:.0f}",
        "Structural Score": "{:.0f}",
        "Entry Score": "{:.0f}",
        "3M Momentum": "{:.1%}",
        "1M Momentum": "{:.1%}",
        "20D Momentum": "{:.1%}",
        "MA50 Abstand": "{:.1%}",
        "Trend Score": "{:.2f}"
    }),
    use_container_width=True,
    hide_index=True
)

show_open_detail_section(long_core_display, "Long Term Core", "long_core_detail_select")

st.markdown("---")

st.markdown("## 🔵 Long Term Entry")
st.caption("Langfristige Qualitätskandidaten mit Fokus auf sinnvollere Einstiegsbereiche. Kurzfristig fallende oder kippende Werte werden ausgeschlossen.")

st.dataframe(
    long_entry_display[[
        "Rang",
        "Name",
        "Ticker",
        "Long Type",
        "Fundamental Quality",
        "Fundamental Score",
        "Structural Score",
        "Entry Quality",
        "Entry Score",
        "3M Momentum",
        "1M Momentum",
        "20D Momentum",
        "MA50 Abstand",
        "Momentum Risiko",
        "Risiko",
        "Trend Score",
        "Long Score",
        "Long Warning"
    ]].style.format({
        "Fundamental Score": "{:.0f}",
        "Structural Score": "{:.0f}",
        "Entry Score": "{:.0f}",
        "3M Momentum": "{:.1%}",
        "1M Momentum": "{:.1%}",
        "20D Momentum": "{:.1%}",
        "MA50 Abstand": "{:.1%}",
        "Trend Score": "{:.2f}",
        "Long Score": "{:.1f}"
    }),
    use_container_width=True,
    hide_index=True
)

show_open_detail_section(long_entry_display, "Long Term Entry", "long_entry_detail_select")

st.markdown("---")

st.markdown("## 🟣 Early Plays")

if len(early_df) < 8:
    st.caption(f"Aktuell nur {len(early_df)} valide Early Plays im Markt gefunden.")
else:
    st.caption("Gefilterte Top-Kandidaten für frühe Trends.")

st.dataframe(
    early_display[[
        "Rang",
        "Name",
        "Ticker",
        "Fundamental Quality",
        "Trendrichtung",
        "Trend Score",
        "3M Momentum",
        "1M Momentum",
        "20D Momentum",
        "MA50 Abstand",
        "Volume Ratio",
        "Momentum Risiko",
        "Early Score",
        "High Conviction"
    ]].style.format({
        "Trend Score": "{:.2f}",
        "3M Momentum": "{:.1%}",
        "1M Momentum": "{:.1%}",
        "20D Momentum": "{:.1%}",
        "MA50 Abstand": "{:.1%}",
        "Volume Ratio": "{:.2f}",
        "Early Score": "{:.1f}"
    }),
    use_container_width=True,
    hide_index=True
)

if not early_display.empty:
    show_open_detail_section(early_display, "Early Play", "early_detail_select")
else:
    st.warning("Aktuell keine Early Plays im Markt gefunden.")
