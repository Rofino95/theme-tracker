import os
import pandas as pd
import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

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


def get_entry_quality(zone, trend_direction, momentum):
    if zone in ["Watchlist Zone", "Transition Zone"] and momentum > 0 and trend_direction in ["Turnaround moeglich", "Frischer Aufwaertstrend"]:
        return "Sehr gut"
    elif zone == "Hold Zone" and momentum > 0:
        return "Gut"
    elif zone == "Upper Range":
        return "Zu spaet"
    elif zone == "Weak Zone":
        return "Riskant"
    else:
        return "Neutral"


def get_exit_signal(zone, momentum, trend_direction):
    if zone == "Upper Range" and momentum < 0.30:
        return "Gewinne sichern"
    elif trend_direction == "Trend schwaecht sich ab":
        return "Vorsicht"
    else:
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


def get_fazit_text(entry_quality, exit_signal, risk_score, position_label, trend_direction, trend_phase, signal):
    if entry_quality == "Sehr gut" and risk_score in ["Niedrig", "Mittel"]:
        return "Interessanter Einstiegskandidat. Das Setup wirkt attraktiv, weil Preiszone, Trendrichtung und Momentum zusammenpassen."

    if entry_quality == "Sehr gut" and risk_score in ["Hoch", "Sehr hoch"]:
        return "Interessanter, aber spekulativer Einstiegskandidat. Das Chance-Risiko-Profil ist erhoeht, deshalb waere ein gestaffelter Einstieg sinnvoller als ein voller Einstieg."

    if entry_quality == "Gut":
        return "Solider Kandidat. Ein Einstieg kann sinnvoll sein, allerdings ist die Aktie nicht mehr ganz frueh in der Bewegung."

    if entry_quality == "Zu spaet":
        return "Technisch stark, aber fuer einen Neueinstieg eher spaet. Die Aktie ist bereits weit gelaufen, deshalb waere ein Ruecksetzer interessanter."

    if entry_quality == "Riskant":
        return "Riskantes Setup. Aufgrund der schwachen Preiszone oder Trendstruktur waere ein Einstieg aktuell eher nicht sinnvoll."

    if trend_direction == "Abwaertstrend":
        return "Kein klares Timing-Signal. Aufgrund des Abwaertstrends waere ein Einstieg aktuell eher nicht sinnvoll, solange keine Trendwende bestaetigt ist."

    if trend_direction == "Trend schwaecht sich ab":
        return "Vorsicht. Der Trend schwaecht sich ab, deshalb waere ein Neueinstieg aktuell eher unattraktiv."

    if position_label == "Transition Zone":
        return "Kein klares Timing-Signal. Die Aktie befindet sich zwischen schwacher Zone und Watchlist-Zone, deshalb waere Abwarten aktuell sinnvoller."

    return "Kein klares Timing-Signal. Die Faktoren liefern aktuell kein eindeutiges Einstiegs- oder Ausstiegssignal."


@st.cache_data(ttl=3600)
def load_price_history(ticker):
    try:
        hist = yf.Ticker(ticker).history(period="1y")
        return hist
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


def signal_badge(signal):
    colors = {
        "Attraktiv": ("#123524", "#ffffff"),
        "Hold": ("#1f3c88", "#ffffff"),
        "Review": ("#5c4b00", "#ffffff"),
        "Take Profits": ("#6a3d00", "#ffffff"),
        "Avoid": ("#5a1e1e", "#ffffff"),
    }
    bg, fg = colors.get(signal, ("#374151", "#ffffff"))
    return f"""
    <div style="
        display:inline-block;
        background:{bg};
        color:{fg};
        padding:8px 14px;
        border-radius:12px;
        font-weight:700;
        font-size:16px;
        margin-top:6px;
    ">{signal}</div>
    """


def phase_badge(phase):
    colors = {
        "Early Trend": ("#123524", "#ffffff"),
        "Mid Trend": ("#1f3c88", "#ffffff"),
        "Late Trend": ("#6a3d00", "#ffffff"),
        "Transition": ("#5c4b00", "#ffffff"),
        "Weak": ("#5a1e1e", "#ffffff"),
    }
    bg, fg = colors.get(phase, ("#374151", "#ffffff"))
    return f"""
    <div style="
        display:inline-block;
        background:{bg};
        color:{fg};
        padding:8px 14px;
        border-radius:12px;
        font-weight:700;
        font-size:16px;
        margin-top:6px;
    ">{phase}</div>
    """


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
momentum = float(stock_df.iloc[0]["Momentum"])
description = stock_df.iloc[0]["Description"] if "Description" in stock_df.columns else ""

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

signal = get_signal(trend_score, momentum, theme_status, theme_bullish_pct)
trend_phase = get_trend_phase(trend_score, momentum)

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

if momentum >= 0.50:
    trend_label = "Very Strong"
elif momentum >= 0.20:
    trend_label = "Strong"
elif momentum >= 0.00:
    trend_label = "Positive"
elif momentum >= -0.20:
    trend_label = "Weakening"
else:
    trend_label = "Weak"

if position_label == "Upper Range" and momentum > 0.30:
    interpretation_label = "Hold"
elif position_label == "Upper Range" and momentum <= 0.30:
    interpretation_label = "Take Profits moeglich"
elif position_label == "Hold Zone" and momentum >= 0.00:
    interpretation_label = "Hold"
elif position_label == "Watchlist Zone" and momentum > 0.00:
    interpretation_label = "Attraktiv / Watchlist"
elif position_label == "Weak Zone" and momentum < 0.00:
    interpretation_label = "Avoid"
else:
    interpretation_label = "Review"

if trend_direction == "Turnaround moeglich" and signal == "Attraktiv":
    interpretation_label = "Spekulativer Turnaround"

