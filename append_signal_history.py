import os
import pandas as pd
from datetime import datetime

INPUT_FILE = "theme_scores.csv"
OUTPUT_FILE = "signal_history.csv"


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


def short_score(row):
    score = row["Entry Score"] * 1.5

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

    return score


def long_score(row):
    score = 0
    score += row["Fundamental Score"] * 2
    score += row["Trend Score"] * 2

    if row["Entry Score"] >= 8:
        score += 3
    elif row["Entry Score"] >= 6:
        score += 2
    elif row["Entry Score"] >= 4:
        score += 1

    if 0.08 <= row["3M Momentum"] <= 0.35:
        score += 2
    elif row["3M Momentum"] > 0.60:
        score -= 3
    elif row["3M Momentum"] < -0.10:
        score -= 2

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

    if row["Momentum"] > 0:
        score += 2

    return score


def add_signal_rows(df, signal_type, score_col, top_n=8):
    rows = []

    signal_df = (
        df.sort_values(by=score_col, ascending=False)
        .drop_duplicates(subset=["Ticker"], keep="first")
        .head(top_n)
        .copy()
    )

    for rank, (_, row) in enumerate(signal_df.iterrows(), start=1):
        rows.append({
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Signal Type": signal_type,
            "Rank": rank,
            "Ticker": row["Ticker"],
            "Name": row["Name"],
            "Entry Price": row["Preis"],
            "Trend Score": row["Trend Score"],
            "Range Momentum": row["Momentum"],
            "3M Momentum": row["3M Momentum"],
            "Entry Score": row["Entry Score"],
            "Entry Quality": row["Entry Quality"],
            "Fundamental Score": row["Fundamental Score"],
            "Fundamental Quality": row["Fundamental Quality"],
            "Signal Score": row[score_col],
        })

    return rows


def main():
    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError("theme_scores.csv wurde nicht gefunden.")

    df = pd.read_csv(INPUT_FILE)

    required = ["Ticker", "Name", "Preis", "52W High", "52W Low", "Trend Score", "Momentum", "3M Momentum"]

    for col in required:
        if col not in df.columns:
            raise ValueError(f"Spalte fehlt: {col}")

    df["Zone"] = df.apply(get_zone, axis=1)
    df["Fundamental Score"] = df.apply(get_fundamental_score, axis=1)
    df["Fundamental Quality"] = df["Fundamental Score"].apply(get_fundamental_quality)
    df["Entry Score"] = df.apply(get_entry_score, axis=1)
    df["Entry Quality"] = df["Entry Score"].apply(get_entry_quality)

    df["Short Score"] = df.apply(short_score, axis=1)
    df["Long Score"] = df.apply(long_score, axis=1)
    df["Early Score"] = df.apply(early_score, axis=1)

    rows = []
    rows += add_signal_rows(df, "Short Term", "Short Score", top_n=8)
    rows += add_signal_rows(df, "Long Term", "Long Score", top_n=8)
    rows += add_signal_rows(df, "Early Play", "Early Score", top_n=8)

    today_df = pd.DataFrame(rows)

    if os.path.exists(OUTPUT_FILE):
        old_df = pd.read_csv(OUTPUT_FILE)

        old_df = old_df[
            ~(
                (old_df["Date"] == datetime.now().strftime("%Y-%m-%d"))
            )
        ]

        final_df = pd.concat([old_df, today_df], ignore_index=True)
    else:
        final_df = today_df

    final_df.to_csv(OUTPUT_FILE, index=False)

    print("Fertig: signal_history.csv aktualisiert")


if __name__ == "__main__":
    main()
