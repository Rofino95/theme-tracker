import os
import pandas as pd
import streamlit as st
import yfinance as yf
import plotly.graph_objects as go


st.set_page_config(
    page_title="Aktien Detail",
    page_icon="assets/logo.png",
    layout="wide"
)


def get_status(score):
    if score > 0.7:
        return "Bullisch"
    elif score > 0.5:
        return "Neutral"
    else:
        return "Baerisch"


def get_momentum_risk(momentum_3m, zone):
    if pd.isna(momentum_3m):
        return "Unklar"

    if momentum_3m > 0.80:
        return "Extrem ueberhitzt"

    if momentum_3m > 0.50:
        return "Ueberhitzt"

    if momentum_3m < -0.10:
        return "Fallend"

    if zone == "Upper Range" and momentum_3m < 0:
        return "Kippt"

    return "Normal"


def adjust_entry_score_for_momentum_risk(entry_score, momentum_risk):
    adjusted_score = entry_score

    if momentum_risk == "Ueberhitzt":
        adjusted_score -= 2

    if momentum_risk == "Extrem ueberhitzt":
        adjusted_score -= 4

    if momentum_risk in ["Fallend", "Kippt"]:
        adjusted_score -= 3

    if momentum_risk == "Unklar":
        adjusted_score -= 1

    return max(0, min(adjusted_score, 10))


def get_master_score(entry_score, fundamental_score, risk_score, momentum_risk):
    score = entry_score * 0.5
    score += fundamental_score * 0.3

    if risk_score == "Sehr hoch":
        score -= 2
    elif risk_score == "Hoch":
        score -= 1
    elif risk_score == "Niedrig":
        score += 1

    if momentum_risk == "Ueberhitzt":
        score -= 1.5
    elif momentum_risk == "Extrem ueberhitzt":
        score -= 3
    elif momentum_risk in ["Fallend", "Kippt"]:
        score -= 2.5
    elif momentum_risk == "Unklar":
        score -= 0.5

    return round(score, 1)


def get_master_signal(master_score, momentum_risk):
    if momentum_risk in ["Extrem ueberhitzt", "Fallend", "Kippt"]:
        return "🔴 Kein Einstieg"

    if momentum_risk == "Ueberhitzt":
        return "🟡 Beobachten"

    if master_score >= 7:
        return "🟢 Einstieg sinnvoll"
    elif master_score >= 5:
        return "🟡 Beobachten"
    else:
        return "🔴 Kein Einstieg"


def get_signal(stock_score, range_momentum, momentum_3m, theme_status, theme_bullish_pct):
    if stock_score < 0.35 and momentum_3m < 0 and theme_status == "Baerisch":
        return "Avoid"

    if stock_score > 0.85 and momentum_3m < 0:
        return "Take Profits"

    if (
        0.55 <= stock_score <= 0.85
        and range_momentum > 0
        and momentum_3m > 0
        and theme_status in ["Bullisch", "Neutral"]
        and theme_bullish_pct >= 50
    ):
        return "Attraktiv"

    if stock_score > 0.85 and momentum_3m > 0:
        return "Hold"

    if stock_score >= 0.50 and range_momentum >= -0.10 and momentum_3m >= 0 and theme_status != "Baerisch":
        return "Hold"

    return "Review"


def get_trend_phase(stock_score, range_momentum, momentum_3m):
    if stock_score < 0.35 and momentum_3m < 0:
        return "Weak"
    elif stock_score > 0.85 and momentum_3m < 0:
        return "Late Trend"
    elif stock_score > 0.75 and range_momentum >= 0.30 and momentum_3m > 0:
        return "Mid Trend"
    elif 0.55 <= stock_score <= 0.75 and range_momentum > 0 and momentum_3m > 0:
        return "Early Trend"
    else:
        return "Transition"


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


