import os
import pandas as pd
from datetime import datetime

INPUT_FILE = "theme_scores.csv"
OUTPUT_FILE = "signal_history.csv"


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


def get_status(score):
    if score > 0.7:
        return "Bullisch"
    elif score > 0.5:
        return "Neutral"
    else:
        return "Baerisch"


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

    if momentum_3m > 0.50:
        if pd.notna(momentum_1m) and momentum_1m < 0:
            return "Kippt"

        if pd.notna(momentum_20d) and momentum_20d < 0:
            return "Kippt"

        if price_above_ma50 is False:
            return "Kippt"

    if pd.notna(momentum_1m) and momentum_1m < -0.10:
        return "Fallend"

    if pd.notna(momentum_20d) and momentum_20d < -0.10:
        return "Fallend"

    if pd.notna(ma50_distance) and ma50_distance < -0.05:
        return "Fallend"

    if price_above_ma50 is False and pd.notna(momentum_1m) and momentum_1m < 0:
        return "Fallend"

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


def get_entry_score(row):
    score = 0

    if row["Zone"] == "Watchlist Zone":
        score += 3
    elif row["Zone"] == "Transition Zone":
        score += 2
    elif row["Zone"] == "Hold Zone":
        score += 1

    if row["Momentum"] > 0:
        score += 1
    elif row["Momentum"] < -0.20:
        score -= 1

    if row["3M Momentum"] > 0.10:
        score += 2
    elif row["3M Momentum"] > 0:
        score += 1
    elif row["3M Momentum"] < -0.10:
        score -= 2
    elif row["3M Momentum"] < 0:
        score -= 1

    if row["Fundamental Quality"] == "Hoch":
        score += 2
    elif row["Fundamental Quality"] == "Mittel":
        score += 1

    if pd.notna(row.get("Forward PE")):
        if 0 < row["Forward PE"] < 20:
            score += 1
        elif row["Forward PE"] > 60:
            score -= 1

    growth_positive = False

    if pd.notna(row.get("Revenue Growth")) and row["Revenue Growth"] > 0.05:
        growth_positive = True

    if pd.notna(row.get("Earnings Growth")) and row["Earnings Growth"] > 0.05:
        growth_positive = True

    if growth_positive:
        score += 1

    return max(0, min(score, 10))


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


def get_entry_quality(score):
    if score >= 8:
        return "Sehr gut"
    elif score >= 6:
        return "Gut"
    elif score >= 4:
        return "Neutral"
    else:
        return "Riskant"


def get_ranking_signal(row):
    if (
        row["Trend Score"] < 0.35
        and row["3M Momentum"] < 0
        and row["Theme Status"] == "Baerisch"
    ):
        return "Avoid"

    if row["Trend Score"] > 0.85 and row["3M Momentum"] < 0:
        return "Take Profits"

    if (
        0.55 <= row["Trend Score"] <= 0.85
        and row["Momentum"] > 0
        and row["3M Momentum"] > 0
        and row["Theme Status"] in ["Bullisch", "Neutral"]
        and row["Theme Bullisch %"] >= 50
        and row["Momentum Risiko"] == "Normal"
    ):
        return "Attraktiv"

    if row["Trend Score"] > 0.85 and row["3M Momentum"] > 0:
        return "Hold"

    if (
        row["Trend Score"] >= 0.50
        and row["Momentum"] >= -0.10
        and row["3M Momentum"] >= 0
        and row["Theme Status"] != "Baerisch"
    ):
        return "Hold"

    return "Review"


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
    elif row["Momentum"] < -0.20:
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

    if row["Fundamental Quality"] == "Hoch":
        score += 1

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


