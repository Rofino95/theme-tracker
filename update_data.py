import os
import pandas as pd
import yfinance as yf
import wikipedia
from datetime import datetime
from deep_translator import GoogleTranslator

INPUT_FILE = "theme_universe.csv"
OUTPUT_FILE = "theme_scores.csv"
SIGNAL_HISTORY_FILE = "signal_history.csv"


def get_existing_descriptions():
    if not os.path.exists(OUTPUT_FILE):
        return {}

    try:
        old_df = pd.read_csv(OUTPUT_FILE)

        if "Ticker" not in old_df.columns or "Description" not in old_df.columns:
            return {}

        old_df["Description"] = old_df["Description"].fillna("")
        return dict(zip(old_df["Ticker"], old_df["Description"]))

    except Exception as e:
        print(f"Konnte alte Beschreibungen nicht laden: {e}")
        return {}


def get_description(ticker, name, existing_description):
    if existing_description and str(existing_description).strip():
        return existing_description

    description = ""

    try:
        data = yf.Ticker(ticker)
        info = data.info
        description = info.get("longBusinessSummary") or ""
    except Exception as e:
        print(f"Yahoo-Beschreibung Fehler bei {ticker}: {e}")

    if not description or len(description.strip()) < 50:
        try:
            wikipedia.set_lang("en")
            results = wikipedia.search(name)

            if not results:
                results = wikipedia.search(f"{ticker} company")

            if results:
                description = wikipedia.summary(results[0], sentences=3, auto_suggest=False)
            else:
                description = ""
        except Exception as e:
            print(f"Wikipedia-Fehler bei {ticker}: {e}")
            description = ""

    if description and len(description.strip()) > 0:
        try:
            description = GoogleTranslator(source="auto", target="de").translate(description)
        except Exception as e:
            print(f"Uebersetzungsfehler bei {ticker}: {e}")

    return description


def fetch_data(ticker, existing_description=""):
    try:
        data = yf.Ticker(ticker)
        info = data.info
        hist = data.history(period="1y")

        if hist.empty:
            return None, None, None, None, ticker, existing_description, None, None, None, None, None, None, None, None

        price = hist["Close"].iloc[-1]
        high = hist["High"].max()
        low = hist["Low"].min()

        if len(hist) >= 64:
            price_3m_ago = hist["Close"].iloc[-64]
            momentum_3m = (price / price_3m_ago) - 1
        else:
            momentum_3m = None

        current_volume = hist["Volume"].iloc[-1]
        avg_volume = hist["Volume"].tail(30).mean()

        name = info.get("shortName") or info.get("longName") or ticker
        description = get_description(ticker, name, existing_description)

        pe = info.get("trailingPE")
        forward_pe = info.get("forwardPE")
        revenue_growth = info.get("revenueGrowth")
        earnings_growth = info.get("earningsGrowth")
        profit_margin = info.get("profitMargins")
        market_cap = info.get("marketCap")

        return (
            price,
            high,
            low,
            momentum_3m,
            name,
            description,
            pe,
            forward_pe,
            revenue_growth,
            earnings_growth,
            profit_margin,
            market_cap,
            current_volume,
            avg_volume
        )

    except Exception as e:
        print(f"Fehler bei {ticker}: {e}")
        return None, None, None, None, ticker, existing_description, None, None, None, None, None, None, None, None


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
    elif row["Trendrichtung"] in ["Abwaertstrend", "Trend schwaecht sich ab"]:
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

    if row["Risiko"] in ["Hoch", "Sehr hoch"]:
        warnings.append("Erhoehtes Risiko")

    return " | ".join(warnings) if warnings else ""


def long_score(row):
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

    return quality_block + timing_block + risk_block + turnaround_block + structure_block


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

    if row["Trendrichtung"] == "Frischer Aufwaertstrend":
        score += 4
    elif row["Trendrichtung"] == "Turnaround moeglich":
        score += 1
    else:
        score -= 3

    if pd.notna(row.get("Volume")) and pd.notna(row.get("Avg Volume")) and row["Avg Volume"] not in [0, None]:
        vol_ratio = row["Volume"] / row["Avg Volume"]

        if vol_ratio > 2:
            score += 6
        elif vol_ratio > 1.5:
            score += 4
        elif vol_ratio > 1.2:
            score += 2
        else:
            score -= 1

    if row["Momentum"] > 0:
        score += 2

    if row["Risiko"] == "Sehr hoch":
        score -= 4

    return score