entry_quality = get_entry_quality(position_label, trend_direction, momentum)
exit_signal = get_exit_signal(position_label, momentum, trend_direction)
risk_score = get_risk_score(position_label, trend_direction)

fazit_text = get_fazit_text(
    entry_quality,
    exit_signal,
    risk_score,
    position_label,
    trend_direction,
    trend_phase,
    signal
)

st.markdown(f"## {stock_name}")
st.markdown(f"**Ticker:** `{ticker}`")

st.markdown("**Main Themes**")
st.markdown(make_tag_html(main_theme_list, bg="#0f3d2e"), unsafe_allow_html=True)

st.markdown("**Sub Themes**")
st.markdown(make_tag_html(sub_theme_list, bg="#1e3a5f"), unsafe_allow_html=True)

st.markdown("---")
st.markdown("### Kennzahlen")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Preis", f"{price:.2f}")
kpi2.metric("52W High", f"{high_52:.2f}")
kpi3.metric("52W Low", f"{low_52:.2f}")
kpi4.metric("Trend Score", f"{trend_score:.2f}")

kpi5, kpi6, kpi7, kpi8 = st.columns(4)
kpi5.metric("Momentum", f"{momentum:.2f}")

with kpi6:
    st.markdown("**Signal**")
    st.markdown(signal_badge(signal), unsafe_allow_html=True)

with kpi7:
    st.markdown("**Trendphase**")
    st.markdown(phase_badge(trend_phase), unsafe_allow_html=True)

kpi8.metric("Trendrichtung", trend_direction)

st.markdown("---")
st.markdown("### Kurschart (1 Jahr)")

if not hist.empty:
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=hist.index,
            y=hist["Close"],
            mode="lines",
            name="Kurs",
            line=dict(width=2)
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

    fig.add_hline(
        y=price,
        line_dash="solid",
        line=dict(width=2)
    )

    fig.update_layout(
        title=f"{stock_name} ({ticker})",
        xaxis_title="Datum",
        yaxis_title="Preis",
        height=520,
        margin=dict(l=20, r=20, t=60, b=20),
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Kein Kursverlauf verfuegbar.")

st.markdown("### Fazit")

fazit1, fazit2, fazit3, fazit4 = st.columns(4)

fazit1.metric("Entry Quality", entry_quality)
fazit2.metric("Exit Signal", exit_signal)
fazit3.metric("Risiko", risk_score)
fazit4.metric("Position", position_label)

if entry_quality == "Sehr gut" and risk_score in ["Hoch", "Sehr hoch"]:
    summary_text = "Interessanter, aber spekulativer Einstiegskandidat."
elif entry_quality == "Sehr gut":
    summary_text = "Interessanter Einstiegskandidat."
elif entry_quality == "Gut":
    summary_text = "Solider Kandidat, aber nicht mehr ganz frueh."
elif entry_quality == "Zu spaet":
    summary_text = "Technisch stark, aber fuer einen Neueinstieg eher spaet."
elif entry_quality == "Riskant":
    summary_text = "Riskanter Kandidat mit schwachem Setup."
else:
    summary_text = "Kein klares Timing-Signal."

st.info(
    f"""
**Kurzfazit:** {fazit_text}

- **Entry Quality:** {entry_quality}
- **Exit Signal:** {exit_signal}
- **Risiko:** {risk_score}
- **Position:** {position_label}
- **Trendrichtung:** {trend_direction}
- **Trendphase:** {trend_phase}

Das Fazit kombiniert Preiszone, Trendrichtung und Momentum. Es ist kein Kauf- oder Verkaufssignal, sondern ein Timing-Filter.
"""
)

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
        "Bedeutung": "Zwischen schwach und attraktiv",
        "Aktuell": "Hier" if weak_zone_max <= price < watchlist_zone_min else ""
    },
    {
        "Zone": "Watchlist Zone",
        "Preisbereich": f"{watchlist_zone_min:.2f} - {watchlist_zone_max:.2f}",
        "Bedeutung": "Interessant fuer Watchlist",
        "Aktuell": "Hier" if watchlist_zone_min <= price < hold_zone_min else ""
    },
    {
        "Zone": "Hold Zone",
        "Preisbereich": f"{hold_zone_min:.2f} - {hold_zone_max:.2f}",
        "Bedeutung": "Gesunder Trendbereich",
        "Aktuell": "Hier" if hold_zone_min <= price < upper_range_min else ""
    },
    {
        "Zone": "Upper Range",
        "Preisbereich": f"Ab {upper_range_min:.2f}",
        "Bedeutung": "Weit gelaufen / Momentum pruefen",
        "Aktuell": "Hier" if price >= upper_range_min else ""
    }
]

zones_df = pd.DataFrame(zones_data)
st.table(zones_df)

st.markdown("---")
st.markdown("### Warum dieses Signal?")

st.info(
    f"""
Diese Aktie wird aktuell als **{signal}** eingestuft.

- Trend Score: **{trend_score:.2f}**
- Momentum: **{momentum:.2f}**
- Zugehoeriges Sub Theme: **{primary_sub_theme}**
- Theme Status: **{theme_status}**
- Bullisch-Anteil im Theme: **{theme_bullish_pct:.0f}%**
- Position in der 52W-Range: **{position_label}**
- Trendstaerke: **{trend_label}**
- Trendrichtung: **{trend_direction}**
- Entry Quality: **{entry_quality}**
- Risiko: **{risk_score}**
"""
)

st.markdown("---")
st.markdown("### Unternehmensbeschreibung")

if description and str(description).strip():
    st.write(description)
else:
    st.info("Keine Beschreibung verfuegbar.")