def long_score(row):
    score = 0

    score += row["Fundamental Score"] * 2
    score += row["Structural Score"] * 1.5

    if row["Fundamental Quality"] == "Hoch":
        score += 2
    elif row["Fundamental Quality"] == "Mittel":
        score += 1

    if row["Entry Score"] >= 8:
        score += 3
    elif row["Entry Score"] >= 6:
        score += 2
    elif row["Entry Score"] >= 4:
        score += 1

    if 0.45 <= row["Trend Score"] <= 0.80:
        score += 3
    elif 0.80 < row["Trend Score"] <= 0.90:
        score += 1
    elif row["Trend Score"] > 0.90:
        score -= 3

    if 0.08 <= row["3M Momentum"] <= 0.35:
        score += 2
    elif 0 < row["3M Momentum"] < 0.08:
        score += 1
    elif row["3M Momentum"] > 0.60:
        score -= 3
    elif row["3M Momentum"] < -0.10:
        score -= 2
    elif row["3M Momentum"] < 0:
        score -= 1

    if pd.notna(row.get("1M Momentum")):
        if row["1M Momentum"] < -0.05:
            score -= 3
        elif row["1M Momentum"] > 0.02:
            score += 1

    if pd.notna(row.get("20D Momentum")):
        if row["20D Momentum"] < -0.05:
            score -= 3
        elif row["20D Momentum"] > 0.02:
            score += 1

    if pd.notna(row.get("MA50 Abstand")):
        if row["MA50 Abstand"] < -0.03:
            score -= 3
        elif 0 <= row["MA50 Abstand"] <= 0.15:
            score += 1
        elif row["MA50 Abstand"] > 0.25:
            score -= 2

    if row["Momentum Risiko"] == "Ueberhitzt":
        score -= 3
    elif row["Momentum Risiko"] == "Extrem ueberhitzt":
        score -= 6
    elif row["Momentum Risiko"] in ["Fallend", "Kippt"]:
        score -= 6
    elif row["Momentum Risiko"] == "Unklar":
        score -= 1

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

    if row["Momentum Risiko"] != "Normal":
        score -= 8

    return score


def add_signal_rows(df, signal_type, score_col, top_n=8):
    rows = []

    signal_df = (
        df.sort_values(by=score_col, ascending=False)
        .drop_duplicates(subset=["Ticker"], keep="first")
        .head(top_n)
        .copy()
    )

    today = datetime.now().strftime("%Y-%m-%d")

    for rank, (_, row) in enumerate(signal_df.iterrows(), start=1):
        rows.append({
            "Date": today,
            "Signal Type": signal_type,
            "Rank": rank,
            "Ticker": row.get("Ticker"),
            "Name": row.get("Name"),
            "Preis": row.get("Preis"),
            "Trend Score": row.get("Trend Score"),
            "Momentum": row.get("Momentum"),
            "3M Momentum": row.get("3M Momentum"),
            "1M Momentum": row.get("1M Momentum"),
            "20D Momentum": row.get("20D Momentum"),
            "MA50 Abstand": row.get("MA50 Abstand"),
            "MA200 Abstand": row.get("MA200 Abstand"),
            "Volume": row.get("Volume"),
            "Avg Volume": row.get("Avg Volume"),
            "Volume Ratio": row.get("Volume Ratio"),
            "Momentum Risiko": row.get("Momentum Risiko"),
            "Zone": row.get("Zone"),
            "Entry Score": row.get("Entry Score"),
            "Entry Quality": row.get("Entry Quality"),
            "Fundamental Score": row.get("Fundamental Score"),
            "Fundamental Quality": row.get("Fundamental Quality"),
            "Short Score": row.get("Short Score"),
            "Long Score": row.get("Long Score"),
            "Early Score": row.get("Early Score"),
            "Signal Score": row.get(score_col),
            "Main Theme": row.get("Main Theme"),
            "Sub Theme": row.get("Sub Theme"),
            "Ranking Signal": row.get("Ranking Signal"),
            "High Conviction": row.get("High Conviction")
        })

    return rows