def append_signal_history(df_all, short_df, long_core_df, long_entry_df, early_df):
    today_str = datetime.now().strftime("%Y-%m-%d")

    signal_frames = []

    def build_signal_frame(source_df, signal_type):
        if source_df.empty:
            return pd.DataFrame()

        cols = [
            "Ticker",
            "Name",
            "Preis",
            "Short Score",
            "Long Score",
            "Early Score",
            "Entry Score",
            "Trend Score",
            "3M Momentum",
            "Zone",
            "Trendrichtung",
            "Fundamental Score",
            "Fundamental Quality",
            "High Conviction"
        ]

        existing_cols = [c for c in cols if c in source_df.columns]
        temp = source_df[existing_cols].copy()

        temp["Date"] = today_str
        temp["Signal Type"] = signal_type
        temp["Signal Price"] = temp["Preis"]

        ordered_cols = [
            "Date",
            "Signal Type",
            "Ticker",
            "Name",
            "Signal Price",
            "Short Score",
            "Long Score",
            "Early Score",
            "Entry Score",
            "Trend Score",
            "3M Momentum",
            "Zone",
            "Trendrichtung",
            "Fundamental Score",
            "Fundamental Quality",
            "High Conviction"
        ]

        for col in ordered_cols:
            if col not in temp.columns:
                temp[col] = None

        return temp[ordered_cols]

    signal_frames.append(build_signal_frame(short_df, "Short Term"))
    signal_frames.append(build_signal_frame(long_core_df, "Long Term Core"))
    signal_frames.append(build_signal_frame(long_entry_df, "Long Term Entry"))
    signal_frames.append(build_signal_frame(early_df, "Early Play"))

    new_signals = pd.concat(signal_frames, ignore_index=True)

    if new_signals.empty:
        print("Keine Signale zum Speichern gefunden.")
        return

    if os.path.exists(SIGNAL_HISTORY_FILE):
        try:
            history_df = pd.read_csv(SIGNAL_HISTORY_FILE)
        except Exception:
            history_df = pd.DataFrame()
    else:
        history_df = pd.DataFrame()

    if not history_df.empty:
        history_df["Date"] = history_df["Date"].astype(str)
        history_df["Ticker"] = history_df["Ticker"].astype(str)
        history_df["Signal Type"] = history_df["Signal Type"].astype(str)

        existing_keys = set(
            zip(history_df["Date"], history_df["Ticker"], history_df["Signal Type"])
        )

        new_signals["__key"] = list(zip(
            new_signals["Date"].astype(str),
            new_signals["Ticker"].astype(str),
            new_signals["Signal Type"].astype(str)
        ))

        new_signals = new_signals[~new_signals["__key"].isin(existing_keys)].copy()
        new_signals = new_signals.drop(columns="__key", errors="ignore")

    if new_signals.empty:
        print("Heute wurden keine neuen Signale angehaengt.")
        return

    final_history = pd.concat([history_df, new_signals], ignore_index=True)
    final_history.to_csv(SIGNAL_HISTORY_FILE, index=False)

    print(f"Signal-Historie aktualisiert: {len(new_signals)} neue Signale gespeichert.")