def get_exit_signal(zone, range_momentum, momentum_3m, trend_direction):
    if zone == "Upper Range" and momentum_3m < 0:
        return "Gewinne sichern"

    if zone == "Upper Range" and trend_direction == "Trend schwaecht sich ab":
        return "Gewinne sichern"

    if zone == "Upper Range" and range_momentum < 0.30:
        return "Gewinne sichern"

    if trend_direction == "Trend schwaecht sich ab":
        return "Vorsicht"

    return "Hold"


def get_risk_score(zone, trend_direction):
    if zone == "Weak Zone":
        return "Sehr hoch"
    elif trend_direction in ["Turnaround moeglich", "Frischer Aufwaertstrend"]:
        return "Hoch"
    elif zone == "Upper Range":
        return "Mittel"
    else:
        return "Niedrig"


def get_fundamental_score(pe, forward_pe, revenue_growth, earnings_growth, profit_margin):
    score = 0

    if pd.notna(revenue_growth):
        if revenue_growth > 0.20:
            score += 2
        elif revenue_growth > 0.05:
            score += 1

    if pd.notna(earnings_growth):
        if earnings_growth > 0.20:
            score += 2
        elif earnings_growth > 0.05:
            score += 1

    if pd.notna(forward_pe):
        if 0 < forward_pe < 20:
            score += 2
        elif 20 <= forward_pe < 35:
            score += 1

    if pd.notna(profit_margin):
        if profit_margin > 0.20:
            score += 2
        elif profit_margin > 0.10:
            score += 1

    if pd.notna(revenue_growth) and pd.notna(earnings_growth) and pd.notna(profit_margin):
        if revenue_growth > 0.15 and earnings_growth > 0.15 and profit_margin > 0.15:
            score += 2

    return score


def get_fundamental_quality(score):
    if score >= 8:
        return "Hoch"
    elif score >= 5:
        return "Mittel"
    else:
        return "Niedrig"


def get_fazit_text(entry_quality, risk_score, position_label, trend_direction, momentum_3m, fundamental_quality, momentum_risk):
    if momentum_risk == "Extrem ueberhitzt":
        return "Die Aktie ist extrem stark gelaufen. Für einen Neueinstieg ist das Chance-Risiko-Verhältnis aktuell ungünstig."

    if momentum_risk == "Ueberhitzt":
        return "Die Aktie ist stark gelaufen. Ein Einstieg ist nicht ausgeschlossen, aber ein Rücksetzer wäre deutlich sinnvoller."

    if momentum_risk == "Fallend":
        return "Die Aktie fällt aktuell deutlich. Hier besteht Risiko, in ein fallendes Messer zu greifen."

    if momentum_risk == "Kippt":
        return "Der Trend wirkt angeschlagen. Erst Stabilisierung abwarten."

    if entry_quality == "Sehr gut" and fundamental_quality == "Hoch" and risk_score in ["Niedrig", "Mittel"]:
        return "Sehr starkes Setup: Gute Einstiegslage, starke Fundamentaldaten und vertretbares Risiko."

    if entry_quality in ["Sehr gut", "Gut"] and momentum_3m < 0:
        return "Technisch interessant, aber das echte 3M Momentum ist negativ. Der Einstieg wirkt daher noch nicht voll bestätigt."

    if entry_quality == "Gut":
        return "Solider Kandidat. Die Einstiegslage ist interessant, aber nicht perfekt."

    if fundamental_quality == "Hoch" and entry_quality not in ["Sehr gut", "Gut"]:
        return "Fundamental stark, aber der Einstieg ist technisch aktuell nicht ideal."

    if risk_score in ["Hoch", "Sehr hoch"]:
        return "Erhöhtes Risiko. Ein Einstieg wäre eher spekulativ oder sollte abgewartet werden."

    if trend_direction == "Abwaertstrend":
        return "Kein gutes Timing: Die Aktie befindet sich im Abwärtstrend."

    if position_label == "Upper Range":
        return "Die Aktie ist bereits weit gelaufen. Für einen Neueinstieg wäre ein Rücksetzer interessanter."

    return "Kein klares Einstiegssignal. Die Aktie sollte eher beobachtet werden."