def main():
    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError("theme_scores.csv wurde nicht gefunden.")

    df = pd.read_csv(INPUT_FILE)

    required = [
        "Ticker",
        "Name",
        "Preis",
        "52W High",
        "52W Low",
        "Trend Score",
        "Momentum",
        "3M Momentum",
        "1M Momentum",
        "20D Momentum",
        "MA50 Abstand",
        "Preis ueber MA50",
        "Volume Ratio"
    ]

    for col in required:
        if col not in df.columns:
            raise ValueError(f"Spalte fehlt: {col}")

    numeric_cols = [
        "Preis",
        "52W High",
        "52W Low",
        "Trend Score",
        "Momentum",
        "3M Momentum",
        "1M Momentum",
        "20D Momentum",
        "MA50 Abstand",
        "MA200 Abstand",
        "Volume",
        "Avg Volume",
        "Volume Ratio",
        "Revenue Growth",
        "Earnings Growth",
        "Profit Margin",
        "Forward PE",
        "PE"
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(
        subset=[
            "Ticker",
            "Name",
            "Preis",
            "52W High",
            "52W Low",
            "Trend Score",
            "Momentum",
            "3M Momentum"
        ]
    ).copy()

    df["Zone"] = df.apply(get_zone, axis=1)

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

    df["Fundamental Score"] = df.apply(get_fundamental_score, axis=1)
    df["Fundamental Quality"] = df["Fundamental Score"].apply(get_fundamental_quality)

    df["Entry Score"] = df.apply(get_entry_score, axis=1)
    df["Entry Score"] = df.apply(apply_momentum_risk_to_entry, axis=1)
    df["Entry Quality"] = df["Entry Score"].apply(get_entry_quality)

    theme_summary = (
        df.groupby("Sub Theme", as_index=False)
        .agg({"Trend Score": "mean"})
    )

    theme_summary["Theme Status"] = theme_summary["Trend Score"].apply(get_status)

    theme_bullish = (
        df.assign(Status=df["Trend Score"].apply(get_status))
        .groupby("Sub Theme")["Status"]
        .apply(lambda x: round((x == "Bullisch").mean() * 100, 0))
        .reset_index(name="Theme Bullisch %")
    )

    theme_summary = theme_summary.merge(theme_bullish, on="Sub Theme", how="left")

    df = df.merge(
        theme_summary[["Sub Theme", "Theme Status", "Theme Bullisch %"]],
        on="Sub Theme",
        how="left"
    )

    df["Ranking Signal"] = df.apply(get_ranking_signal, axis=1)

    df["Structural Score"] = df.apply(structural_score, axis=1)
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

    safe_mask = (
        (df["Momentum Risiko"] == "Normal")
        & (df["1M Momentum"] > 0)
        & (df["20D Momentum"] > 0)
        & (df["MA50 Abstand"] > -0.03)
    )

    rows = []

    ranking_attraktiv_df = df[
        (df["Ranking Signal"] == "Attraktiv")
        & safe_mask
    ].copy()

    rows += add_signal_rows(
        ranking_attraktiv_df,
        "Ranking Attraktiv",
        "Entry Score",
        top_n=12
    )

    short_df = df[
        safe_mask
        & (df["Short Score"] > 0)
    ].copy()

    rows += add_signal_rows(
        short_df,
        "Short Term Top 8",
        "Short Score",
        top_n=8
    )

    long_entry_df = df[
        df["Fundamental Quality"].isin(["Hoch", "Mittel"])
        & safe_mask
        & (df["Long Score"] > 0)
    ].copy()

    rows += add_signal_rows(
        long_entry_df,
        "Long Term Entry Top 8",
        "Long Score",
        top_n=8
    )

    early_df = df[
        (df["Trend Score"] > 0.20)
        & (df["Trend Score"] < 0.78)
        & (df["3M Momentum"] > 0.02)
        & (df["3M Momentum"] < 0.40)
        & (df["1M Momentum"] > -0.04)
        & (df["20D Momentum"] > -0.04)
        & (df["Momentum Risiko"] == "Normal")
        & (df["MA50 Abstand"] > -0.06)
        & (df["MA50 Abstand"] < 0.22)
        & (df["Volume Ratio"] > 1.05)
        & (df["Early Score"] >= 8)
    ].copy()

    rows += add_signal_rows(
        early_df,
        "Early Play",
        "Early Score",
        top_n=8
    )

    high_conviction_df = early_df[
        early_df["High Conviction"] == True
    ].copy()

    rows += add_signal_rows(
        high_conviction_df,
        "High Conviction Early Play",
        "Early Score",
        top_n=8
    )

    today_df = pd.DataFrame(rows)

    if today_df.empty:
        print("Keine Signale fuer heute gefunden.")
        return

    today = datetime.now().strftime("%Y-%m-%d")

    if os.path.exists(OUTPUT_FILE):
        old_df = pd.read_csv(OUTPUT_FILE)

        if "Date" in old_df.columns:
            old_df = old_df[old_df["Date"] != today]

        final_df = pd.concat([old_df, today_df], ignore_index=True)
    else:
        final_df = today_df

    final_df = final_df.drop_duplicates(
        subset=["Date", "Signal Type", "Ticker"],
        keep="first"
    )

    final_df.to_csv(OUTPUT_FILE, index=False)

    print("Fertig: signal_history.csv aktualisiert")
    print(f"Gespeicherte Signale heute: {len(today_df)}")


if __name__ == "__main__":
    main()