def main():
    df = pd.read_csv(INPUT_FILE, sep=None, engine="python")
    df.columns = df.columns.str.strip()

    existing_descriptions = get_existing_descriptions()

    prices = []
    highs = []
    lows = []
    momentum_3m_list = []
    names = []
    descriptions = []

    pe_list = []
    forward_pe_list = []
    revenue_growth_list = []
    earnings_growth_list = []
    profit_margin_list = []
    market_cap_list = []

    volume_list = []
    avg_volume_list = []

    for ticker in df["Ticker"]:
        existing_description = existing_descriptions.get(ticker, "")

        (
            price,
            high,
            low,
            momentum_3m,
            name,
            description,
            pe,
            forward_pe,
            revenue_growth,
            earnings_growth,
            profit_margin,
            market_cap,
            volume,
            avg_volume
        ) = fetch_data(ticker, existing_description)

        prices.append(price)
        highs.append(high)
        lows.append(low)
        momentum_3m_list.append(momentum_3m)
        names.append(name)
        descriptions.append(description)

        pe_list.append(pe)
        forward_pe_list.append(forward_pe)
        revenue_growth_list.append(revenue_growth)
        earnings_growth_list.append(earnings_growth)
        profit_margin_list.append(profit_margin)
        market_cap_list.append(market_cap)

        volume_list.append(volume)
        avg_volume_list.append(avg_volume)

    df["Preis"] = prices
    df["52W High"] = highs
    df["52W Low"] = lows
    df["3M Momentum"] = momentum_3m_list
    df["Name"] = names
    df["Description"] = descriptions

    df["PE"] = pe_list
    df["Forward PE"] = forward_pe_list
    df["Revenue Growth"] = revenue_growth_list
    df["Earnings Growth"] = earnings_growth_list
    df["Profit Margin"] = profit_margin_list
    df["Market Cap"] = market_cap_list

    df["Volume"] = volume_list
    df["Avg Volume"] = avg_volume_list

    df = df.dropna(subset=["Preis", "52W High", "52W Low"]).copy()

    df["Trend Score"] = (df["Preis"] - df["52W Low"]) / (df["52W High"] - df["52W Low"])
    df["Momentum"] = (
        (df["Preis"] - ((df["52W High"] + df["52W Low"]) / 2)) /
        ((df["52W High"] - df["52W Low"]) / 2)
    )

    df["Trend Score"] = df["Trend Score"].round(2)
    df["Momentum"] = df["Momentum"].round(2)
    df["3M Momentum"] = df["3M Momentum"].round(2)

    trendrichtungen = []
    for _, row in df.iterrows():
        hist = load_price_history(row["Ticker"])
        trendrichtungen.append(get_trend_direction(hist, row["Preis"]))

    df["Trendrichtung"] = trendrichtungen
    df["Zone"] = df.apply(get_zone, axis=1)
    df["Fundamental Score"] = df.apply(get_fundamental_score, axis=1)
    df["Fundamental Quality"] = df["Fundamental Score"].apply(get_fundamental_quality)

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

    df["Structural Score"] = df.apply(structural_score, axis=1)
    df["Long Type"] = df.apply(long_type, axis=1)
    df["Long Warning"] = df.apply(long_warning, axis=1)

    df["Short Score"] = df.apply(short_score, axis=1)
    df["Long Score"] = df.apply(long_score, axis=1)
    df["Early Score"] = df.apply(early_score, axis=1)

    df["High Conviction"] = (
        (df["Early Score"] >= 12) &
        (df["Fundamental Quality"] == "Hoch") &
        (df["3M Momentum"] > 0)
    )

    df.to_csv(OUTPUT_FILE, index=False)

    ranked_df = (
        df.sort_values(
            by=["Long Score", "Short Score", "Entry Score", "Fundamental Score"],
            ascending=[False, False, False, False]
        )
        .drop_duplicates(subset=["Ticker"], keep="first")
    )

    short_df = (
        ranked_df.sort_values(
            by=["Short Score", "Entry Score", "3M Momentum", "Fundamental Score"],
            ascending=[False, False, False, False]
        )
        .head(8)
    )

    long_core_df = (
        ranked_df[
            ranked_df["Fundamental Quality"].isin(["Hoch", "Mittel"])
        ]
        .sort_values(
            by=["Fundamental Score", "Structural Score", "Long Score", "Entry Score"],
            ascending=[False, False, False, False]
        )
        .head(8)
    )

    long_entry_df = (
        ranked_df[
            ranked_df["Fundamental Quality"].isin(["Hoch", "Mittel"])
        ]
        .sort_values(
            by=["Long Score", "Entry Score", "Trend Score", "Fundamental Score"],
            ascending=[False, False, False, False]
        )
        .head(8)
    )

    has_volume_cols = {"Volume", "Avg Volume"}.issubset(ranked_df.columns)

    if has_volume_cols:
        early_mask = (
            (ranked_df["Trend Score"] < 0.65) &
            (ranked_df["Trend Score"] > 0.25) &
            (ranked_df["3M Momentum"] > 0.03) &
            (ranked_df["3M Momentum"] < 0.20) &
            (ranked_df["Trendrichtung"] == "Frischer Aufwaertstrend") &
            (ranked_df["Avg Volume"] > 0) &
            (ranked_df["Volume"] > 1.2 * ranked_df["Avg Volume"])
        )
    else:
        early_mask = pd.Series([False] * len(ranked_df), index=ranked_df.index)

    early_df = (
        ranked_df[early_mask]
        .sort_values(by=["Early Score", "Fundamental Score", "3M Momentum"], ascending=[False, False, False])
    )

    early_df = early_df[early_df["Early Score"] >= 12].head(8)

    append_signal_history(
        ranked_df,
        short_df,
        long_core_df,
        long_entry_df,
        early_df
    )

    with open("last_update.txt", "w") as f:
        f.write(datetime.now().strftime("%Y-%m-%d %H:%M"))

    print("Fertig: theme_scores.csv erstellt")
    print("Signal-Historie wurde aktualisiert.")


if __name__ == "__main__":
    main()