@st.cache_data(ttl=3600)
def load_price_history(ticker):
    try:
        return yf.Ticker(ticker).history(period="1y")
    except Exception:
        return pd.DataFrame()


def make_tag_html(items, bg="#1f2937", color="#f9fafb"):
    tags = ""
    for item in items:
        tags += f"""
        <span style="
            display:inline-block;
            background:{bg};
            color:{color};
            padding:6px 10px;
            margin:4px 6px 0 0;
            border-radius:999px;
            font-size:14px;
            font-weight:500;
        ">{item}</span>
        """
    return tags


def badge(text, bg="#374151"):
    return f"""
    <div style="
        display:inline-block;
        background:{bg};
        color:#ffffff;
        padding:8px 14px;
        border-radius:12px;
        font-weight:700;
        font-size:16px;
        margin-top:6px;
        white-space:normal;
    ">{text}</div>
    """


def signal_badge(signal):
    colors = {
        "Attraktiv": "#123524",
        "Hold": "#1f3c88",
        "Review": "#5c4b00",
        "Take Profits": "#6a3d00",
        "Avoid": "#5a1e1e",
    }
    return badge(signal, colors.get(signal, "#374151"))


def phase_badge(phase):
    colors = {
        "Early Trend": "#123524",
        "Mid Trend": "#1f3c88",
        "Late Trend": "#6a3d00",
        "Transition": "#5c4b00",
        "Weak": "#5a1e1e",
    }
    return badge(phase, colors.get(phase, "#374151"))


def direction_badge(direction):
    colors = {
        "Aufwaertstrend": "#123524",
        "Frischer Aufwaertstrend": "#1f3c88",
        "Turnaround moeglich": "#5c4b00",
        "Seitwaerts / unklar": "#374151",
        "Trend schwaecht sich ab": "#6a3d00",
        "Abwaertstrend": "#5a1e1e",
        "Kurzfristig positiv": "#123524",
        "Kurzfristig negativ": "#5a1e1e",
        "Unklar": "#374151",
    }
    return badge(direction, colors.get(direction, "#374151"))


def momentum_risk_badge(momentum_risk):
    colors = {
        "Normal": "#123524",
        "Ueberhitzt": "#6a3d00",
        "Extrem ueberhitzt": "#5a1e1e",
        "Fallend": "#5a1e1e",
        "Kippt": "#6a3d00",
        "Unklar": "#374151",
    }
    return badge(momentum_risk, colors.get(momentum_risk, "#374151"))


st.title("Aktien-Detailseite")

st.caption("Screening nach Entry Score, 3M Momentum, Zonen, Risiko und Fundamentaldaten.")

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
main_theme_list = sorted(stock_df["Main Theme"].dropna().unique())
sub_theme_list = sorted(stock_df["Sub Theme"].dropna().unique())

price = float(stock_df.iloc[0]["Preis"])
high_52 = float(stock_df.iloc[0]["52W High"])
low_52 = float(stock_df.iloc[0]["52W Low"])
trend_score = float(stock_df.iloc[0]["Trend Score"])
range_momentum = float(stock_df.iloc[0]["Momentum"])

momentum_3m = (
    float(stock_df.iloc[0]["3M Momentum"])
    if "3M Momentum" in stock_df.columns and pd.notna(stock_df.iloc[0]["3M Momentum"])
    else 0
)

description = stock_df.iloc[0]["Description"] if "Description" in stock_df.columns else ""

pe = stock_df.iloc[0]["PE"] if "PE" in stock_df.columns else None
forward_pe = stock_df.iloc[0]["Forward PE"] if "Forward PE" in stock_df.columns else None
revenue_growth = stock_df.iloc[0]["Revenue Growth"] if "Revenue Growth" in stock_df.columns else None
earnings_growth = stock_df.iloc[0]["Earnings Growth"] if "Earnings Growth" in stock_df.columns else None
profit_margin = stock_df.iloc[0]["Profit Margin"] if "Profit Margin" in stock_df.columns else None
market_cap = stock_df.iloc[0]["Market Cap"] if "Market Cap" in stock_df.columns else None

range_52 = high_52 - low_52

weak_zone_max = low_52 + 0.35 * range_52
watchlist_zone_min = low_52 + 0.55 * range_52
watchlist_zone_max = low_52 + 0.70 * range_52
hold_zone_min = low_52 + 0.70 * range_52
hold_zone_max = low_52 + 0.85 * range_52
upper_range_min = low_52 + 0.85 * range_52

primary_sub_theme = stock_df.iloc[0]["Sub Theme"]

theme_df = df[df["Sub Theme"] == primary_sub_theme].copy()
theme_status = get_status(theme_df["Trend Score"].mean())
theme_bullish_pct = round((theme_df["Trend Score"].apply(get_status) == "Bullisch").mean() * 100, 0)

signal = get_signal(trend_score, range_momentum, momentum_3m, theme_status, theme_bullish_pct)
trend_phase = get_trend_phase(trend_score, range_momentum, momentum_3m)

hist = load_price_history(ticker)
trend_direction = get_trend_direction(hist, price)

if price < weak_zone_max:
    position_label = "Weak Zone"
elif weak_zone_max <= price < watchlist_zone_min:
    position_label = "Transition Zone"
elif watchlist_zone_min <= price < hold_zone_min:
    position_label = "Watchlist Zone"
elif hold_zone_min <= price < upper_range_min:
    position_label = "Hold Zone"
else:
    position_label = "Upper Range"

momentum_risk = get_momentum_risk(momentum_3m, position_label)

if momentum_risk in ["Ueberhitzt", "Extrem ueberhitzt", "Fallend", "Kippt"]:
    signal = "Review"

fundamental_score = get_fundamental_score(
    pe,
    forward_pe,
    revenue_growth,
    earnings_growth,
    profit_margin
)

fundamental_quality = get_fundamental_quality(fundamental_score)

entry_score = get_entry_score(
    position_label,
    trend_direction,
    range_momentum,
    momentum_3m,
    fundamental_quality,
    forward_pe,
    revenue_growth,
    earnings_growth
)

entry_score = adjust_entry_score_for_momentum_risk(entry_score, momentum_risk)
entry_quality = get_entry_quality_from_score(entry_score)

exit_signal = get_exit_signal(
    position_label,
    range_momentum,
    momentum_3m,
    trend_direction
)

risk_score = get_risk_score(position_label, trend_direction)

master_score = get_master_score(
    entry_score,
    fundamental_score,
    risk_score,
    momentum_risk
)

master_signal = get_master_signal(
    master_score,
    momentum_risk
)

fazit_text = get_fazit_text(
    entry_quality,
    risk_score,
    position_label,
    trend_direction,
    momentum_3m,
    fundamental_quality,
    momentum_risk
)

if momentum_risk in ["Extrem ueberhitzt", "Ueberhitzt"]:
    combined_text = "Fundamental kann die Aktie stark sein, aber das Timing ist wegen Überhitzung aktuell schwierig."
elif momentum_risk in ["Fallend", "Kippt"]:
    combined_text = "Das technische Bild ist angeschlagen. Erst Stabilisierung abwarten."
elif fundamental_quality == "Hoch" and entry_quality in ["Sehr gut", "Gut"]:
    combined_text = "Technik und Fundamentaldaten passen gut zusammen."
elif fundamental_quality == "Hoch":
    combined_text = "Fundamental stark, aber der Einstieg ist technisch aktuell nicht ideal."
elif fundamental_quality == "Mittel" and entry_quality in ["Sehr gut", "Gut"]:
    combined_text = "Technisch interessant, fundamental aber nicht eindeutig stark."
else:
    combined_text = "Aktuell liefert die Kombination aus Technik und Fundamentaldaten kein starkes Gesamtbild."


# HEADER
st.markdown(f"## {stock_name}")
st.markdown(f"**Ticker:** `{ticker}`")

if "🟢" in master_signal:
    bg = "#123524"
elif "🟡" in master_signal:
    bg = "#5c4b00"
else:
    bg = "#5a1e1e"

st.markdown(
    f"""
<div style="
    display:flex;
    align-items:center;
    justify-content:center;
    background:{bg};
    padding:14px 20px;
    border-radius:12px;
    font-size:22px;
    font-weight:700;
    margin:18px 0 20px 0;
">
    {master_signal}
</div>
""",
    unsafe_allow_html=True
)

theme_col1, theme_col2 = st.columns(2)

with theme_col1:
    st.markdown("**Main Themes**")
    st.markdown(make_tag_html(main_theme_list, bg="#0f3d2e"), unsafe_allow_html=True)

with theme_col2:
    st.markdown("**Sub Themes**")
    st.markdown(make_tag_html(sub_theme_list, bg="#1e3a5f"), unsafe_allow_html=True)

st.markdown("---")


# KENNZAHLEN
st.markdown("### Überblick")

top1, top2, top3, top4 = st.columns(4)
top1.metric("Preis", f"{price:.2f}")
top2.metric("Trend Score", f"{trend_score:.2f}")
top3.metric("Entry Score", f"{entry_score}/10")
top4.metric("Master Score", f"{master_score}")

mid1, mid2, mid3, mid4, mid5 = st.columns(5)
mid1.metric("Range Momentum", f"{range_momentum:.2f}")
mid2.metric("3M Momentum", f"{momentum_3m * 100:.1f}%")
mid3.metric("Fundamental Score", f"{fundamental_score}/10")
mid4.metric("Risiko", risk_score)
mid5.metric("Momentum Risiko", momentum_risk)

badge1, badge2, badge3, badge4 = st.columns(4)

with badge1:
    st.markdown("**Signal**")
    st.markdown(signal_badge(signal), unsafe_allow_html=True)

with badge2:
    st.markdown("**Trendphase**")
    st.markdown(phase_badge(trend_phase), unsafe_allow_html=True)

with badge3:
    st.markdown("**Trendrichtung**")
    st.markdown(direction_badge(trend_direction), unsafe_allow_html=True)

with badge4:
    st.markdown("**Momentum Risiko**")
    st.markdown(momentum_risk_badge(momentum_risk), unsafe_allow_html=True)


if momentum_risk == "Extrem ueberhitzt":
    st.error("Diese Aktie ist nach dem 3M Momentum extrem überhitzt. Ein Neueinstieg wäre aktuell riskant.")
elif momentum_risk == "Ueberhitzt":
    st.warning("Diese Aktie ist stark gelaufen. Ein Rücksetzer wäre für einen Einstieg sinnvoller.")
elif momentum_risk == "Fallend":
    st.error("Diese Aktie fällt aktuell deutlich. Risiko eines fallenden Messers.")
elif momentum_risk == "Kippt":
    st.warning("Der Trend wirkt angeschlagen. Erst Stabilisierung abwarten.")


# CHART
st.markdown("---")
st.markdown("### Kurschart (1 Jahr)")

if not hist.empty:
    chart_hist = hist.copy()
    chart_hist["MA50"] = chart_hist["Close"].rolling(50).mean()
    chart_hist["MA200"] = chart_hist["Close"].rolling(200).mean()

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=chart_hist.index,
            y=chart_hist["Close"],
            mode="lines",
            name="Kurs",
            line=dict(width=2)
        )
    )

    fig.add_trace(
        go.Scatter(
            x=chart_hist.index,
            y=chart_hist["MA50"],
            mode="lines",
            name="MA50",
            line=dict(width=1, dash="dot")
        )
    )

    fig.add_trace(
        go.Scatter(
            x=chart_hist.index,
            y=chart_hist["MA200"],
            mode="lines",
            name="MA200",
            line=dict(width=1, dash="dash")
        )
    )

    fig.add_hrect(y0=0, y1=weak_zone_max, fillcolor="rgba(180, 50, 50, 0.08)", line_width=0)
    fig.add_hrect(y0=weak_zone_max, y1=watchlist_zone_min, fillcolor="rgba(150, 110, 40, 0.08)", line_width=0)
    fig.add_hrect(y0=watchlist_zone_min, y1=watchlist_zone_max, fillcolor="rgba(220, 180, 50, 0.08)", line_width=0)
    fig.add_hrect(y0=hold_zone_min, y1=hold_zone_max, fillcolor="rgba(50, 120, 220, 0.08)", line_width=0)
    fig.add_hrect(y0=upper_range_min, y1=high_52 * 1.1, fillcolor="rgba(50, 180, 80, 0.08)", line_width=0)

    fig.add_hline(y=weak_zone_max, line_dash="dot")
    fig.add_hline(y=watchlist_zone_min, line_dash="dot")
    fig.add_hline(y=watchlist_zone_max, line_dash="dot")
    fig.add_hline(y=hold_zone_min, line_dash="dot")
    fig.add_hline(y=hold_zone_max, line_dash="dot")
    fig.add_hline(y=upper_range_min, line_dash="dot")
    fig.add_hline(y=price, line_dash="solid", line=dict(width=2))

    fig.update_layout(
        title=f"{stock_name} ({ticker})",
        xaxis_title="Datum",
        yaxis_title="Preis",
        height=520,
        margin=dict(l=20, r=20, t=60, b=20),
        showlegend=True
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Kein Kursverlauf verfuegbar.")


# FAZIT
st.markdown("### Fazit")

f1, f2, f3, f4, f5 = st.columns(5)
f1.metric("Entry Quality", entry_quality)
f2.metric("Fundamental Quality", fundamental_quality)
f3.metric("Position", position_label)
f4.metric("Exit Signal", exit_signal)
f5.metric("Momentum Risiko", momentum_risk)

st.info(
    f"""
**Kurzfazit:** {fazit_text}

**Gesamtbild:** {combined_text}

Das Fazit kombiniert Preiszone, Trendstruktur, echtes 3M Momentum, Momentum-Risiko und Fundamentaldaten.
"""
)


# KOMPAKTE ANALYSE
st.markdown("### Kompakte Analyse")

analysis_df = pd.DataFrame([
    {
        "Bereich": "Timing",
        "Wert": entry_quality,
        "Score": f"{entry_score}/10",
        "Interpretation": f"{position_label}, {trend_direction}"
    },
    {
        "Bereich": "Momentum",
        "Wert": f"{momentum_3m * 100:.1f}% 3M",
        "Score": f"Range: {range_momentum:.2f}",
        "Interpretation": "echtes Momentum positiv" if momentum_3m > 0 else "echtes Momentum negativ"
    },
    {
        "Bereich": "Momentum Risiko",
        "Wert": momentum_risk,
        "Score": "-",
        "Interpretation": "sauber" if momentum_risk == "Normal" else "Timing-Risiko erhöht"
    },
    {
        "Bereich": "Fundamentals",
        "Wert": fundamental_quality,
        "Score": f"{fundamental_score}/10",
        "Interpretation": "fundamental stark" if fundamental_quality == "Hoch" else "fundamental gemischt"
    },
    {
        "Bereich": "Risiko",
        "Wert": risk_score,
        "Score": "-",
        "Interpretation": "erhoehtes Risiko" if risk_score in ["Hoch", "Sehr hoch"] else "vertretbares Risiko"
    }
])

st.table(analysis_df)


# FUNDAMENTALS
st.markdown("### Fundamentaldaten")

fund1, fund2, fund3 = st.columns(3)

fund1.metric("PE", f"{pe:.2f}" if pd.notna(pe) else "n/a")
fund2.metric("Forward PE", f"{forward_pe:.2f}" if pd.notna(forward_pe) else "n/a")

if pd.notna(market_cap):
    fund3.metric("Market Cap", f"{market_cap:,.0f}")
else:
    fund3.metric("Market Cap", "n/a")

fund_df = pd.DataFrame([
    {
        "Kennzahl": "Revenue Growth",
        "Wert": f"{revenue_growth * 100:.1f}%" if pd.notna(revenue_growth) else "n/a"
    },
    {
        "Kennzahl": "Earnings Growth",
        "Wert": f"{earnings_growth * 100:.1f}%" if pd.notna(earnings_growth) else "n/a"
    },
    {
        "Kennzahl": "Profit Margin",
        "Wert": f"{profit_margin * 100:.1f}%" if pd.notna(profit_margin) else "n/a"
    }
])

st.table(fund_df)


# ZONEN
st.markdown("### Zonen-Uebersicht")

zones_data = [
    {
        "Zone": "Weak Zone",
        "Preisbereich": f"Bis {weak_zone_max:.2f}",
        "Bedeutung": "Schwach / eher meiden",
        "Aktuell": "Hier" if price < weak_zone_max else ""
    },
    {
        "Zone": "Transition Zone",
        "Preisbereich": f"{weak_zone_max:.2f} - {watchlist_zone_min:.2f}",
        "Bedeutung": "Zwischenphase",
        "Aktuell": "Hier" if weak_zone_max <= price < watchlist_zone_min else ""
    },
    {
        "Zone": "Watchlist Zone",
        "Preisbereich": f"{watchlist_zone_min:.2f} - {watchlist_zone_max:.2f}",
        "Bedeutung": "Interessant",
        "Aktuell": "Hier" if watchlist_zone_min <= price < hold_zone_min else ""
    },
    {
        "Zone": "Hold Zone",
        "Preisbereich": f"{hold_zone_min:.2f} - {hold_zone_max:.2f}",
        "Bedeutung": "Trend stabil",
        "Aktuell": "Hier" if hold_zone_min <= price < upper_range_min else ""
    },
    {
        "Zone": "Upper Range",
        "Preisbereich": f"Ab {upper_range_min:.2f}",
        "Bedeutung": "Weit gelaufen",
        "Aktuell": "Hier" if price >= upper_range_min else ""
    }
]

st.table(pd.DataFrame(zones_data))


# EXPANDER
with st.expander("Warum dieses Signal?"):
    st.write(
        f"""
Diese Aktie wird aktuell als **{signal}** eingestuft.

- Trend Score: **{trend_score:.2f}**
- Range Momentum: **{range_momentum:.2f}**
- 3M Momentum: **{momentum_3m * 100:.1f}%**
- Momentum Risiko: **{momentum_risk}**
- Theme Status: **{theme_status}**
- Bullisch-Anteil: **{theme_bullish_pct:.0f}%**
- Position: **{position_label}**
- Trendrichtung: **{trend_direction}**
- Entry Quality: **{entry_quality}**
- Fundamental Quality: **{fundamental_quality}**
- Risiko: **{risk_score}**

Wenn das Momentum Risiko **Ueberhitzt**, **Extrem ueberhitzt**, **Fallend** oder **Kippt** ist, wird das Signal bewusst konservativer bewertet.
"""
    )

with st.expander("Unternehmensbeschreibung"):
    if description and str(description).strip():
        st.write(description)
    else:
        st.info("Keine Beschreibung verfuegbar.")
